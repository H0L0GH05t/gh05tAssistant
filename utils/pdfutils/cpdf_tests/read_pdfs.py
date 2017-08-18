import subprocess
import io, sys, os

input_path = "test_path"

failed_pages = []

for pdf in os.listdir(input_path):
    print("Testing pdf: %s" % pdf)
    path = os.path.join(input_path, pdf)

    try:
        get_page_info = "cpdf -page-info %s " % path
        process = subprocess.Popen(get_page_info, shell=True, stdout=subprocess.PIPE, )
        output, unused_err = process.communicate()
        page_info = output.decode('utf-8')
        page_info_line = page_info.split('\n')
        trimbox = []
        mediabox = []
        cropbox = []
        for line in page_info_line:
            if "MediaBox" in line:
                mediabox = line.replace('MediaBox: ','').split()
            if "TrimBox" in line:
                trimbox = line.replace('TrimBox: ','').split()
            if "CropBox" in line:
                cropbox = line.replace('CropBox: ','').split()
        print("Found boxes > mediabox: %s -- trimbox: %s -- cropbox: %s\n" % (mediabox, trimbox, cropbox))
    except Exception as e:
        print("Failed to get page info with utf-8 decode: %s" % e)
        try:
            page_info = str(output)
            page_info_line = page_info.split('\\n')
            trimbox = []
            mediabox = []
            cropbox = []
            for line in page_info_line:
                print(line)
                if "MediaBox" in line:
                    mediabox = line.replace('MediaBox: ', '').split()
                if "TrimBox" in line:
                    trimbox = line.replace('TrimBox: ', '').split()
                if "CropBox" in line:
                    cropbox = line.replace('CropBox: ', '').split()
            print("\nFound boxes > mediabox: %s -- trimbox: %s -- cropbox: %s\n" % (mediabox, trimbox, cropbox))
        except Exception as e:
            import traceback
            print("Failed to get page info for page '%s': %s\n\n%s" % (pdf, e, traceback.format_exc()))
            failed_pages.append(pdf)
            try:
                print(output)
            except Exception as e:
                print("Can't print output\n\n")
print("\n\nFailed PDFs:\n")
for page in failed_pages:
    print(page)