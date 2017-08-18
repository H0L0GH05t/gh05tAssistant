import io, sys, os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch, cm
from reportlab.lib import colors

import subprocess

input_path = "test_1.pdf"
output_path = 'edition.pdf'
out3 = 'stamp_under_2.pdf'
link_page = "link_page.pdf"

# input_path = "20170311brunsmt8kollektiv-14.pdf"
# input_path = "20170311.BRUNS.MT.8.KOLLEKTIV-14.pdf"
# input_path = "20170311.BRUNS.MT.1.MINDEN.pdf"
# input_path = "deflate.pdf"

# link_page = "20170311brunsmt8kollektiv-14-link_page.pdf"

merge_only = False


if merge_only:
    try:
        ## Apply the same mediabox to the link_page pdf, then crop to trimbox or cropbox
        # if len(mediabox) > 0:
        #     # set mediabox
        #     crop_pdf_cmd = 'cpdf -mediabox "%s %s %s %s" %s -o %s' % (mediabox[0], mediabox[1], mediabox[2], mediabox[3], temp_path, temp_path)
        #     output = subprocess.check_call(crop_pdf_cmd, shell=True, stdout=subprocess.PIPE, )
        #     if output:
        #         logger.warning("Applied mediabox to link_page -- output: %s" % output)
        #         output = None  # reset output for next subprocess call
        # if len(cropbox) > 0:
        #     # apply crop to page
        #     crop_pdf_cmd = 'cpdf -crop "%s %s %s %s" %s -o %s' % (cropbox[0], cropbox[1],
        #                                                           str(float(cropbox[2]) - float(cropbox[0])),
        #                                                           str(float(cropbox[3]) - float(cropbox[1])), temp_path, temp_path)
        #     output = subprocess.check_call(crop_pdf_cmd, shell=True, stdout=subprocess.PIPE, )
        #     if output:
        #         logger.warning("Applied crop to link_page -- output: %s" % output)
        #         output = None  # reset output for next subprocess call
        # elif len(trimbox) > 0:
        #     # crop to trimbox
        #     crop_pdf_cmd = 'cpdf -crop "%s %s %s %s" %s -o %s' % (trimbox[0], trimbox[1],
        #                                                           str(float(trimbox[2]) - float(trimbox[0])),
        #                                                           str(float(trimbox[3]) - float(trimbox[1])), temp_path, temp_path)
        #     output = subprocess.check_call(crop_pdf_cmd, shell=True, stdout=subprocess.PIPE, )
        #     if output:
        #         logger.warning("Applied trimbox to link_page -- output: %s" % output)
        #         output = None  # reset output for next subprocess call

        print("Copy Annots...")
        # Copy any annotations from the original PDF to the link page
        copy_annots_cmd = "cpdf -copy-annotations %s %s 1 -o %s" % (input_path, link_page, link_page)
        process = subprocess.Popen(copy_annots_cmd, shell=True, stdout=subprocess.PIPE, )
        output, err = process.communicate()
        if err:
            print('ERROR ---\n%s' % err)
        if output:
            print('OUTPUT ---\n%s' % output)

        err = ''
        output = ''

        # -scale-stamp-to-fit
        # preprocess the stamp with -shift first
        # -pos-center "200 200" <-- position center of baseline at 200pt, 200pt
        # -pos-left "200 200" <-- left of baseline at 200,200
        # -pos-right "200 200"
        # -top 10 <-- center of baseline 10pts down from top center
        # -topleft 10 <-- down and in from top left
        # -left, -bottomleft, -bottom, -bottomright, -right
        # -diagonal <-- diagonal, bottom left to top right, centered on page
        # reverse-diagonal <-- diagonal, top left to bottom right, centered on page
        # -center <-- centered on page
        # -relative-to-cropbox
        print("\nStart merge...")

        # merge the link page on top of the original PDF
        stamp_under2_cmd = "cpdf -stamp-under %s %s -o %s" % (link_page, input_path, out3)

        process = subprocess.Popen(stamp_under2_cmd, shell=True, stdout=subprocess.PIPE, )
        output, err = process.communicate()
        if err:
            print('ERROR ---\n%s' % err)
        if output:
            print('OUTPUT ---\n%s' % output)
        print("\nStamp under (with linkpage as base) finished...")
        err = ''
        output = ''


    except Exception as e:
        exc_type, exc_value, exc_tb = sys.exc_info()
        line = exc_tb.tb_lineno
        print("Line %s : %s" % (line, e))

