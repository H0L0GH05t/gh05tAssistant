import io, sys, os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch, cm
from reportlab.lib import colors

import subprocess

POINTS_PER_INCH = 72.0
MM_PER_INCH = 25.4
POINTS_PER_MM = POINTS_PER_INCH / MM_PER_INCH

input_path = "LQJ_20160409_34_WEK_DIVERS.pdf"
output_path = 'edition.pdf'
link_page = "link_page.pdf"
center_spread_pdf = True
article_geometry_units = "mm"
# article_geometry_units = "points"

# Case 1: Geometries are already formatted for the split page
# regions = [{ "id": "geometry_2",  "page": "1", "bottom": int(float(0)), "left": int(float(2985378)), "right": int(float(486835)), "top": int(float(1207727))},
#            { "id": "geometry_3",  "page": "2", "bottom": int(float(156000)), "left": int(float(178750)), "right": int(float(6088000)), "top": int(float(4350000))}]
# Case 2: Geometries are formatted for the center spread and need to be adjusted
regions = [{"id": "right_page_geo", "page": "1", "bottom": int(float(440)), "left": int(float(480)), "right": int(float(630)), "top": int(float(30))},
           { "id": "middle_geo",  "page": "1", "bottom": int(float(260)), "left": int(float(210)), "right": int(float(470)), "top": int(float(65))},
           { "id": "left_page_geo",  "page": "1", "bottom": int(float(438)), "left": int(float(13)), "right": int(float(65)), "top": int(float(315))},
           {"id": "left_page_overlap", "page": "1", "bottom": int(float(440)), "left": int(float(5)), "right": int(float(475)), "top": int(float(30))}]

get_pages_cmd = "cpdf -pages %s " % input_path
get_page_info = "cpdf -page-info %s " % input_path
output = subprocess.check_output(get_pages_cmd, shell=True, )

# process = subprocess.Popen(get_pages_cmd + " & " + get_page_info, shell=True, stdout=subprocess.PIPE, )
# output, unused_err = process.communicate()

number_of_pages = int(output.decode('utf-8'))

