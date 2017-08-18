import io, os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
import subprocess

            
if os.getenv('PDFTK_PATH'):
    PDFTK_PATH = os.getenv('PDFTK_PATH')
else:
    PDFTK_PATH = 'pdftk'

path = "zen_merge_test.pdf"
output_path = 'edition.pdf'
input_streams = []

def run_command(command, shell=False):
    ''' run a system command and yield output '''
    p = check_output(command, shell=shell)
    return p.split('\n')

def get_num_pages(pdf_path):
    ''' return number of pages in a given PDF file '''
    for line in run_command([PDFTK_PATH, pdf_path, 'dump_data']):
        if line.lower().startswith('numberofpages'):
            return int(line.split(':')[1])
    return 0

def merge_pages(link_page, pdf_path, out_path):
    ''' merges the link page on top of the pdf page '''
    #copy original files, return original if fail
    #pdftk forground.pdf background background.pdf output merged.pdf
    cmd = [PDFTK_PATH, link_page, 'background', pdf_path, 'output', out_path]
    run_command(cmd)

number_of_pages = get_num_pages(path)

if number_of_pages > 0:
    #input_page = input.getPage(0) # Only support one page per pdf for now
    
    ##crop the pdf to the trimbox first                    
    #input_page.cropBox.upperLeft  = input_page.trimBox.upperLeft
    #input_page.cropBox.upperRight = input_page.trimBox.upperRight
    #input_page.cropBox.lowerLeft  = input_page.trimBox.lowerLeft
    #input_page.cropBox.lowerRight = input_page.trimBox.lowerRight
    
    #then make the size for the link_page the size of the input_page
    size = {'width': float(input_page.mediaBox.getWidth()), 
            'height': float(input_page.mediaBox.getHeight())}
    margin = {'left': 0, 
                'top': 0,
                'right': 0,
                'bottom': 0}
    scale_factor = 10.0

link_page = None
input_stream = None
output = PdfWriter()
output2 = PdfWriter()

packet = io.BytesIO()
#create a new PDF with Reportlab
can = canvas.Canvas(packet, pagesize=(size['width'], size['height']))
#import tempfile
#temp_dir = tempfile.gettempdir()
#temp_path = os.path.join(temp_dir, "tmp.pdf")
#can = canvas.Canvas(temp_path, pagesize=(size['width'], size['height']))
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

try:
    new_pdf = PdfReader(packet)
    #new_pdf = PdfFileReader(temp_path)
    input_stream = new_pdf.stream
    link_page = new_pdf.getPage(0)
    output2.addPage(link_page)
    output_stream2 = open("link_page.pdf", "wb")
    output2.write(output_stream2)
    output_stream2.close()
    print("Made link pdf?")
except Exception as e:
    print(e)

if input_stream != None:
    input_streams.append(input_stream)
if link_page != None:
    print("LINK PAGE!")
    input_page.mergePage(link_page)
    
    output.addPage(input_page)
    
    output_stream = open(output_path, "wb")
    output.write(output_stream)
    output_stream.close()
        
    print("Done making new pdf!")
for input_stream in input_streams:
        input_stream.close()
print("Finished")