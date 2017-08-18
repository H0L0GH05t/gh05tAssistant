import os, sys
import io, re
import tempfile, shutil
import subprocess

pdf_library_available = False
try:
    from pdfrw import (PdfReader, PdfWriter, PdfDict, PdfName, IndirectPdfDict, PdfArray)
    from pdfrw.buildxobj import pagexobj
    pdf_library_available = True
except Exception:
    print("Can't find pdfrw")
    
pdfminer_available = False
try:
    from pdfminer.pdfparser import PDFParser, PDFDocument
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.pdfdevice import PDFDevice
    from pdfminer.converter import  TextConverter, PDFPageAggregator
    from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTChar
    pdfminer_available = True
except Exception:
    print("Can't find pdfminer")
    
report_lab_available = False
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch, cm
    from reportlab.lib import colors
    report_lab_available = True
except Exception:
    print("Can't find reportlab")

#######################################################################
auto_generate_links = True ####
pdf_file = "auto_link-tester_doc-01.pdf"####
#pdf_file = "2014-07-10COT04.pdf"

class auto_links_tester():

    def auto_link_generator(pdf_path, debug_article_links):
        if not pdfminer_available:
            print('auto_link_generator failed: Pdfminer library not available')####
            return
        try:
            print("starting link generation...")####
            #re patterns
            TRAILING_PUNCTUATION = ['.', ',', ':', ';', '.)', '"', '\'']
            word_split_re = re.compile(r'(\s+)')
            simple_url_re = re.compile(r'^https?://\[?\w', re.IGNORECASE)
            simple_url_2_re = re.compile(r'(^www\.|^(?!http))\w[^@]+\.(com|edu|gov|int|mil|net|org|ch|de|at|be|uk|fr|es|nl|ly|pl|hu)($|/.*)$', re.IGNORECASE)
            simple_email_re = re.compile(r'^\S+@\S+\.\S+$')
            
            #Set up parser and document
            openpdf = open(pdf_path, 'rb')
            parser = PDFParser(openpdf)
            document = PDFDocument()
            parser.set_document(document)
            document.set_parser(parser)
            document.initialize('')
            print("setup document and parser\n")####
            
            #Create a PDF resource manager object that stores shared resources
            rsrcmgr = PDFResourceManager()
            # Set parameters for analysis.
            laparams = LAParams()
            
            #Create PDF device interpreter objects
            device = PDFPageAggregator(rsrcmgr, laparams=laparams)
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            print("setup resource manager, params, device, interpreter...\n")####
            
            #Process each page
            for page in document.get_pages():
                interpreter.process_page(page)
                print("processing page\n")####
                
                #check for existing link objects
                uri_objs = []
                if page.annots:
                    print("Found page annots\n")####
                    obj = page.annots
                    if not isinstance(obj, list):
                        obj = obj.resolve()
                    if isinstance(obj, list):
                        for v in obj:
                            objref = v.resolve()
                            if objref['Subtype'] == '/Link':
                                if is_numeric(objref['A']):
                                    uri_obj = objref['A'].resolve()
                                    uri_objs.append(uri_obj['URI'])
                                else:
                                    uri_objs.append(uri_obj['URI'])
    
                #set canvas for drawing new links
                page_width = page.mediabox[2]
                page_height = page.mediabox[3]
                packet = io.BytesIO()
                can = canvas.Canvas(packet, pagesize=(page_width, page_height))
                print("set canvas\n")####
    
                layout = device.get_result()
                print("got device, starting link generation\n")####
                generated_links = False
                
                for lt_obj in layout:
                    #find the link text
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
                                        #Check for short url
                                        if simple_url_re.match(middle):
                                            url = middle
                                        
                                        #Check for long url
                                        elif simple_url_2_re.match(middle):
                                                url = 'http://%s' % middle
                                        
                                        #check for email
                                        elif ':' not in middle and simple_email_re.match(middle):
                                            local, domain = middle.rsplit('@', 1)
                                            try:
                                                domain = domain.encode('idna').decode('ascii')
                                            except UnicodeError:
                                                continue
                                            url = 'mailto:%s@%s' % (local, domain)
                                            
                                        #check for phone number
                                        #TODO
                                        
                                        #if link already exists, skip it
                                        if uri_objs:
                                            for uri in uri_objs:
                                                if url == uri:
                                                    url = None
                                                    #logger.info('Existing link match for %s' % uri)
                                        
                                        if url: 
                                            #find the LTChar objects for the first and last char of the link
                                            first_match = None
                                            last_match = None
                                            match = False
                                            i = 0
                                            for lt_char_obj in lt_text_obj:
                                                if i > len(word)-1:
                                                    break
                                                if lt_char_obj.get_text() == word[i]:
                                                    if i == 0: first_match = lt_char_obj
                                                    if i == len(word)-1: last_match = lt_char_obj
                                                    match = True
                                                    i += 1
                                                else:
                                                    match = False
                                                    i = 0
                                            if first_match and last_match:
                                                #get the coordinates to draw the link box
                                                x0 = first_match.bbox[0]
                                                y0 = first_match.bbox[1]
                                                x1 = last_match.bbox[2]
                                                y1 = last_match.bbox[3]
                                                
                                                r1 = (x0, y0, x1, y1)
                                                can.linkURL(url, r1, thickness=1, color=colors.green)
                                                generated_links = True
                                                if debug_article_links:
                                                    width = x1-x0
                                                    height = y0-y1
                                                    can.setStrokeColorRGB(1,0,1)
                                                    can.setFillColorRGB(1,0,1)
                                                    can.rect(x0, y1, width, height, stroke=1, fill=0)
                                            else:
                                                #match failed on LTChar so use the coordinates of the LTTextLine
                                                try:
                                                    x0 = lt_text_obj.bbox[0]
                                                    x1 = lt_text_obj.bbox[2]
                                                    y0 = lt_text_obj.bbox[1]
                                                    y1 = lt_text_obj.bbox[3]
                                                
                                                    r1 = (x0, y0, x1, y1)
                                                    can.linkURL(url, r1, thickness=1, color=colors.green)
                                                    
                                                    if debug_article_links:
                                                        width = x1-x0
                                                        height = y0-y1
                                                        can.setStrokeColorRGB(1,0,1)
                                                        can.setFillColorRGB(1,0,1)
                                                        can.rect(x0, y1, width, height, stroke=1, fill=0)
                                                except Exception as e:
                                                    print('Could not make link box for %s' % url)####
                                            
            if generated_links:
                can.showPage()
                can.save()
                packet.seek(0)
                try:
                    new_pdf = PdfFileReader(packet)
                    openpdf.close()
                    print('Sucessfully generated links for %s' % os.path.basename(pdf_path))####
                    return new_pdf.getPage(0), new_pdf.stream
                except Exception as e:
                    openpdf.close()
                    print('Could not generate links for %s: %s' % (os.path.basename(pdf_path),e))####
                    return None, None
            else:
                openpdf.close()
                print('No links found for %s' % os.path.basename(pdf_path))####
                return None, None
        except Exception as e:
            print('Could not generate links for %s: %s' % (os.path.basename(pdf_path),e))####
            import traceback
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_tb(exc_tb)
            return None, None

