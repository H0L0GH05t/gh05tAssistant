import io, os, sys, errno, re
import tempfile
import codecs
import shutil
from io import StringIO, BytesIO

name_list_path = "rename_list.txt"
template_img = "template.jpg"

if os.path.exists(name_list_path) and os.path.exists(template_img):
    try:
        with open(name_list_path, 'r') as name_list_file:
            name_list = name_list_file.read()
            for img_name in name_list.split(','):
                if os.path.exists(img_name):
                    print("duplicate image: %s" % img_name)
                else:
                    shutil.copy2(template_img, img_name)
                    print("Created placeholder image for: %s" % img_name)

    except Exception as e:
        print("Exception renaming images: %s" % e)
else:
    print("Missing rename_list.txt or template.jpg")
print("End")
sys.exit()