if number_of_pages > 0:
    try:
        output = subprocess.check_output(get_page_info, shell=True, )
        page_info = output.decode('utf-8')
        page_info_line = page_info.split('\n')
        for line in page_info_line:
            if "MediaBox" in line:
                mediabox = line.replace('MediaBox: ','').split()

        size = {'width': float(mediabox[2]),
                'height': float(mediabox[3])}
        margin = {'left': 0,
                  'top': 0,
                  'right': 0,
                  'bottom': 0}
        scale_factor = 1.0
        if article_geometry_units == "mm":
            scale_factor = POINTS_PER_MM

        ##############################
        # Check for center spread PDF
        if center_spread_pdf:
            split_path_left = "%s-left.pdf" % input_path.replace('.pdf', '')
            crop_pdf_left_cmd = 'cpdf -mediabox "0pt 0pt %s %s" %s -o %s' % (float(size['width'] / 2), float(size['height']), input_path, split_path_left)
            output = subprocess.check_call(crop_pdf_left_cmd, shell=True, stdout=subprocess.PIPE, )

            #Copy the pdf for the right page

            # apply_right_crop_cmd = 'cpdf -frombox /MediaBox -tobox /TrimBox "%s" -o "%s"' % (split_path_right, split_path_right)
            # output = subprocess.check_call(apply_right_crop_cmd, shell=True, stdout=subprocess.PIPE, )
            # print("\n\napplied right crop: %s\n\n" % output)####

            scaled_width = float(size['width']/2)

            # Need to make new pdf object for these pages
            # The left page replaces the existing pdf object
            # The right page gets a new object

            import tempfile
            left_regions = []
            right_regions = []

            for region in regions:
                # Need to check the left geometry values to determine if a geometry is
                # entirely on the right page or left page
                scaled_right = scale_factor * region['right']
                scaled_left = scale_factor * region['left']

                print("\nREGION (%s) left [%s] - right [%s] - scaled width [%s]" % (region['id'], scaled_left, scaled_right, scaled_width))  ####

                if scaled_left < scaled_width and scaled_right > scaled_width:
                    # Geometry is on both pages
                    right_regions.append(region)
                    left_regions.append(region)
                elif scaled_left > scaled_width:
                    # Geometry is on right page only
                    right_regions.append(region)
                else:
                    # Geometry is on left page only
                    left_regions.append(region)

            print("\n\nLeft Regions: %s\n" % left_regions)####

            if left_regions:
                temp_dir = tempfile.gettempdir()
                temp_left_path = os.path.join(temp_dir, "tmp-l.pdf")
                # If a pdf with that name already exists, delete it before continuing
                if os.path.exists(temp_left_path):
                    os.remove(temp_left_path)

                can_left = canvas.Canvas(temp_left_path, pagesize=(float(size['width'] / 2), size['height']))
                for region in left_regions:
                    print("\nWriting region %s to page %s" % (region['id'], region['page']))  ####

                    region_left = scale_factor * region['left']
                    region_bottom = scale_factor * region['bottom']
                    region_right = scale_factor * region['right']
                    region_top = scale_factor * region['top']

                    x1 = float(region_left + margin['left'])
                    y1 = float(size['height'] - region_bottom - margin['top'])
                    x2 = float(region_right + margin['left'])
                    y2 = float(size['height'] - region_top - margin['top'])

                    width = float(region_right - region_left)
                    height = float(region_bottom - region_top)

                    r1 = (x1, y1, x2, y2)
                    url = "http://google.com"
                    can_left.linkURL(url, r1, thickness=1, color=colors.green, relative=1)
                    # current_can.linkURL(url, r1, thickness=1, color=colors.green)
                    can_left.setStrokeColorRGB(1, 0, 1)
                    can_left.setFillColorRGB(1, 0, 1)
                    can_left.rect(x1, y1, width, height, stroke=1, fill=0)
                    can_left.drawString(x2 + 5, y1 * 1.5, str(region['id']))

                can_left.showPage()
                can_left.save()

                try:
                    print("merging left link page [%s]..." % split_path_left)  ####

                    copy_annots_cmd = "cpdf -copy-annotations %s %s 1 -o %s" % (split_path_left, temp_left_path, 'page_left.pdf')
                    output = subprocess.check_call(copy_annots_cmd, shell=True, stdout=subprocess.PIPE, )
                    if output != '0':
                        print(output)

                    stamp_cmd = "cpdf -stamp-under %s %s -o %s" % (split_path_left, 'page_left.pdf', 'page_left.pdf')
                    output = subprocess.check_call(stamp_cmd, shell=True, stdout=subprocess.PIPE, )
                    if output != '0':
                        print(output)

                    # print('temp path left: %s' % temp_left_path)  ####
                    if os.path.exists(temp_left_path):
                        os.remove(temp_left_path)

                except Exception as e:
                    exc_type, exc_value, exc_tb = sys.exc_info()
                    line = exc_tb.tb_lineno
                    print("Exception at Line %s : %s" % (line, e))
                    if os.path.exists(temp_left_path):
                        os.remove(temp_left_path)

            print("\n\n------------Right Regions:\n %s\n" % right_regions)  ####

            if right_regions:
                temp_dir = tempfile.gettempdir()
                temp_right_path = os.path.join(temp_dir, "tmp-r.pdf")
                # If a pdf with that name already exists, delete it before continuing
                if os.path.exists(temp_right_path):
                    os.remove(temp_right_path)

                can_right = canvas.Canvas(temp_right_path, pagesize=(size['width'], size['height']))
                for region in right_regions:

                    # ratio = float(size['width']/region['left']) *

                    # geo_left = float(region['left']/2)
                    # geo_right = float(region['right']/2)

                    geo_left = region['left']
                    geo_right = region['right']

                    print("RIGHT - region left [%s] --> scaled left [%s] -- width [%s] --> half width [%s]" % (region['left'], (scale_factor * geo_left), (scale_factor * size['width']), scaled_width))  ####

                    # middle geometries should be written on both pages as is (if the box goes over the bounds it doesn't matter)
                    # middle is determined by a left that is on the page, and a right that is off the page?

                    print("\nWriting region %s to page %s" % (region['id'], region['page']))  ####

                    region_left = scale_factor * geo_left
                    region_bottom = scale_factor * region['bottom']
                    region_right = scale_factor * geo_right
                    region_top = scale_factor * region['top']

                    x1 = float(region_left + margin['left'])
                    y1 = float(size['height'] - region_bottom - margin['top'])
                    x2 = float(region_right + margin['left'])
                    y2 = float(size['height'] - region_top - margin['top'])

                    width = float(region_right - region_left)
                    height = float(region_bottom - region_top)

                    r1 = (x1, y1, x2, y2)
                    url = "http://google.com/" + region['id']
                    can_right.linkURL(url, r1, thickness=1, color=colors.green, relative=1)
                    # can_right.linkURL(url, r1, thickness=1, color=colors.green)
                    can_right.setStrokeColorRGB(1, 0, 1)
                    can_right.setFillColorRGB(1, 0, 1)
                    can_right.rect(x1, y1, width, height, stroke=1, fill=0)
                    can_right.drawString(x2+5, y1*1.5, str(region['id']))

                can_right.showPage()
                can_right.save()

                try:
                    print("\n\n\nmerging right link page [%s]..." % input_path)  ####

                    copy_annots_cmd = "cpdf -copy-annotations %s %s 1 -o %s" % (input_path, temp_right_path, 'page_right.pdf')
                    print("MERGE CMD:%s\n" % copy_annots_cmd)  ####
                    output = subprocess.check_call(copy_annots_cmd, shell=True, stdout=subprocess.PIPE, )
                    if output != '0':
                        print(output)

                    stamp_cmd = "cpdf -stamp-under %s %s -o %s" % (input_path, 'page_right.pdf', 'page_right.pdf')
                    output = subprocess.check_call(stamp_cmd, shell=True, stdout=subprocess.PIPE, )
                    if output != '0':
                        print(output)

                    split_path_right = "%s-right.pdf" % input_path.replace('.pdf', '')
                    crop_pdf_right_cmd = 'cpdf -mediabox "%s 0pt %s %s" %s -o %s' % (float(size['width'] / 2), float(size['width']) / 2, float(size['height']), 'page_right.pdf', split_path_right)
                    output = subprocess.check_call(crop_pdf_right_cmd, shell=True, stdout=subprocess.PIPE, )

                    # apply_right_crop_cmd = 'cpdf -frombox /MediaBox -tobox /TrimBox "%s" -o "%s"' % (split_path_right, 'page_right.pdf')
                    # output = subprocess.check_call(apply_right_crop_cmd, shell=True, stdout=subprocess.PIPE, )
                    # print("\n\napplied right crop: %s\n\n" % output)  ####


                    # print('temp path right: %s' % temp_right_path)####
                    if os.path.exists(temp_right_path):
                        os.remove(temp_right_path)

                except Exception as e:
                    exc_type, exc_value, exc_tb = sys.exc_info()
                    line = exc_tb.tb_lineno
                    print("Exception at Line %s : %s" % (line, e))
                    if os.path.exists(temp_right_path):
                        os.remove(temp_right_path)


        ##############################
        else:
            #create a new PDF with Reportlab
            #packet = io.BytesIO()
            #can = canvas.Canvas(packet, pagesize=(size['width'], size['height']))
            import tempfile
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, "tmp.pdf")

            # If a pdf with that name already exists, delete it before continuing
            if os.path.exists(temp_path):
                os.remove(temp_path)

            can = canvas.Canvas(temp_path, pagesize=(size['width'], size['height']))

            for region in regions:
                print("Writing region %s" % region['id'])####
                region_left = scale_factor * region['left']
                region_bottom = scale_factor * region['bottom']
                region_right = scale_factor * region['right']
                region_top = scale_factor * region['top']

                x1 = float(region_left + margin['left'])
                y1 = float(size['height'] - region_bottom - margin['top'])
                x2 = float(region_right + margin['left'])
                y2 = float(size['height'] - region_top - margin['top'])

                width = float(region_right - region_left)
                height = float(region_bottom - region_top)

                r1 = (x1, y1, x2, y2)
                url = "http://google.com"
                # can.linkURL(url, r1, thickness=1, color=colors.green, relative=1)
                can.linkURL(url, r1, thickness=1, color=colors.green, relative=1)
                can.setStrokeColorRGB(1,0,1)
                can.setFillColorRGB(1,0,1)
                can.rect(x1, y1, width, height, stroke=1, fill=0)
                can.drawString(x1+3, y2+2, str(region['id']))

            can.showPage()
            can.save()

            try:
                print("merging link page...")  ####

                copy_annots_cmd = "cpdf -copy-annotations %s %s 1 -o %s" % (input_path, output_path, output_path)
                process = subprocess.Popen(copy_annots_cmd, shell=True, stdout=subprocess.PIPE, )
                output, err = process.communicate()
                if err:
                    print(err)

                stamp_cmd = "cpdf -stamp-under %s %s -o %s" % (input_path, temp_path, output_path)
                process = subprocess.Popen(stamp_cmd, shell=True, stdout=subprocess.PIPE, )
                output, err = process.communicate()
                if err:
                    print(err)

                if os.path.exists(temp_path):
                    os.remove(temp_path)

            except Exception as e:
                exc_type, exc_value, exc_tb = sys.exc_info()
                line = exc_tb.tb_lineno
                print("Exception at Line %s : %s"%(line,e))
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            #
            #if link_page != None:
            #    print("LINK PAGE!")
    except Exception as e:
        exc_type, exc_value, exc_tb = sys.exc_info()
        line = exc_tb.tb_lineno
        print("Exception at Line %s : %s" % (line, e))

print("\n\nFinished")

sys.exit()

####### Using imagemagick #######
# convert input_pdf:   -crop 50%x1+0+0      crop_half.jpg
# -crop 2x1
# http://imagemagick.org/discourse-server/viewtopic.php?t=18127
# http://www.imagemagick.org/Usage/crop/#crop_equal
########################


######## Using GS #######
# gswin32c.exe
# -o cropped.pdf
# -sDEVICE=pdfwrite
# -c "[/CropBox [24 72 559 794]"
# -c " /PAGES pdfmark"
# -f uncropped-input.pdf
########################

######## Using CPDF #######
# http://www.coherentpdf.com/cpdfmanual.pdf
# cpdf -crop "0pt 0pt 200mm 200mm" in.pdf -o out.pdf
#             minX minY height width
########################