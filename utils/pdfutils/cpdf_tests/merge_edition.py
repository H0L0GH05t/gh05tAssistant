import io, sys, os
import subprocess

input_path = "gplus 17_01.pdf"
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

    for index, pdf in enumerate(pdfs):
        # original_path = path
        # try:
        #     if link_page:
        #         ## Apply the same mediabox to the link_page pdf, then crop to trimbox or cropbox
        #         if len(mediabox) > 0:
        #             # set mediabox
        #             crop_pdf_cmd = 'cpdf -mediabox "%s %s %s %s" %s -o %s' % (mediabox[0], mediabox[1], mediabox[2], mediabox[3], link_page, link_page)
        #             output = subprocess.check_call(crop_pdf_cmd, shell=True, stdout=subprocess.PIPE, )
        #             if output:
        #                 print("Applied mediabox to link_page -- output: %s" % output)
        #                 output = None  # reset output for next subprocess call
        #         if len(cropbox) > 0:
        #             # apply crop to page
        #             crop_pdf_cmd = 'cpdf -crop "%s %s %s %s" %s -o %s' % (cropbox[0], cropbox[1],
        #                                                                   str(float(cropbox[2]) - float(cropbox[0])),
        #                                                                   str(float(cropbox[3]) - float(cropbox[1])), link_page, link_page)
        #             output = subprocess.check_call(crop_pdf_cmd, shell=True, stdout=subprocess.PIPE, )
        #             if output:
        #                 print("Applied crop to link_page -- output: %s" % output)
        #                 output = None  # reset output for next subprocess call
        #         elif len(trimbox) > 0:
        #             # crop to trimbox
        #             crop_pdf_cmd = 'cpdf -crop "%s %s %s %s" %s -o %s' % (trimbox[0], trimbox[1],
        #                                                                   str(float(trimbox[2]) - float(trimbox[0])),
        #                                                                   str(float(trimbox[3]) - float(trimbox[1])), link_page, link_page)
        #             output = subprocess.check_call(crop_pdf_cmd, shell=True, stdout=subprocess.PIPE, )
        #             if output:
        #                 print("Applied trimbox to link_page -- output: %s" % output)
        #                 output = None  # reset output for next subprocess call
        #
        #         # Copy any annotations from the original PDF to the link page
        #         copy_annots_cmd = "cpdf -copy-annotations %s %s 1 -o %s" % (path, link_page, link_page)
        #         process = subprocess.Popen(copy_annots_cmd, shell=True, stdout=subprocess.PIPE, )
        #         output, err = process.communicate()
        #         if err:
        #             print(err)
        #         if output:
        #             print(output)  ####
        #
        #         # merge the link page on top of the original PDF
        #         stamp_cmd = "cpdf -stamp-under %s %s -o %s" % (path, link_page, link_page)
        #         process = subprocess.Popen(stamp_cmd, shell=True, stdout=subprocess.PIPE, )
        #         output, err = process.communicate()
        #         if err:
        #             print(err)
        #         if output:
        #             print(output)  ####
        #         path = link_page
        #         link_page_paths.append(link_page)
        # except Exception as e:
        #     message = 'Failed to merge_pdf_files for: %s, Exception: %s' % (self.input_issue.title, e)
        #     print(message)
        #     self.error_messages.append(message)
        #     self.event_logger.log_error_event(message)
        #     path = original_path
        # # add first page to output path list
        # if os.path.exists(path):
        #     # TODO: Validate PDF file here before adding it to the merge path
        #     output_page_list.append(path)  # pdf path
        #     output_page_list.append('1')  # which page of pdf to merge
        #     # output_pages += path + ' 1 '
        # else:
        #     print"PDF does not exist, failed to merge '%s'" % path)

        if len(output_page_list) > 0:
            # output_page_list has "'page_path', '1'" for each page, where 1 is specifying the 1st page of the pdf
            if len(output_page_list) > 100:
                # When there are over 50 pages, we need to break up the merge command into many smaller groups
                page_set_idx = 0
                increment = int(len(output_page_list) / 10)
                if not increment % 2 == 0:
                    increment = increment + 1
                while page_set_idx < len(output_page_list):
                    page_set = output_page_list[page_set_idx:page_set_idx + increment]
                    if (page_set_idx + increment) > len(output_page_list):
                        page_set_idx = page_set_idx + (len(output_page_list) - page_set_idx)
                    else:
                        page_set_idx += increment

                    if os.path.exists(output_path):
                        merge_pg_cmd = ['cpdf', '-merge', output_path] + page_set + ['-o', output_path]
                    else:
                        merge_pg_cmd = ['cpdf', '-merge'] + page_set + ['-o', output_path]
                    cmd_result = subprocess.check_output(merge_pg_cmd, shell=True)
                    if cmd_result:
                        print(cmd_result)
            elif len(output_page_list) > 20:
                # If there is more than 10 pages, split up the merge command into a few smaller groups
                page_set_idx = 0
                increment = int(len(output_page_list) / 4)
                if not increment % 2 == 0:
                    increment = increment + 1
                while page_set_idx < len(output_page_list):
                    page_set = output_page_list[page_set_idx:page_set_idx + increment]
                    if (page_set_idx + increment) > len(output_page_list):
                        page_set_idx = page_set_idx + (len(output_page_list) - page_set_idx)
                    else:
                        page_set_idx += increment

                    if os.path.exists(output_path):
                        merge_pg_cmd = ['cpdf', '-merge', output_path] + page_set + ['-o', output_path]
                    else:
                        merge_pg_cmd = ['cpdf', '-merge'] + page_set + ['-o', output_path]
                    cmd_result = subprocess.check_output(merge_pg_cmd, shell=True)
                    if cmd_result:
                        print(cmd_result)
            else:
                merge_pg_cmd = ['cpdf', '-merge'] + output_page_list + ['-o', output_path]
                # merge_cmd = "cpdf -merge %s -o %s" % (output_pages, output_path)
                cmd_result = subprocess.check_output(merge_pg_cmd, shell=True)
                if cmd_result:
                    print(cmd_result)
        else:
            print("No output pages to merge!")

        try:
            page_and_ext = '__page_' + str(page + 1) + '.pdf'
            new_file_name = input_path.replace('.pdf', page_and_ext)
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