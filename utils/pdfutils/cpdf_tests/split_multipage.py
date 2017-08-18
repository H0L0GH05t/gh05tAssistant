import io, sys, os
import subprocess

# input_path = "edition.pdf"
input_path = "Schoeler_40 Seiten Eigenwerbung.pdf"
output_path = 'split_output'
link_page = "link_page.pdf"

get_pages_cmd = 'cpdf -pages "%s" ' % input_path
process = subprocess.Popen(get_pages_cmd, shell=True, stdout=subprocess.PIPE, )
output, unused_err = process.communicate()

number_of_pages = int(output.decode('utf-8'))

if number_of_pages > 0:

    split_path = input_path.replace('.pdf', '__split_pages')
    output_path = os.path.join(output_path, split_path)
    if not os.path.exists(output_path): os.makedirs(output_path, 0o777)

    for page in range(number_of_pages):
        try:
            # page_and_ext = '__page_' + str(page + 1) + '.pdf'
            # new_file_name = input_path.replace('.pdf', page_and_ext)
            page_and_ext = input_path[-7:]
            if page + 1 > 9: zeros = '0'
            else: zeros = '00'
            new_file_name = input_path.replace(page_and_ext, zeros + str(page + 1) + '.pdf')
            print("Splitting page: %s" % new_file_name)
            split_cmd = 'cpdf "%s" %s -o "%s"' % (input_path, str(page + 1), os.path.join(output_path, new_file_name))
            output = subprocess.check_call(split_cmd, shell=True, stdout=subprocess.PIPE, )
            if output:
                print("Subprocess output: %s" % output)
        except Exception as e:
            try:
                import traceback
                print('Unable to split PDF pages, exception: %s ' % (traceback.format_exc()))
            except Exception:
                print('Unable to split PDF pages, exception: %s' % e)

print("\n\nEND")