else:
    get_pages_cmd = "cpdf -pages %s " % input_path
    process = subprocess.Popen(get_pages_cmd, shell=True, stdout=subprocess.PIPE, )
    output, unused_err = process.communicate()

    number_of_pages = int(output.decode('utf-8'))

    if number_of_pages > 0:

        get_page_info = "cpdf -page-info %s " % input_path
        process = subprocess.Popen(get_page_info, shell=True, stdout=subprocess.PIPE, )
        output, unused_err = process.communicate()
        page_info = output.decode('utf-8')
        page_info_line = page_info.split('\n')
        for line in page_info_line:
            if "MediaBox" in line:
                mediabox = line.replace('MediaBox: ','').split()

        size = {'width': float(mediabox[2]),
                'height': float(mediabox[3])}
        margin = {'left': 0,
                    'top': 0,
                    'right': 0,
                    'bottom': 0}
        scale_factor = 10.0

        #create a new PDF with Reportlab
        # import tempfile
        # temp_dir = tempfile.gettempdir()
        # temp_path = os.path.join(temp_dir, "tmp.pdf")
        can = canvas.Canvas(link_page, pagesize=(size['width'], size['height']))

        region_left = scale_factor * 10
        region_bottom = scale_factor * 30
        region_right = scale_factor * 50
        region_top = scale_factor * 80

        x1 = float(region_left + margin['left'])
        # y1 = float(size['height'])/2
        y1 = float(region_top - size['height']) / 2
        x2 = float(region_right + margin['left'])
        y2 = float(size['height'])

        width = float(region_right - region_left)
        height = float(region_bottom - region_top)

        r1 = (x1, y1, x2, y2)
        url = "http://google.com"
        can.linkURL(url, r1, thickness=1, color=colors.green, relative=1)
        can.setStrokeColorRGB(1,0,1)
        can.setFillColorRGB(1,0,1)
        can.rect(x1, y1, width, height, stroke=1, fill=1)
        can.drawString(x1+3, y2+2, 'TEST')

        can.showPage()
        can.save()

        try:
            ## Apply the same mediabox to the link_page pdf, then crop to trimbox or cropbox
            # if len(mediabox) > 0:
            #     # set mediabox
            #     crop_pdf_cmd = 'cpdf -mediabox "%s %s %s %s" %s -o %s' % (mediabox[0], mediabox[1], mediabox[2], mediabox[3], link_page, link_page)
            #     output = subprocess.check_call(crop_pdf_cmd, shell=True, stdout=subprocess.PIPE, )
            #     if output:
            #         print("Applied mediabox to link_page -- output: %s" % output)
            #         output = None  # reset output for next subprocess call
            # if len(cropbox) > 0:
            #     # apply crop to page
            #     crop_pdf_cmd = 'cpdf -crop "%s %s %s %s" %s -o %s' % (cropbox[0], cropbox[1],
            #                                                           str(float(cropbox[2]) - float(cropbox[0])),
            #                                                           str(float(cropbox[3]) - float(cropbox[1])), link_page, link_page)
            #     output = subprocess.check_call(crop_pdf_cmd, shell=True, stdout=subprocess.PIPE, )
            #     if output:
            #         print("Applied crop to link_page -- output: %s" % output)
            #         output = None  # reset output for next subprocess call
            # elif len(trimbox) > 0:
            #     # crop to trimbox
            #     crop_pdf_cmd = 'cpdf -crop "%s %s %s %s" %s -o %s' % (trimbox[0], trimbox[1],
            #                                                           str(float(trimbox[2]) - float(trimbox[0])),
            #                                                           str(float(trimbox[3]) - float(trimbox[1])), link_page, link_page)
            #     output = subprocess.check_call(crop_pdf_cmd, shell=True, stdout=subprocess.PIPE, )
            #     if output:
            #         print("Applied trimbox to link_page -- output: %s" % output)
            #         output = None  # reset output for next subprocess call

            # Copy any annotations from the original PDF to the link page to ensure we copy links from the original page
            copy_annots_cmd = "cpdf -fast -copy-annotations %s %s 1 -o %s" % (input_path, link_page, link_page)
            process = subprocess.Popen(copy_annots_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, err = process.communicate()
            if err:
                print("Error copying annotations for debug link page: %s" % err)
                err = ''
            if output:
                print(output)
                output = ''
            # Copy any annotations from the link page to the original PDF
            copy_annots_cmd = "cpdf -fast -copy-annotations %s %s 1 -o %s" % (link_page, input_path, link_page)
            process = subprocess.Popen(copy_annots_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, err = process.communicate()
            if err:
                print("Error adding click region to PDF: %s" % err)
                path = original_path
            else:
                path = link_page
            if output:
                print(output)

            print(path)


        except Exception as e:
            exc_type, exc_value, exc_tb = sys.exc_info()
            line = exc_tb.tb_lineno
            print("Line %s : %s"%(line,e))

    else:
        print("\t\t!! Error: Number of pages in pdf is 0!")

    #if link_page != None:
    #    print("LINK PAGE!")

print("Finished")
