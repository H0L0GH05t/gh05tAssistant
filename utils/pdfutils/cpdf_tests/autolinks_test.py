import io, sys, os
import re
import tempfile, shutil
import subprocess

pdfminer_available = False
try:
    from pdfminer.pdfparser import PDFParser, PDFDocument
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.pdfdevice import PDFDevice
    from pdfminer.converter import  TextConverter, PDFPageAggregator
    from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTChar
    pdfminer_available = True
except Exception:
    print('pdfminer not available')

report_lab_available = False
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch, cm
    from reportlab.lib import colors
    report_lab_available = True
except Exception:
    print('reportlab not available')

pdf_path = "test_1.pdf"
#pdf_path = "merge_test.pdf"

def url_finder(pdf_path, debug_article_links, cropbox, trimbox):
    if not pdfminer_available:
        print('url_finder failed: Pdfminer library not available')
        return
    try:
        # re patterns
        TRAILING_PUNCTUATION = ['.', ',', ':', ';', '.)', '"', '\'']
        domain_list = r'com|edu|gov|int|mil|net|org|ch|de|at|be|uk|fr|es|nl|ly|pl|hu|br|ar|cl|ec|pe|uy|co|ve|bo|sr|gy|tt|pa|ng|ca'
        simple_url_2_compile = r'(^www\.|^(?!http))\w[^@]+\.(' + domain_list + r')($|/.*)$'
        word_split_re = re.compile(r'(\s+)')
        simple_url_re = re.compile(r'^https?://\[?\w', re.IGNORECASE)
        simple_url_2_re = re.compile(simple_url_2_compile, re.IGNORECASE)
        simple_email_re = re.compile(r'^\S+@\S+\.\S+$')

        # Set up parser and document
        openpdf = open(pdf_path, 'rb')
        parser = PDFParser(openpdf)
        document = PDFDocument()

        # Set parser to document and initialize
        parser.set_document(document)
        document.set_parser(parser)
        document.initialize('')

        # Create a PDF resource manager object that stores shared resources
        rsrcmgr = PDFResourceManager()
        # set parameters for analysis
        laparams = LAParams()

        # Create PDF device interpreter objects
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        # Process each page
        for page in document.get_pages():
            interpreter.process_page(page)

            # check for existing link objects
            uri_objs = []
            if page.annots:
                obj = page.annots
                if not isinstance(obj, list):
                    obj = obj.resolve()
                if isinstance(obj, list):
                    for v in obj:
                        objref = v.resolve()
                        if str(objref['Subtype']) == '/Link' and 'A' in objref:
                            if type((objref['A'])) == dict:
                                uri_objs.append(objref['A']['URI'])
                            else:
                                uri_obj = objref['A'].resolve()
                                if 'URI' in uri_obj:
                                    uri_objs.append(uri_obj['URI'])

            # set canvas for drawing new links
            if cropbox:
                page_width = float(cropbox[2]) - float(cropbox[0])
                page_height = float(cropbox[3]) - float(cropbox[1])
            elif trimbox:
                page_width = float(trimbox[2]) - float(trimbox[0])
                page_height = float(trimbox[3]) - float(trimbox[1])
            else:
                page_width = page.mediabox[2] - page.mediabox[0]
                page_height = page.mediabox[3] - page.mediabox[1]

            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, "auto_link_page.pdf")
            can = canvas.Canvas(temp_path, pagesize=(page_width, page_height))

            layout = device.get_result()
            generated_links = False

            for lt_obj in layout:
                # find the link text
                if isinstance(lt_obj, LTTextBox):
                    for lt_text_obj in lt_obj:
                        if isinstance(lt_text_obj, LTTextLine):
                            words = word_split_re.split(lt_text_obj.get_text())
                            for i, word in enumerate(words):
                                if '.' in word or '@' in word or ':' in word:
                                    # Deal with punctuation.
                                    lead, middle, trail = '', word, ''
                                    for punctuation in TRAILING_PUNCTUATION:
                                        if middle.endswith(punctuation):
                                            middle = middle[:-len(punctuation)]
                                            trail = punctuation + trail

                                    url = None
                                    # Check for short url
                                    if simple_url_re.match(middle):
                                        url = middle

                                    # Check for long url
                                    elif simple_url_2_re.match(middle):
                                        url = 'http://%s' % middle

                                    # check for email
                                    elif ':' not in middle and simple_email_re.match(middle):
                                        local, domain = middle.rsplit('@', 1)
                                        try:
                                            domain = domain.encode('idna').decode('ascii')
                                        except UnicodeError:
                                            continue
                                        url = 'mailto:%s@%s' % (local, domain)

                                    # check for phone number
                                    # TODO: phone number regex

                                    # if link already exists, skip it
                                    if uri_objs:
                                        for uri in uri_objs:
                                            if url == uri:
                                                url = None
                                                print('Existing link match for %s' % uri)

                                    if url:
                                        # find the LTChar objects for the first and last char of the link
                                        first_match = None
                                        last_match = None
                                        match = False
                                        i = 0
                                        for lt_char_obj in lt_text_obj:
                                            if i > len(word) - 1:
                                                break
                                            if lt_char_obj.get_text() == word[i]:
                                                if i == 0: first_match = lt_char_obj
                                                if i == len(word) - 1: last_match = lt_char_obj
                                                match = True
                                                i += 1
                                            else:
                                                match = False
                                                i = 0
                                        if first_match and last_match:
                                            # get extra margins to add if there's a cropbox
                                            extra_margin_bottom = 0
                                            extra_margin_left = 0
                                            # if cropbox: #this is no longer necessary
                                            #     # extra_margin_bottom = float(cropbox[2]) - float(page.mediabox[2])
                                            #     extra_margin_bottom = float(cropbox[0])
                                            #     # extra_margin_left = float(cropbox[3]) - float(page.mediabox[3])
                                            #     extra_margin_left = float(cropbox[1])
                                            # get the coordinates to draw the link box
                                            x0 = float(first_match.bbox[0] + extra_margin_bottom)
                                            y0 = float(first_match.bbox[1] + extra_margin_left)
                                            x1 = float(last_match.bbox[2] + extra_margin_bottom)
                                            y1 = float(last_match.bbox[3] + extra_margin_left)

                                            r1 = (x0, y0, x1, y1)
                                            can.linkURL(url, r1, thickness=1, color=colors.green)
                                            generated_links = True
                                            if debug_article_links:
                                                width = x1 - x0
                                                height = y0 - y1
                                                can.setStrokeColorRGB(154, 0, 255)
                                                can.setFillColorRGB(154, 0, 255)
                                                can.rect(x0, y1, width, height, stroke=1, fill=0)
                                                can.drawString(x0 + 3, y1 + 2, 'URL')
                                        else:
                                            # match failed on LTChar so use the coordinates of the LTTextLine
                                            try:
                                                x0 = lt_text_obj.bbox[0]
                                                x1 = lt_text_obj.bbox[2]
                                                y0 = lt_text_obj.bbox[1]
                                                y1 = lt_text_obj.bbox[3]

                                                r1 = (x0, y0, x1, y1)
                                                can.linkURL(url, r1, thickness=1, color=colors.green)

                                                if debug_article_links:
                                                    width = x1 - x0
                                                    height = y0 - y1
                                                    can.setStrokeColorRGB(154, 0, 255)
                                                    can.setFillColorRGB(154, 0, 255)
                                                    can.rect(x0, y1, width, height, stroke=1, fill=0)
                                                    can.drawString(x0 + 3, y1 + 2, 'URL')
                                            except Exception as e:
                                                print("Could not make link box for '%s': %s" % (url, e))

        if generated_links:
            can.showPage()
            can.save()
            print('Sucessfully generated links for %s' % os.path.basename(pdf_path))
            return temp_path
        else:
            print('No links found for %s' % os.path.basename(pdf_path))
            return None
    except Exception as e:
        import traceback
        print('Error reading pdf for automatic link generation: %s -- %s' % (e, traceback.format_exc()))
        return None

