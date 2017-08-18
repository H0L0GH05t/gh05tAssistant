input_path = 'c:/cms_software/reader/data/jcc-bruns-betriebs-gmbh/41298\edition.pdf'
original_file_name = 'MT-PDF_man'
GS64_PATH = 'C:\\Program Files\\gs\\gs9.15\\bin'

import sys, os

#normalize media_file path
input_path = input_path.replace('\\', '/')

#Get pdf version
with open(input_path, 'rb') as f:
  pdf_version = f.readline()
  pdf_version = pdf_version.replace('%PDF-','')
pdf_version = pdf_version[:3] #removes extra chars at the end
if pdf_version == "1.3":
    pdf_version = 1.4

#copy files to local temp
import tempfile, shutil
temp_dir = tempfile.gettempdir()
temp_path = tempfile.mktemp()
shutil.copy2(input_path, temp_path)
#logger.debug(temp_path)

#get the correct gs command based on operating system
if sys.platform == "win32":
    sys_op = os.path.join(GS64_PATH, 'gswin64c')
    sys_op = '"' + sys_op + '"'
    sys_op = sys_op.replace('/', '\\')
else:
    sys_op = 'gs '

extension = '.pdf'
if ".pdf" in input_path: extension = '.pdf'
elif ".PDF" in input_path: extension = '.PDF'
output_path = input_path.replace(extension, '-resaved.pdf')


#Ghostscript command
resave_cmd = '%s \
-q \
-dNOPAUSE \
-dBATCH \
-sDEVICE=pdfwrite \
-dCompatibilityLevel=%s \
-sOutputFile="%s"  \
-f "%s"' % (sys_op, pdf_version, output_path, temp_path)
print('\n')
print(resave_cmd)####
print('\n')
try:
    import subprocess
    proc = subprocess.check_call(resave_cmd)
    #cmd_output, cmd_err = proc.communicate()
    
    if not os.path.exists(output_path):
        print('Resave Failed on %s: Ghostscript did not run sucessfully' % original_file_name)
        #if cmd_err: print(cmd_err)
        #elif cmd_output: print(cmd_output)
        #else: print('Resave Failed on %s: Ghostscript did not run sucessfully' % original_file_name)
    #elif cmd_output:
    #    print('>>> STDOUT: %s' % cmd_output)
    #elif cmd_err:
    #    message = 'Resave Failed with an error from Ghostscript: %s' % cmd_err
    #    print('>>> STDERR: %s' % cmd_err)
    #else:
        #replace the original media_file with the successfully downsampled file
        #message = 'Successfully resaved %s' % original_file_name
        #os.remove(input_path)
        #if not os.path.exists(input_path):
        #    os.rename(output_path, input_path)
        #else:
        #    message = 'Could not replace %s with the resaved file' % original_file_name
    #remove temp file
    else:
      print('Success?')
    os.remove(temp_path)
except Exception, e:
    print(e)