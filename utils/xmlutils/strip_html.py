import os, sys, re
# from bs4 import UnicodeDammit
# from bs4 import BeautifulSoup, Comment
try:
    from lxml import etree
    from lxml.html.clean import Cleaner
    from lxml.cssselect import CSSSelector
except Exception:
    etree = None
    Cleaner = None

# input_file = "article_gp.xml"
input_str = "<h1>testing title3</h1>"

def strip_html_tags(text, strip_all, strip_inline_styles=False):
    stripped_str = text
    if text:
        tag_re = re.compile('<[^>]*>')
        header_re = re.compile('h\d', re.IGNORECASE)

        tags = tag_re.findall(text)
        keep_tags = ['b', 'strong', 'i', 'em', 'emphasis',
                     'u', 'strike', 'br','span']

        # New method
        if tags:
            # try:
            text = "<rt>%s</rt>" % text
            dom = etree.fromstring(text)
            strip_tags_list = []
            for element in dom.iter():
                print('\nelement: %s -- %s' % (element.tag, element.attrib))
                # Strip Inline Styles
                if strip_inline_styles and 'style' in element.attrib:
                    print("Stripping style")
                    del element.attrib['style']

                # Strip Header
                if header_re.match(element.tag):
                    print("HEADER")
                    if element.attrib:
                        print("CHANGE TO SPAN")
                        element.tag = 'span'
                        print(element)
                    else:
                        strip_tags_list.append(element.tag)
                        print("REMOVE %s" % element.tag)
                # Strip All tags
                if strip_all and (element.tag not in keep_tags):
                    strip_tags_list.append(element.tag)
                    #TODO: convert to span if attributes to preserve customer classes?

            if strip_tags_list:
                etree.strip_tags(dom, strip_tags_list)
            stripped_str = etree.tostring(dom, encoding='UTF-8')
            if isinstance(stripped_str, bytes):
                stripped_str = stripped_str.decode('utf-8')
            stripped_str = stripped_str[4:-5] #remove root we added
            # except Exception as e:
            #     print("Exception reading tags: %s" % e)

        # Old method
        # keep_tags = ['<b ', '<b/', '<b>', '</b>',
        #              '<strong', '</strong>',
        #              '<i ', '<i/', '</i>', '<i>',
        #              '<em ', '</em ', '<em>', '</em>',
        #              '<emphasis', '</emphasis>',
        #              '<u ', '<u/', '<u>', '</u>',
        #              '<strike', '</strike>',
        #              '<br ', '<br/', '<br>', '</br>',
        #              '<span', '</span>']
        # if strip_all:
        #     for tag in tags:
        #         remove_tag = False
        #         for keep_tag in keep_tags:
        #             if tag.lower().startswith(keep_tag):
        #                 remove_tag = False
        #                 break
        #             else:
        #                 remove_tag = True
        #         if remove_tag:
        #             stripped_str = stripped_str.replace( tag +'\n' ,"")
        #             stripped_str = stripped_str.replace(tag ,"")
        #         elif strip_inline_styles:
        #             # Strip inline styles
        #             m = inline_styles_re.match(tag.lower())
        #             if not m:
        #                 m = inline_styles_re2.match(tag.lower())
        #             if m:
        #                 style_attr = m.group(1)
        #                 stripped_str = stripped_str.replace( ' ' +style_attr, "")
        #
        # else:
        #     for tag in tags:
        #         replace_end_tag = False
        #         if header_re.match(tag.lower()):
        #             logger.warning("found header tag: %s" % tag  )####
        #             logger.warning("before: %s" % stripped_str)  ####
        #             stripped_str = stripped_str.replace( tag +'\n' ,"")
        #             stripped_str = stripped_str.replace(tag ,"")
        #
        #         if strip_inline_styles:
        #             # Strip inline styles
        #             m = inline_styles_re.match(tag.lower())
        #             if not m:
        #                 m = inline_styles_re2.match(tag.lower())
        #             if m:
        #                 style_attr = m.group(1)
        #                 stripped_str = stripped_str.replace( ' ' +style_attr, "")
        #         logger.warning("result: %s" % stripped_str)  ####
    return stripped_str

##########

def main(argv):
    if argv:
        input_file = argv[0]
        if os.path.exists(input_file):
            raw_str = ''
            print("Reading text from file %s...\n" % input_file)
            with open(input_file, 'r') as txt_file:
                raw_str = txt_file.read()
                txt_file.close()

            strip_all = False
            strip_inline_styles = False

            stripped_str = strip_html_tags(raw_str, strip_all, strip_inline_styles=strip_inline_styles)
            print("Result:\n\n%s" % stripped_str)

            write_results = input("Write to file? y/n\n")
            if write_results.lower().strip().startswith('y'):
                if os.path.exists('results.txt'):
                    print("Old file exists!")
                    os.remove('results.txt')
                with open("results.txt", 'w') as results_file:
                    results_file.write(stripped_str)
                    results_file.close()
        else:
            print("File %s doesn't exist!" % input_file)
    else:
        print("No filename given!\n Call using 'python strip_html.py [filename]'")
    print("ENDING")
    sys.exit()



if __name__ == "__main__":
    main(sys.argv[1:])
