import io, sys, os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
    
from pdfrw import PdfReader, PdfWriter
from pdfrw.buildxobj import pagexobj

import subprocess

input_path = "zen_merge_test.pdf"
output_path = 'edition.pdf'
link_page = "link_page.pdf"

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

link_page = None

#create a new PDF with Reportlab
#packet = io.BytesIO()
#can = canvas.Canvas(packet, pagesize=(size['width'], size['height']))
import tempfile
temp_dir = tempfile.gettempdir()
temp_path = os.path.join(temp_dir, "tmp.pdf")
can = canvas.Canvas(temp_path, pagesize=(size['width'], size['height']))

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
#packet.seek(0)

try:
    stamp_cmd = "cpdf -stamp-under %s %s -o %s" % (input_path, temp_path, output_path)
    process = subprocess.Popen(stamp_cmd, shell=True, stdout=subprocess.PIPE, )
    output, err = process.communicate()
    if err:
        print(err)
        
    copy_annots_cmd = "cpdf -copy-annotations %s %s 1 -o %s" % (input_path, output_path, output_path)
    process = subprocess.Popen(stamp_cmd, shell=True, stdout=subprocess.PIPE, )
    output, err = process.communicate()
    if err:
        print(err)
        
    
except Exception as e:
    exc_type, exc_value, exc_tb = sys.exc_info()
    line = exc_tb.tb_lineno
    print("Line %s : %s"%(line,e))
#
#if link_page != None:
#    print("LINK PAGE!")

print("Finished")
