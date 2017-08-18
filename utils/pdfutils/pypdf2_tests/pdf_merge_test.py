import io, sys, os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch, cm
from reportlab.lib import colors

from PyPDF2 import PdfFileWriter, PdfFileReader
from PyPDF2.pdf import PageObject
from PyPDF2.utils import b_

import subprocess

input_path = "Schoeler_40 Seiten Eigenwerb013.pdf"
output_path = 'result.pdf'
# link_page = "link_page.pdf"

get_pages_cmd = 'pdftk "%s" dump_data_utf8 ' % input_path
process = subprocess.Popen(get_pages_cmd, shell=True, stdout=subprocess.PIPE, )
output, err = process.communicate()
if err:
    print(err)
page_info = output.decode('utf-8')
page_info_line = page_info.split('\n')
number_of_pages = 0
trimbox = []
cropbox = []
mediabox = []
for line in page_info_line:
    if not isinstance(line, int):
        if line.lower().startswith('numberofpages'):
            number_of_pages = int(line.split(':')[1])
        if line.startswith("PageMediaTrimRect"):
            trimbox = line.replace('PageMediaTrimRect: ', '').split()
        if line.startswith("PageMediaCropRect"):
            cropbox = line.replace('PageMediaCropRect: ', '').split()
        if line.startswith("PageMediaRect"):
            mediabox = line.replace('PageMediaRect: ', '').split()

print("Boxes > mediabox: %s -- cropbox: %s -- trimbox: %s\n\n" % (mediabox, cropbox, trimbox))####

if number_of_pages > 0:
    size = {'width': float(mediabox[2]), 
            'height': float(mediabox[3])}
    margin = {'left': 0, 
                'top': 0,
                'right': 0,
                'bottom': 0}
    scale_factor = 10.0

    link_page = None

    #create a new PDF with Reportlab
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(size['width'], size['height']))
    import tempfile
    # temp_dir = tempfile.gettempdir()
    # temp_path = os.path.join(temp_dir, "tmp.pdf")
    # temp_path = "link_page.pdf"####
    # can = canvas.Canvas(temp_path, pagesize=(size['width'], size['height']))

    region_left = scale_factor * 10
    region_bottom = scale_factor * 10
    region_right = scale_factor * 80
    region_top = scale_factor * 0

    x1 = float(region_left + margin['left'])
    y1 = float(size['height'])/2
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
    packet.seek(0)

    new_pdf = PdfFileReader(packet)
    # openpdf.close()
    print('Sucessfully generated links for %s' % os.path.basename(input_path))
    link_page = new_pdf.getPage(0)
    input_stream = new_pdf.stream


    try:
        if input_stream != None and link_page != None:
            # if pdf_library_available:
            output = PdfFileWriter()
            input_streams = []
            input_pdf = PdfFileReader(open(input_path, "rb"), strict=False)
            input_page = input_pdf.getPage(0)
            input_streams.append(input_pdf.stream)
            input_streams.append(input_stream)
            input_page.mergePage(link_page)
            output.addPage(input_page)
            output_path = input_path.replace('.pdf', '-links.pdf')
            output_stream = open(output_path, "wb")
            output.write(output_stream)
            output_stream.close()
            for input_stream in input_streams:
                input_stream.close()
            # os.remove(input_path)
            # if not os.path.exists(input_path):
            #     os.rename(output_path, input_path)
            # else:
            #     print('Could not replace %s with the link generated version' % input_path)
            # else:
            #     print(u'auto_link_generator failed: Pdf library not available')


    except Exception as e:
        exc_type, exc_value, exc_tb = sys.exc_info()
        line = exc_tb.tb_lineno
        print("Line %s : %s"%(line,e))
    #
    #if link_page != None:
    #    print("LINK PAGE!")

print("Finished")
