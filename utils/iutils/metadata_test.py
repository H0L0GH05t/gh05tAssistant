import exiftool
import sys, os

legal_image_exts = ['.jpg', '.jpeg', '.png', '.gif']
legal_image_extensions = ['jpg', 'jpeg', 'png', 'gif']

num_of_imgs = 0
image_list = []
path_name = ''

use_folder = input("Will you use a folder path? (y/n) ")
if use_folder.lower() == 'y':
    path_name = input("Enter path for the image folder: ")
    if os.path.exists(path_name):
        for root, dirs, files in os.walk(path_name):
            for name in files:
                image_filename = os.path.basename(name)
                image_basename, image_file_extension = os.path.splitext(image_filename)
                if image_file_extension in legal_image_exts:
                    print("Found image: %s" % os.path.join(root, name))
                    image_list.append(os.path.join(root, name))
    else:
        print("Path does not exist.")
        sys.exit()
else:
    num_of_imgs = input("How many images do you want to test? ")
    for i in range(int(num_of_imgs)):
        path_name = input("Enter file name for image %s: " % str(i+1))
        image_list.append(path_name)

output_name = 'exiftool_output-%s.txt' % path_name

if os.path.exists(output_name):
    print("Previous results will be overwritten!")
    os.remove(output_name)

output = open(output_name, 'w')

for path_name in image_list:
    output.write("Image Name: " + path_name + "\n\n")
    with exiftool.ExifTool() as et:
        metadata = et.get_metadata(path_name)
    for d in metadata:
        
        #Print out formatted as "Filename     Artist EXIF info      Image Description EXIF info"
        #output.write("{:20.20} {:20.20} {:20.20}\n".format(d["SourceFile"],d["EXIF:Artist"],d["EXIF:ImageDescription"]))
        
        value = metadata[d]
        if not isinstance(value, str): value = str(value)
        
        #Print out all EXIF data formatted
        output.write("{:40.40} {:500.500}\n".format(d,value))
        
        #Print out specific EXIF data:
        #if d == "XMP:Creator":
        #    output.write(d + " - " + value + "\n")
        #if d == "XMP:Title":
        #    output.write(d + " - " + value + "\n")
        #if d == "EXIF:Artist":
        #    output.write(d + " - " + value + "\n")
        #if d == "EXIF:XPTitle":
        #    output.write(d + " - " + value + "\n")
        #if d == "EXIF:XPComment":
        #    output.write(d + " - " + value + "\n")
        #if d == "EXIF:ImageDescription":
        #    output.write(d + " - " + value + "\n")
        #if d == "EXIF:XPAuthor":
        #    output.write(d + " - " + value + "\n")
        
    output.write("----------------------------\n")

output.close()    
print("\nDONE!\n\n")
sys.exit()