#########################################################################

    if auto_generate_links:
        if pdfminer_available and report_lab_available:
            debug_article_links = True #Override for debug links ####
            link_page = None
            input_stream = None
            print("Link creation libraries found, debug links is set to %s" % debug_article_links)####
            link_page, input_stream = auto_link_generator(pdf_file, debug_article_links)####
            if input_stream != None and link_page != None:
                if pdf_library_available:
                    output = PdfFileWriter()
                    input_streams = []
                    input = PdfFileReader(open(pdf_file, "rb"), strict=False)####
                    input_page = input.getPage(0)
                    input_streams.append(input.stream)
                    input_streams.append(input_stream)
                    input_page.mergePage(link_page)
                    output.addPage(input_page)
                    output_path = pdf_file.replace('.pdf','-links.pdf')####
                    output_stream = open(output_path, "wb")
                    output.write(output_stream)
                    output_stream.close()
                    for input_stream in input_streams:
                        input_stream.close()
                    #os.remove(pdf_file)####
                    #if not os.path.exists(pdf_file):####
                    #    os.rename(output_path, pdf_file)####
                    #else:
                    #    print('Could not replace %s with the link generated version' % pdf_file)####
                else:
                    print('auto_link_generator failed: Pdf library not available')####
        else:
            print('auto_link_generator failed: Pdfminer library or Report Lab not available')####

print("\n\nEND----------------")