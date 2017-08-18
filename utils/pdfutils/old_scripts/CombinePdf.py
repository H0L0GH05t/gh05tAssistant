# from PyPDF2 import PdfFileWriter, PdfFileReader#, PdfFileMerger
import os, sys
import logging, traceback
import subprocess
logger = logging.getLogger("pdf_merge.log")
handler = logging.FileHandler("pdf_merge.log")
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

print("\n\nHello!\n Welcome to the pdf_merge script!\n\
      If not using a preset file, you will be asked for a number of files, then each name separately. \n\tPlease press the enter key after you answer each question!\n\n Thank you for using PDF merger! \n\n")

def get_file_list:
    try:
        # Get output path from user. If this is left blank, the default 'merged_pdfs.pdf' will be used instead.
        output_filename = input("What would you like to name the merged file? (Full path is also accepted)\n")
        use_preset = input("Do you have a preset instructions file? y/n\t")
        if use_preset.lower()[0] == 'y':
            # Read file to find files names to merge
            preset_file = input("What is the name of the preset instructions file?\n")

        #Manually accept input for file info
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

# in_streams = []
# output = PdfFileWriter()
# out_stream = open('merged_pdfs.pdf','wb')

# def validate_path:
    # Check if file exists

output_path = 'merged_pdfs.pdf'
# Validate and correct user input path
try:
    if os.path.exists(output_path):
        overwrite_prev = input("\tThere is already a file with the name provided. Overwrite? y/n")
        if overwrite_prev.lower()[0] == 'y':
            try:
                os.remove(overwrite_prev)
            except Exception:
                print("\tError deleting existing file.\n")
                logger.error(traceback.format_exc())

except Exception as ex:
    print("\tThere was an error with the provided output path.\n\tWe will name the output 'merged_pdfs.pdf' by default and place it in the current directory.\n")
    logger.warning(ex)
    exc_type, exc_value, exc_tb = sys.exc_info()
    logger.warning("Trace: %s" % traceback.format_tb(exc_tb))

def run_merge(file_list):
    try:
        # OLD PyPDF2 version
        # for file in file_list:
        #     print("Merging %s..." % file)
        #     in_file = PdfFileReader(open(file,'rb'))
        #     for page_num in range(in_file.numPages):
        #         logger.info("Adding page %s from %s...\n" % (int(page_num+1), file))
        #         output.addPage(in_file.getPage(page_num))
        #         in_streams.append(in_file)
        #
        # output.write(out_stream)
        # out_stream.close()
        # for in_stream in in_streams:
        #     in_stream.stream.close()
        # print("Finished successfully!")
        # handler.close()
        # os.remove('pdf_merge.log')

        if len(file_list) > 0:
            # file_list has "'page_path', '1'" for each page, where 1 is specifying the 1st page of the pdf
            if len(file_list) > 100:
                # When there are over 50 pages, we need to break up the merge command into many smaller groups
                page_set_idx = 0
                increment = int(len(file_list) / 10)
                if not increment % 2 == 0:
                    increment = increment + 1
                while page_set_idx < len(file_list):
                    page_set = file_list[page_set_idx:page_set_idx + increment]
                    if (page_set_idx + increment) > len(file_list):
                        page_set_idx = page_set_idx + (len(file_list) - page_set_idx)
                    else:
                        page_set_idx += increment

                    if os.path.exists(output_path):
                        merge_pg_cmd = ['cpdf', '-merge', output_path] + page_set + ['-o', output_path]
                    else:
                        merge_pg_cmd = ['cpdf', '-merge'] + page_set + ['-o', output_path]
                    cmd_result = subprocess.check_output(merge_pg_cmd, shell=True)
                    if cmd_result:
                        logger.error(cmd_result)
            elif len(file_list) > 20:
                # If there is more than 10 pages, split up the merge command into a few smaller groups
                page_set_idx = 0
                increment = int(len(file_list) / 4)
                if not increment % 2 == 0:
                    increment = increment + 1
                while page_set_idx < len(file_list):
                    page_set = file_list[page_set_idx:page_set_idx + increment]
                    if (page_set_idx + increment) > len(file_list):
                        page_set_idx = page_set_idx + (len(file_list) - page_set_idx)
                    else:
                        page_set_idx += increment

                    if os.path.exists(output_path):
                        merge_pg_cmd = ['cpdf', '-merge', output_path] + page_set + ['-o', output_path]
                    else:
                        merge_pg_cmd = ['cpdf', '-merge'] + page_set + ['-o', output_path]
                    cmd_result = subprocess.check_output(merge_pg_cmd, shell=True)
                    if cmd_result:
                        logger.error(cmd_result)
            else:
                merge_pg_cmd = ['cpdf', '-merge'] + file_list + ['-o', output_path]
                # merge_cmd = "cpdf -merge %s -o %s" % (output_pages, output_path)
                cmd_result = subprocess.check_output(merge_pg_cmd, shell=True)
                if cmd_result:
                    logger.error(cmd_result)
        else:
            logger.error("No pages to merge!")

        # If the merged_pdfs.pdf doesn't exist, make sure an error gets displayed in the ui
        if not os.path.exists(output_path):
            print("Failed to save merged file")
            logger.error("Failed to save merged file: output path does not exist")
        else:
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