########################################################

auto_generate_links = True
debug_article_links = True #Override for debug links

if auto_generate_links:
    if pdfminer_available and report_lab_available:

        # get cropbox info from original page
        get_page_info = 'cpdf -page-info "%s" ' % pdf_path
        process = subprocess.Popen(get_page_info, shell=True, stdout=subprocess.PIPE, )
        output, err = process.communicate()
        if err:
            print(err)
        page_info = output.decode('utf-8')
        page_info_line = page_info.split('\n')
        trimbox = []
        cropbox = []
        mediabox = []
        for line in page_info_line:
            if "TrimBox" in line:
                trimbox = line.replace('TrimBox: ', '').split()
            if "CropBox" in line:
                cropbox = line.replace('CropBox: ', '').split()
            if "MediaBox" in line:
                mediabox = line.replace('MediaBox: ', '').split()

        link_page = None
        link_page = url_finder(pdf_path, debug_article_links, cropbox, trimbox)
        if link_page != None:
            ## Apply the same mediabox to the link_page pdf, then crop to trimbox or cropbox
            # shutil.copy(link_page, "autolinks_results/link_page.pdf")####
            # input("Created link page!\nHit enter to continue...\n\n")####

            if len(mediabox) > 0:
                # set mediabox
                crop_pdf_cmd = 'cpdf -mediabox "%s %s %s %s" "%s" -o "%s' % (mediabox[0], mediabox[1], mediabox[2], mediabox[3], link_page, link_page)
                output = subprocess.check_call(crop_pdf_cmd, shell=True, stdout=subprocess.PIPE, )
                if output:
                    print("Applied mediabox to link_page -- output: %s" % output)
                    output = ''  # reset output for next subprocess call

                # shutil.copy(link_page, "autolinks_results/link_page__applied_mediabox.pdf")####
                # input("Applied mediabox\nHit enter to continue...\n\n")  ####

            if len(cropbox) > 0:
                # apply crop to page
                crop_pdf_cmd = 'cpdf -crop "%s %s %s %s" "%s" -o "%s"' % (cropbox[0], cropbox[1],
                                                                          str(float(cropbox[2]) - float(cropbox[0])),
                                                                          str(float(cropbox[3]) - float(cropbox[1])), link_page, link_page)
                output = subprocess.check_call(crop_pdf_cmd, shell=True, stdout=subprocess.PIPE, )
                if output:
                    print("Applied crop to link_page -- output: %s" % output)
                    output = ''  # reset output for next subprocess

                # shutil.copy(link_page, "autolinks_results/link_page__applied_cropbox.pdf")####
                # input("Applied cropbox\nHit enter to continue...\n\n")  ####

            elif len(trimbox) > 0:
                # crop to trimbox
                crop_pdf_cmd = 'cpdf -crop "%s %s %s %s" "%s" -o "%s"' % (trimbox[0], trimbox[1],
                                                                          str(float(trimbox[2]) - float(trimbox[0])),
                                                                          str(float(trimbox[3]) - float(trimbox[1])), link_page, link_page)
                output = subprocess.check_call(crop_pdf_cmd, shell=True, stdout=subprocess.PIPE, )
                if output:
                    print("Applied trimbox to link_page -- output: %s" % output)
                    output = ''  # reset output for next subprocess call

                # shutil.copy(link_page, "autolinks_results/link_page__applied_trimbox.pdf")####
                # input("Applied trimbox\nHit enter to continue...\n\n")  ####

            if debug_article_links:
                print("debug_article_links is on, so we will use the merge page method for link pages on: %s" % pdf_path)
                # Copy any annotations from the original PDF to the link page
                copy_annots_cmd = 'cpdf -fast -copy-annotations "%s" "%s" 1 -o "%s"' % (pdf_path, link_page, link_page)
                process = subprocess.Popen(copy_annots_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output, err = process.communicate()
                if err:
                    print("Error copying annotations for debug link page: %s" % err)
                    err = ''
                if output:
                    print(output)
                    output = ''

                shutil.copy(link_page, "autolinks_results/link_page__copied_annots_debug.pdf")####
                input("Copied annots (debug method)\nHit enter to continue...\n\n")  ####

                # merge the link page on top of the original PDF
                stamp_cmd = 'cpdf -fast -stamp-under "%s" "%s" -o "%s"' % (pdf_path, link_page, "autolinks_results/stamped_under_final.pdf")
                process = subprocess.Popen(stamp_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output, err = process.communicate()
                if err:
                    print("Error adding debug boxes for click region to PDF: %s" % err)
                    # Copy any annotations from the link page to the original PDF
                    copy_annots_cmd = 'cpdf -fast -copy-annotations "%s" "%s" 1 -o "%s"' % (link_page, pdf_path, "autolinks_results/err__copy_annots_final.pdf")
                    process = subprocess.Popen(copy_annots_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    output, err = process.communicate()
                    if err:
                        print("Error adding click region to PDF: %s" % err)
                    if output:
                        print(output)
                if output:
                    print(output)
            else:
                # Copy any annotations from the original PDF to the link page to ensure we copy links from the original page
                copy_annots_cmd = 'cpdf -fast -copy-annotations "%s" "%s" 1 -o "%s"' % (pdf_path, link_page, link_page)
                process = subprocess.Popen(copy_annots_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output, err = process.communicate()
                if err:
                    print("Error copying annotations for debug link page: %s" % err)
                    err = ''
                if output:
                    print(output)
                    output = ''

                shutil.copy(link_page, "autolinks_results/link_page__copied_annots.pdf")  ####
                input("Copied annots\nHit enter to continue...\n\n")  ####

                # Copy any annotations from the link page to the original PDF
                copy_annots_cmd = 'cpdf -fast -copy-annotations "%s" "%s" 1 -o "%s"' % (link_page, pdf_path, "autolinks_results/copy_annots_final.pdf")
                process = subprocess.Popen(copy_annots_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output, err = process.communicate()
                if err:
                    print("Error adding click region to PDF: %s" % err)
                if output:
                    print(output)

            #### OLD ####
            # stamp_cmd = "cpdf -stamp-under %s %s -o %s" % (pdf_path, link_page, link_page)
            # #stamp_cmd = "cpdf -stamp-under %s %s -o %s" % (pdf_path, link_page, "stamped_link_page.pdf")
            # process = subprocess.Popen(stamp_cmd, shell=True, stdout=subprocess.PIPE, )
            # output, err = process.communicate()
            # if err:
            #     print(err)
            #
            # #copy_annots_cmd = "cpdf -copy-annotations %s %s 1 -o %s" % (pdf_path, link_page, pdf_path)
            # copy_annots_cmd = "cpdf -copy-annotations %s %s 1 -o %s" % (pdf_path, link_page, "finished_merge.pdf")
            # process = subprocess.Popen(copy_annots_cmd, shell=True, stdout=subprocess.PIPE, )
            # output, err = process.communicate()
            # if err:
            #     print(err)
            #######
    else:
        print('url_finder failed: Pdfminer library or Report Lab not available')

#######################################################

print("END")
