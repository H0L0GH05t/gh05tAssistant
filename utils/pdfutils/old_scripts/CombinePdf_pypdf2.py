from PyPDF2 import PdfFileWriter, PdfFileReader#, PdfFileMerger
import os, sys
import logging, traceback
logger = logging.getLogger("pdf_merge.log")
handler = logging.FileHandler("pdf_merge.log")
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

print("\n\nHello!\n Welcome to the pdf_merge script!\n\
      You will be asked for a number of files, then each name seperately. \n\tPlease press the enter key after you answer each question!\n\n\
      Thank you for using PDF merger! \n\n")

try:
    num_of_files = input("How many pdf files would you like to combine? ")
    
    file_list = []
    for i in range(int(num_of_files)):
        filename = input("What is the full name of file %s? (ex: pdf_file.pdf)\n" % int(i+1))
        file_list.append(filename)
except Exception as ex:
    print("\tI'm sorry, but that input doesn't work!\n\tPlease try again, or check the error log")
    logger.warning(ex)
    exc_type, exc_value, exc_tb = sys.exc_info()
    logger.warning("Trace: %s"%traceback.format_tb(exc_tb))
    sys.exit()

logger.info("Merging %s files\n"%(num_of_files))
logger.info(file_list)

in_streams = []
output = PdfFileWriter()
out_stream = open('merged_pdfs.pdf','wb')
try:
    for file in file_list:
        print("Merging %s..." % file)
        in_file = PdfFileReader(open(file,'rb'))
        for page_num in range(in_file.numPages):
            logger.info("Adding page %s from %s...\n" % (int(page_num+1), file))
            output.addPage(in_file.getPage(page_num))
            in_streams.append(in_file)
    
    output.write(out_stream)
    out_stream.close()
    for in_stream in in_streams:
        in_stream.stream.close()
    print("Finished successfully!")
    handler.close()
    os.remove('pdf_merge.log')
except Exception as e:
    print("There was a problem while merging your files. Please check the error log!")
    logger.info("Please email this log to the creator at aki.akai.ame@gmail.com")
    logger.error(e)
    exc_type, exc_value, exc_tb = sys.exc_info()
    logger.error("Trace: %s"%traceback.format_tb(exc_tb))
    sys.exit()
    
print("\n\nEnd of program!\n\n")