#----------------------

def main(argv):
    try:
        options, remainder = getopt.gnu_getopt(sys.argv[1:],'i:o:p:x:n:e:f:h',["ifile=","ofile=", "pfile=", "xslt=", "pubname=", "encoding=","function=","help="])
    except getopt.GetoptError as e:
        print('Error getting args. Use -h or --help to see help.\nError: %s' % e)
        sys.exit(2)
    try:
        for opt, arg in options:

            if opt in ("-h", "--help"):
                print('\n\nThere are 3 ways to use this script. It can be run by itself and prompt for info, with commandline args, or with a presets file.\n'
                      'Without Presets**: python test_xml.py -i <inputfile> -o <outputfile> -x <xsltfile> -pub <publicationname> -e <xmlencoding>\n'
                      'With Presets**: python test_xml.py (optional: -i <inputfile> -o <outputfile>) -pf <presetsfile>\n'
                      'Without Args*: test_xml.py\n\n'
                      'Options (None are mandatory):\n'
                      '-i, --ifile    - Path to the input folder containing PDFS\n'
                      '-o, --ofile    - Path for the ouput file\n'
                      '-x, --xslt     - Path to the XSLT to be used\n'
                      '-t2, --use2     - Boolean used to turn 2nd XSLT on(for Eversify Output Mode only)\n'
                      '-x2, --xslt2    - Path to the 2nd XSLT to be used\n'
                      '-n, --pubname  - Publication Name\n'
                      '-e, --encoding - Encoding of XML files\n'
                      '-p, --pfile    - Path to presets file (use either this or the above)\n'
                      '-f, --function - Select what to do with the xml ("info" for class output, "transform" for Everisify output)\n'
                      '* Note: If no args, user will be prompted.\n'
                      '** If there is any missing info from either the presets file or the args list, the user will be prompted to provide it. \n\n')
                sys.exit()
            elif opt in ("-i", "--ifile"):
                xml_folder_path = normalize(arg, False)
            elif opt in ("-x", "--xslt"):
                xslt_path = normalize(arg, False)
            elif opt in ("-u2", "--use2"):
                if arg.lower() == 'true' or arg.lower() == 't' or \
                                arg.lower() == 'yes'  or arg.lower() == 'y':
                    use_xslt2 = True
            elif opt in ("-x2", "--xslt2"):
                xslt2_path = normalize(arg, False)
            elif opt in ("-n", "--pubname"):
                pub_name = arg
            elif opt in ("-e", "--encoding"):
                encoding = arg
            elif opt in ("-p", "--pfile"):
                presets_path = arg
            elif opt in ("-o", "--ofile"):
                output_path = normalize(arg, True)
            elif opt in ("-f", "--function"):
                funct = arg

    except Exception as e:
        print("Error loading presets: %s" % e)

    print("\n\npresets_path: %s\noutput_path: %s\nxml_folder_path: %s\nuse_xslt2: %s\nxslt_path: %s\nxslt2_path: %s\npub_name: %s\nencoding: %s\nfunction: %s\n\n" % (presets_path, output_path, xml_folder_path, use_xslt2, xslt_path, xslt_path, pub_name, encoding, funct))
    if funct == 'transform':
        create_eversify_output(presets_path, output_path, xml_folder_path, use_xslt2, xslt_path, xslt2_path, pub_name, encoding)
    else:
        get_xml_info(presets_path, output_path, xml_folder_path, xslt_path, pub_name, encoding)

if __name__ == "__main__":
    main(sys.argv[1:])

print("\n\nEnd of program!\n\n")
sys.exit()