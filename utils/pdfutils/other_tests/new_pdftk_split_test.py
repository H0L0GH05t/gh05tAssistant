import os, sys, traceback
import re, datetime
import subprocess
import tempfile
import shutil
import zipfile

from django.utils.encoding import smart_text

import io, sys, os
import subprocess

# input_path = "edition.pdf"
input_path = "Weidwerk_05-2015_1.pdf"
output_path = 'split_output'
number_of_pages = 0

get_pages_cmd = 'pdftk "%s" dump_data_utf8 ' % input_path
# get_pages_cmd = 'pdftk "%s" dump_data ' % input_path
process = subprocess.Popen(get_pages_cmd, shell=True, stdout=subprocess.PIPE, )
output, unused_err = process.communicate()
output_test = output.decode('utf-8').split('\n')
got_page_count = False
for line in output_test:
    if not isinstance(line, int) and line.lower().startswith('numberofpages'):
        number_of_pages = int(line.split(':')[1])
        got_page_count = True
        print("Pdf has %s pages." % number_of_pages)
if not got_page_count:
    print("The NumberOfPages in dump_data could not be found in pdf %s. It will process only the first page." % input_path)
    number_of_pages = 1

# number_of_pages = int(output.decode('utf-8'))

if number_of_pages > 0:

    split_path = input_path.replace('.pdf', '__split_pages')
    output_path = os.path.join(output_path, split_path)
    if not os.path.exists(output_path): os.makedirs(output_path, 0o777)

    out_pattern = os.path.join(output_path, 'page_%02d.pdf')
    try:
        split_cmd = 'pdftk "%s" burst output "%s"' % (input_path , out_pattern)
        output = subprocess.check_call(split_cmd, shell=True, stdout=subprocess.PIPE, )
        if output:
            print("Subprocess output: %s" % output)
    except:
        try:
            import traceback
            print('Unable to split PDF pages, exception: %s ' % (traceback.format_exc()))
        except Exception:
            print('Unable to split PDF pages, exception: %s' % e)

    # for page in range(number_of_pages):
    #     try:
    #         # page_and_ext = '__page_' + str(page + 1) + '.pdf'
    #         # new_file_name = input_path.replace('.pdf', page_and_ext)
    #         page_and_ext = input_path[-7:]
    #         if page + 1 > 9: zeros = '0'
    #         else: zeros = '00'
    #         new_file_name = input_path.replace(page_and_ext, zeros + str(page + 1) + '.pdf')
    #         print("Splitting page: %s" % new_file_name)
    #         split_cmd = 'cpdf "%s" %s -o "%s"' % (input_path, str(page + 1), os.path.join(output_path, new_file_name))
    #         output = subprocess.check_call(split_cmd, shell=True, stdout=subprocess.PIPE, )
    #         if output:
    #             print("Subprocess output: %s" % output)
    #     except Exception as e:
    #         try:
    #             import traceback
    #             print('Unable to split PDF pages, exception: %s ' % (traceback.format_exc()))
    #         except Exception:
    #             print('Unable to split PDF pages, exception: %s' % e)

print("\n\nEND")