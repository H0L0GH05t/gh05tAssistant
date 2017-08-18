import io, os, sys, errno
import subprocess
import tempfile
import shutil
import re
import codecs
import getopt

from io import StringIO, BytesIO
from bs4 import UnicodeDammit
from bs4 import BeautifulSoup, Comment

try:
    from lxml import etree
    from lxml.html.clean import Cleaner
    from lxml.cssselect import CSSSelector
except Exception:
    print('LXML library not found')
    etree = None
    Cleaner = None

from copy import deepcopy

#TODO: Look into writing to excel sheet --> https://github.com/python-excel
# http://stackoverflow.com/questions/13437727/python-write-to-excel-spreadsheet

###############################################

class ParseCDATAExtElement(etree.XSLTExtension):
    def execute(self, context, self_node, input_node, output_parent):
        # lxml python ext for parsing CDATA into html
        print("running cdata parse extension!")####
        input_cdata = input_node.text
        input_xml = etree.ElementTree(etree.fromstring(input_cdata))

        root = input_xml.getroot()
        # for node in root:
            # parsed_html.append(node)

        results = self.apply_templates(context, root)
        output_parent.append(results[0])

class StringReExtElement(etree.XSLTExtension):
    def execute(self, context, self_node, input_node, output_parent):
        # lxml python ext for parsing strings into tables using regex
        # TODO: add ability to import a list of regex to find a possible match
        print("\n\nrunning string regex extension!\n")####
        re_list = []
        try:
            re_str = self_node.attrib['re_str']
        except Exception as e:
            print("StringReExtElement Failed to get p_on_fail attribute value: %s" % e)

        return_string = False
        try:
            string_only = self_node.attrib['string_only']
            if string_only.lower().strip() == 'true' or string_only.lower().strip() == 'yes':
                return_string = True
        except Exception as e:
            print("StringReExtElement Failed to get string_only attribute value: %s" % e)

        input_text = input_node.text
        elem = deepcopy(input_node)

        # Return text only or return node?
        # Return node or apply templates and return result?

        results = self.apply_templates(context, root)
        output_parent.append(results[0])

class ReTableExtElement(etree.XSLTExtension):
    def execute(self, context, self_node, input_node, output_parent):
        # lxml python ext for parsing strings into tables using regex
        # TODO: add ability to import a list of regex to find a possible match
        print("\n\nrunning table regex extension!\n")####
        re_list = []
        re_str = self_node.attrib['re_str']
        # (\S+\s-\s\S+\s*\S*)\s+(\d+\:\d+) --> LQJ example "Buochs - Mxnsingen  2:2"
        # (\d+\.\D+\s{1}[^\s]\d+\s|\d+\.\D+\s)\s+(\S*)\s+(\S*)\s+(\S*)\s+(\S*)\s+(\S*)\s+(\S*)\s*
        #   \--> LQJ example "4.âZoug 94   18 7 6 5 31-23 27  5.âYoung Boys M21   18 7 5 6 34-27 26  6.âThoune M21   18 7 5 6 34-29 26  7.âSoleure   18 6 8 4 27-26 26  "
        P_on_fail = False
        try:
            P_on_fail_attr = self_node.attrib['p_on_fail']
            if P_on_fail_attr.lower().strip() == 'true' or P_on_fail_attr.lower().strip() == 'yes':
                P_on_fail = True
        except Exception as e:
            print("ReTableExtElement Failed to get p_on_fail attribute value: %s" % e)
        row_only = False # Default is to create a full table element
        create_table = "true"
        try:
            create_table = self_node.attrib['create_table']
            if create_table.lower().strip() == 'false' or create_table.lower().strip() == 'no':
                row_only = True
        except Exception as e:
            print("ReTableExtElement Failed to get create_table attribute value: %s" % e)
        elem = deepcopy(input_node)

        if row_only:
            # If row_only, we should create and return a single "tr" element instead of a full "table"
            print("re_str: %s" % re_str)  ####
            table_row = None
            for text_item in elem.itertext():
                matching_el = False
                for el in elem.iterchildren():
                    if el.text == text_item:
                        match = re.compile(re_str).findall(el.text)
                        if match:
                            print("Matched text for ROW")  ####
                            for row in match:
                                table_row = etree.Element("tr")
                                for attr in el.attrib:
                                    table_row.set(attr, el.attrib[attr])
                                for col in row:
                                    table_column2 = etree.SubElement(table_row, "td")
                                    table_column2.text = col
                        else:
                            print("FAILED TO MATCH text for ROW")  ####
                            if P_on_fail:
                                new_p = etree.Element("p")
                                new_p.set('evr-ext-class', 'table-item')  # Set special attribute for parsing
                                for attr in el.attrib:
                                    new_p.set(attr, el.attrib[attr])
                                new_p.text = el.text
                                output_parent.append(new_p)
                            else:
                                table_row = etree.Element("tr")
                                for attr in el.attrib:
                                    table_row.set(attr, el.attrib[attr])
                                table_column = etree.SubElement(table_row, "td")
                                table_column.text = el.text

                        matching_el = True
                if not matching_el:
                    match = re.compile(re_str).findall(text_item)
                    if match:
                        print("Matched text2 for ROW")  ####
                        for row in match:
                            table_row = etree.Element("tr")
                            for attr in elem.attrib:
                                table_row.set(attr, elem.attrib[attr])
                            for col in row:
                                table_column2 = etree.SubElement(table_row, "td")
                                table_column2.text = col
                    else:
                        print("FAILED TO MATCH text2 for ROW" )  ####
                        if P_on_fail:
                            new_p = etree.Element("p")
                            new_p.set('evr-ext-class', 'table-item')  # Set special attribute for parsing
                            for attr in elem.attrib:
                                new_p.set(attr, elem.attrib[attr])
                            new_p.text = text_item
                            output_parent.append(new_p)
                        else:
                            table_row = etree.Element("tr")
                            for attr in elem.attrib:
                                table_row.set(attr, elem.attrib[attr])
                            table_column = etree.SubElement(table_row, "td")
                            table_column.text = text_item
                            
                if table_row is not None:
                    output_parent.append(table_row)
                    print("RETURNING TABLE ROW")  ####
                else:
                    print("no table row...")  ####
        else:
            # Process any aditional nodes
            table_nodes = etree.Element('table_nodes')
            self.process_children(context, output_parent=table_nodes)
            print("\nExtra Nodes:")
            print(etree.tostring(table_nodes))####
            print("\n")

            # get regex strings from input node
            # re_list.append(input_node.text)
            # for re_str in re_list:
                # find the best re match
                # match = re.match(re_str, input_str)

            print("re_str: %s" % re_str)  ####
            table = etree.Element("table")
            table.set('evr-ext-class', 'table-item')  # Set special attribute for parsing
            for text_item in elem.itertext():
                matching_el = False
                for el in elem.iterchildren():
                    if el.text == text_item:
                        match = re.compile(re_str).findall(el.text)
                        if match:
                            print("Matched text")  ####
                            for row in match:
                                table_row = etree.SubElement(table, "tr")
                                for attr in el.attrib:
                                    table_row.set(attr, el.attrib[attr])
                                for col in row:
                                    table_column2 = etree.SubElement(table_row, "td")
                                    table_column2.text = col
                        else:
                            print("FAILED TO MATCH text")  ####
                            if P_on_fail:
                                new_p = etree.Element("p")
                                new_p.set('evr-ext-class', 'table-item')  # Set special attribute for parsing
                                for attr in el.attrib:
                                    new_p.set(attr, el.attrib[attr])
                                new_p.text = el.text
                                output_parent.append(new_p)
                            else:
                                table_row = etree.SubElement(table, "tr")
                                for attr in el.attrib:
                                    table_row.set(attr, el.attrib[attr])
                                table_column = etree.SubElement(table_row, "td")
                                table_column.text = el.text

                        matching_el = True
                if not matching_el:
                    match = re.compile(re_str).findall(text_item)
                    if match:
                        print("Matched text2")  ####
                        for row in match:
                            table_row = etree.SubElement(table, "tr")
                            for attr in elem.attrib:
                                table_row.set(attr, elem.attrib[attr])
                            for col in row:
                                table_column2 = etree.SubElement(table_row, "td")
                                table_column2.text = col
                    else:
                        print("FAILED TO MATCH text2" )  ####
                        if P_on_fail:
                            new_p = etree.Element("p")
                            new_p.set('evr-ext-class', 'table-item')  # Set special attribute for parsing
                            for attr in elem.attrib:
                                new_p.set(attr, elem.attrib[attr])
                            new_p.text = text_item
                            output_parent.append(new_p)
                        else:
                            table_row = etree.SubElement(table, "tr")
                            for attr in elem.attrib:
                                table_row.set(attr, elem.attrib[attr])
                            table_column = etree.SubElement(table_row, "td")
                            table_column.text = text_item
            # If we have addition nodes, add rows here
            if table_nodes is not None:
                for table_node in table_nodes:
                    for text_item in table_node.itertext():
                        matching_el = False
                        for el in table_node.iterchildren():
                            if el.text == text_item:
                                match = re.compile(re_str).findall(el.text)
                                if match:
                                    print("EXTRA Matched text")  ####
                                    for row in match:
                                        table_row = etree.SubElement(table, "tr")
                                        for attr in el.attrib:
                                            table_row.set(attr, el.attrib[attr])
                                        for col in row:
                                            table_column2 = etree.SubElement(table_row, "td")
                                            table_column2.text = col
                                else:
                                    print("EXTRA FAILED TO MATCH text")  ####
                                    if P_on_fail:
                                        new_p = etree.Element("p")
                                        new_p.set('evr-ext-class', 'table-item')  # Set special attribute for parsing
                                        for attr in el.attrib:
                                            new_p.set(attr, el.attrib[attr])
                                        new_p.text = el.text
                                        output_parent.append(new_p)
                                    else:
                                        table_row = etree.SubElement(table, "tr")
                                        for attr in el.attrib:
                                            table_row.set(attr, el.attrib[attr])
                                        table_column = etree.SubElement(table_row, "td")
                                        table_column.text = el.text

                                matching_el = True
                        if not matching_el:
                            match = re.compile(re_str).findall(text_item)
                            if match:
                                print("EXTRA Matched text2")  ####
                                for row in match:
                                    table_row = etree.SubElement(table, "tr")
                                    for attr in table_node.attrib:
                                        table_row.set(attr, table_node.attrib[attr])
                                    for col in row:
                                        table_column2 = etree.SubElement(table_row, "td")
                                        table_column2.text = col
                            else:
                                print("EXTRA FAILED TO MATCH text2")  ####
                                if P_on_fail:
                                    new_p = etree.Element("p")
                                    new_p.set('evr-ext-class', 'table-item')  # Set special attribute for parsing
                                    for attr in table_node.attrib:
                                        new_p.set(attr, table_node.attrib[attr])
                                    new_p.text = text_item
                                    output_parent.append(new_p)
                                else:
                                    table_row = etree.SubElement(table, "tr")
                                    for attr in table_node.attrib:
                                        table_row.set(attr, table_node.attrib[attr])
                                    table_column = etree.SubElement(table_row, "td")
                                    table_column.text = text_item

            if table is not None:
                output_parent.append(table)
                print("RETURNING TABLE")  ####
            else:
                print("no table...")  ####


#### Code from Eversify

class XMLProcesser():
    def __init__(self):
        self.article_path = None  # used during processing, do not initialize
        self.article_count = 0 # used in the description
        
        self.is_pdf_replica = False
        self.is_hybrid = False
        self.archive_ext = '.zip'
        self.article_ext = '.xml'
        self.zip_path = None
        self.articlePath_endswith = None
        self.encoding = 'utf-8'
        self.xslt_path = None
        self.is_docx = False
    
    def splitfile(self, f):
        finfo = None
        try:
            finfo = {'fullname': f}
            path = os.path.dirname(f)
            basename = os.path.basename(f)
            root, ext = os.path.splitext(basename)
            finfo['path'] = path
            finfo['basename']  = basename
            finfo['root'] = root
            finfo['ext']  = ext
        except Exception as e:
            print("Exception in splitfile: %s" % e)
        return finfo
    
    def is_article_file(self, filename, ext):
        # Find article file within folder
        isExtOk = str(ext.lower()) == str(self.article_ext)
        if os.path.basename(filename).startswith('.'):
            isExtOk = False
        return isExtOk 
    
    def parse_xml_from_file_like_object(self, some_file_like_object):
        # Create HTML parser object
        parser = etree.XMLParser(ns_clean=True,
                                 remove_blank_text=True,
                                 recover=True,
                                 resolve_entities=True)
        try:
            dom = etree.parse(some_file_like_object, parser)
        except etree.XMLSyntaxError as e:
            log = e.error_log.filter_from_level(etree.ErrorLevels.FATAL)
            print("\n-------------------------\n" + "Error in parse_xml_from_file_like_object:\n" + log + "\n-------------------------\n")
            return
        return dom
    
    def parse_xml_from_bytes(self, b):
        # For use with text/files using an unknown encoding (e.g. input/uploaded data)
        file_like_object = io.BytesIO(b)
        return self.parse_xml_from_file_like_object(file_like_object)
    
    def parse_xml_from_utf8_str(self, xmlstr):
        # For use with text stored in our DB (our DB saves text as UTF-8)
        b = xmlstr.encode('utf-8')
        if b is not None:
            b = b.lstrip(b'\xef\xbb\xbf') # Remove BOM
        return self.parse_xml_from_bytes(b)
    
    def apply_transform(self, article_xml, xslt, filename, use_ext):
        transform = None
        result = article_xml
        if xslt and len(xslt) > 0:
            try:
                xslt_root = self.parse_xml_from_utf8_str(xslt)
                if use_ext:
                    #### extensions ####
                    parse_cdata_ext = ParseCDATAExtElement()
                    re_table_ext = ReTableExtElement()
                    extensions = {('eversifyns', 'cdata-ext'): parse_cdata_ext,
                                  ('eversifyns', 'table-ext'): re_table_ext}
                    transform = etree.XSLT(xslt_root, extensions = extensions)
                    ########################
                else:
                    transform = etree.XSLT(xslt_root)
                filename = "'" + filename + "'"
                result = transform(article_xml, param1=filename)
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print("\nException in apply_transform: %s - line %s\n\n" % (e, exc_traceback.tb_lineno))
                if transform:
                    print('---LXML Error Log----\n')
                    for entry in transform.error_log:
                        print('message from line %s, col %s: %s' % (entry.line, entry.column, entry.message))
                        print('\n')
                    print('---End Log----\n')
        return result
    
    def parse_article(self, article_data, xslt_data, xslt2_data, filename, use_ext, use_xslt2, save_first_result):
        articleXml = None
        try:
            article_dom = self.parse_xml_from_utf8_str(article_data)
            # article_dom = self.parse_xml_from_bytes(article_data)
            if article_dom:
                articleXml = article_dom
                articleXml = self.apply_transform(articleXml, xslt_data, filename, use_ext)
                if use_xslt2:
                    if save_first_result:
                        output_file_path = "temp_output_path"
                        # If the folder doesn't exist, create it
                        if not os.path.exists(output_file_path):
                            os.mkdir(output_file_path)
                        # save the result here first!
                        print("saving transformation 1")####
                        # Generate name for folder to hold results
                        output_xml_path = os.path.join(output_file_path, "transformed_1_" + filename + '.xml')

                        # Remove existing output files with the same name
                        if os.path.exists(output_xml_path):
                            os.remove(output_xml_path)

                        print("writing file: %s" % output_xml_path)####
                        # Write output file
                        with codecs.open(output_xml_path, 'w', 'utf-8') as output_file:
                        # with open(output_xml_path, 'w', encoding="utf-8") as output_file:
                            output_file.write(str(articleXml))
                    articleXml = self.apply_transform(articleXml, xslt2_data, filename, use_ext)
            else:
                print("Error in parse_article: parse_xml_from_bytes returned None for article_dom on file %s - the encoding may not match the delcared encoding the xml header" % filename)
                return
        except etree.XMLSyntaxError as e:
            log = e.error_log.filter_from_level(etree.ErrorLevels.FATAL)
            print("Exception XMLSyntaxError in parse_article: %s" % log)
            return
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("Error in parse_article: %s - line %s" % (e, exc_traceback.tb_lineno))
        return articleXml
    
    def process_xml(self, f, xslt_data, xslt2_data, use_ext, use_xslt2, save_first_result):
        print("Processing file: " + str(f))####
        article_dom = ''
        try:
            if not isinstance(f, str):
                try:
                    str(f, "ascii")
                except UnicodeError:
                    try:
                        str(f, "utf-8")
                    except UnicodeError:
                        f = f.decode("cp437")
                    else:
                        pass
                else:
                    pass
            finfo = self.splitfile(f)
            if finfo:
                if self.is_article_file(f, finfo['ext']):
                    uid = finfo['root']
                    article_data = ''
                    with open(f, 'r', encoding=self.encoding) as article_file:
                        article_data = article_file.read()
                    article_dom = self.parse_article(article_data, xslt_data, xslt2_data, uid, use_ext, use_xslt2, save_first_result)
            else:
                print("Error: finfo returned None for file '%s'" % f)
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("Exception in process_xml: %s - line %s" % (e, exc_traceback.tb_lineno))
        return article_dom

def innerHtml(element_node):
    inner = ''
    try:
        if element_node is None:
            inner = ''
        elif isinstance(element_node, etree._ElementStringResult):
            inner = str(element_node)
        elif isinstance(element_node, etree._ElementUnicodeResult):
            inner = str(element_node)
        elif isinstance(element_node, str):
            inner = element_node
        elif isinstance(element_node, str):
            inner = str(element_node)
        elif isinstance(element_node, etree._Element):
            # one node
            inner = etree.tostring(element_node,
                                   encoding=str,
                                   method='html',
                                   with_tail=False)
        # Do we have a list of elements?
        elif isinstance(element_node, list):
            if isinstance(element_node[0], etree._Element):
                if len(element_node) > 0:
                    inner = ''.join([etree.tostring(el,
                                                     encoding=str,
                                                     method='html',
                                                     with_tail=False) for el in element_node])
            elif isinstance(element_node[0], etree._ElementUnicodeResult):
                inner = ''.join([str(el) for el in element_node])
            elif isinstance(element_node[0], etree._ElementStringResult):
                inner = ''.join([str(el) for el in element_node])
            elif isinstance(element_node[0], str):
                inner = ''.join([el for el in element_node])
            elif isinstance(element_node[0], str):
                inner = ''.join([str(el) for el in element_node])
        else:
            # Not sure what to do with this, does not match any types we should be getting here
            inner = ''
    except Exception:
        logger.exception('')
        inner = str(element_node)
    return inner

### ------------------------------------------------------------------------ ###

def normalize(path, full_path):
    normalized_path = path
    if full_path:
        normalized_path = os.path.normcase(os.path.normpath(path)).replace('\\', '/')
    else:
        normalized_path = path.replace('\\', '/')
    return normalized_path

def get_xml_info(presets_path, output_file_path, xml_folder_path, xslt_path, pub_name, encoding):
    is_pdf_replica = False
    is_hybrid = False
    encoding = ''
    archive_ext = ''
    zip_path = ''
    articlePath_endswith = ''
    article_ext = ''
    is_docx = False

    xslt_path = ''
    # xslt2_path = '' # Only run 1 xslt for now
    use_xslt2 = False # Only run 1 xslt for now
    xml_folder_path = ''
    edition_list = ''

    # Turn off extensions since we are just using a basic class lister
    use_ext = False
    save_first_result = False # we only run 1 xslt for this function

    print("\n\npresets_path: %s\npub_name: %s\noutput_file_path: %s\nxml_folder_path: %s\nxslt_path: %s\nencoding: %s\nedition_list: %s\n\n" %
                      (presets_path, pub_name, output_file_path, xml_folder_path, xslt_path, encoding, edition_list))

    # Check for a presets file
    if os.path.exists(presets_path):
        try:
            with open(presets_path, 'r') as presets_file:
                for line in presets_file.readlines():
                    if "pub_name=" in line:
                        pub_name = line.split('pub_name=')[1].strip()
                    if "output_path=" in line:
                        output_file_path = normalize(line.split('output_path=')[1].strip(), True)
                    if "xml_folder_path=" in line:
                        xml_folder_path = normalize(line.split('xml_folder_path=')[1].strip(), False)
                    if "xslt_path=" in line:
                        xslt_path = normalize(line.split('xslt_path=')[1].strip(), False)
                    # if "use_xslt2=" in line:
                    #     use_xslt2 = line.split('use_xslt2=')[1].strip() == 'true'
                    # if "xslt2_path=" in line:
                    #     xslt2_path = normalize(line.split('xslt2_path=')[1].strip(), False)
                    if "encoding=" in line:
                        encoding = line.split('encoding=')[1].strip()
                    if "edition_list=" in line:
                        edition_list = line.split('edition_list=')[1].strip()

                print("\n\npub_name: %s\noutput_file_path: %s\nxml_folder_path: %s\nxslt_path: %s\nencoding: %s\nedition_list: %s\n\n" %
                      (pub_name, output_file_path, xml_folder_path, xslt_path, encoding, edition_list))

            if not xml_folder_path or not xslt_path or not encoding:
                print("\nSome required information was missing from the presets file. Please provide the following information:\n")

            if not encoding:
                encoding = input("From the General tab in the Archive Import Recipe, please copy and paste Encoding:\n")
            if not xslt_path:
                xslt_path = normalize(input("\nPlease enter the full path to the xslt file you would like to use:\n"), False)
            # if use_xslt2 and not xslt2_path:
            #     xslt2_path = normalize(input("\nPlease enter the full path to the 2nd xslt file you would like to use:\n"), False)
            if not xml_folder_path:
                xml_folder_path = normalize(input("\nPlease enter the full path to the folder containing the xml files:\n"), False)
        except Exception as e:
            print("Exception loading presets: %s" % e)

    # If no preset file, check for paths set by args
    elif xml_folder_path or xslt_path:
        if xml_folder_path and xslt_path:
            # Both were set, check if they are valid
            if os.path.exists(xml_folder_path) and not os.path.exists(xslt_path):
                # Only the xml_folder_path exists
                xslt_path = normalize(input("\nThe XSLT path you provided was not valid. Please enter a valid full path to the xslt file you would like to use:\n"), False)
            elif os.path.exists(xslt_path) and not os.path.exists(xml_folder_path):
                # Only the xslt_path exists
                xml_folder_path = normalize(input("\nThe XML folder path you provided was not valid. Please enter a valid full path to the folder containing the xml files:\n"), False)
            elif not os.path.exists(xml_folder_path) and not os.path.exists(xml_folder_path):
                # Neither path is valid!
                print("\nNeither the XML folder path nor the XSLT path you provided was valid. Please provide valid paths:\n")
                xslt_path = normalize(input("\nPlease enter a valid full path to the xslt file you would like to use:\n"), False)
                xml_folder_path = normalize(input("\nPlease enter a valid full path to the folder containing the xml files:\n"), False)

        elif xml_folder_path:
            # Only the xml folder path was set
            if os.path.exists(xml_folder_path):
                # Only the xslt_path exists
                xslt_path = normalize(input("\nThe XSLT file path was not provided. Please enter the full path to the xslt file you would like to use:\n"), False)
            else:
                # The path was not valid, so we need both
                print("\nThe XML folder path you provided was not valid and the XSLT path was not provided. Please provide valid paths for both:\n")
                xslt_path = normalize(input("\nPlease enter a valid full path to the xslt file you would like to use:\n"), False)
                xml_folder_path = normalize(input("\nPlease enter a valid full path to the folder containing the xml files:\n"), False)

        else:
            # Only the xslt path was set
            if os.path.exists(xslt_path):
                # Only the xslt_path exists
                xml_folder_path = normalize(input("\nThe XML folder path was not provided. Please enter the full path to the folder containing the xml files:\n"), False)
            else:
                # The path was not valid, so we need both
                print("\nThe XML folder path was not set and the XSLT path you provided was not valid. Please provide valid paths for both:\n")
                xslt_path = normalize(input("\nPlease enter a valid full path to the xslt file you would like to use:\n"), False)
                xml_folder_path = normalize(input("\nPlease enter a valid full path to the folder containing the xml files:\n"), False)

        # By now we should have both paths set, so check the encoding
        if not encoding:
            encoding = input("\nThe Encoding was not provided. From the General tab in the Archive Import Recipe, please copy and paste Encoding:\n")

        # Check the path for the 2nd xslt if we are set to use it
        # if use_xslt2:
        #     if not xslt2_path or os.path.exists(xslt2_path):
        #         xslt2_path = normalize(input("\nPlease enter a valid full path to the 2nd xslt file you would like to use:\n"), False)

    # If no presets, then prompt the user for input
    else:
        try:
            # From Archive Import Recipe
            print("\nPlease provide the following information:\n")
            encoding = input("From the General tab in the Archive Import Recipe, please copy and paste Encoding:\n")
            #archive_ext = input("From the Import Rules tab, copy and paste Archive Ext:\n")
            # zip_path = input("From the Import Rules tab, copy and paste Zip Path:\n")
            #articlePath_endswith = input("From the Import Rules tab, copy and paste Article Path ends with:\n")
            # article_ext = input("From the Import Rules tab, copy and paste Article Ext:\n\n")
            # For XSLT
            xslt_path = normalize(input("\nPlease enter the full path to the xslt file you would like to use:\n"), False)
            # use_xslt2 = normalize(input("\nPlease enter the full path to the xslt file you would like to use:\n"), False)
            # xslt2_path = normalize(input("\nPlease enter the full path to the 2nd xslt file you would like to use:\n"), False)
            xml_folder_path = normalize(input("\nPlease enter the full path to the folder containing the xml files:\n"), False)
        except Exception as e:
            print("Exception getting user input: %s" % e)
        
    try:
        if os.path.exists(xml_folder_path):
            if os.path.exists(xslt_path):
                # Begin task
                print("\nThank you for your input. Please wait while I generate your info file...\n\n-----------------------------\n")
                
                xml_set = XMLProcesser()
                
                # if is_pdf_replica != None:
                #     xml_set.is_pdf_replica = is_pdf_replica
                # if is_hybrid != None and is_pdf_replica:
                #     xml_set.is_hybrid = is_hybrid
                if encoding != '':
                    xml_set.encoding = encoding
                if archive_ext != '':
                    xml_set.archive_ext = archive_ext
                # if zip_path != '':
                #     xml_set.zip_path = zip_path
                if articlePath_endswith != '':
                    xml_set.articlePath_endswith = articlePath_endswith
                if article_ext != '':
                    xml_set.article_ext = article_ext
                    
                if xslt_path != '':
                    xml_set.xslt_path = xslt_path
                # if xslt2_path != '':
                #     xml_set.xslt2_path = xslt2_path
                if is_docx:
                    xml_set.is_docx = is_docx
                
                # Get XSLT data from file
                xslt_data = ''
                xslt2_data = ''
                with open(xslt_path, 'r') as xslt_file:
                    xslt_data = xslt_file.read()
                # if xslt2_path:
                #     with open(xslt2_path, 'r') as xslt2_file:
                #         xslt2_data = xslt2_file.read()
                
                # Data we will add to the info file
                successful_files_count = 0
                failed_files_count = 0
                total_files_count = 0
                
                total_elements_count = 0
                unique_elements_count = 0

                total_attribute_count = 0
                unique_attribute_count = 0
                unique_attr_val_count = 0

                #TODO: add counter for attributes under each element (i.e. element "div" has 4 possible attributes)
                #TODO: add counter for possible values for each attributes (i.e. attribute "class" has 4 possible values)
                
                failed_files_list = []
                
                # Transform each XML file
                tag_list = {} # tag list will be for all articles
                for xml_file in os.listdir(xml_folder_path):
                    if xml_file.endswith(xml_set.article_ext):
                        total_files_count += 1
                        full_path = os.path.join(xml_folder_path, xml_file)
                        article_dom = xml_set.process_xml(full_path, xslt_data, xslt2_data, use_ext, use_xslt2, save_first_result)
                        if article_dom:
                            successful_files_count += 1
                            for element in article_dom.getiterator():
                                total_elements_count += 1

                                # Add new tag names to the list (unless it's our root container element)
                                if not element.tag in tag_list and element.tag != 'ClassnameContainer':
                                    tag_list[element.tag] = {}
                                    unique_elements_count += 1

                                for attribute in element.attrib:
                                    total_attribute_count += 1
                                    # Change the blank attribute values to empty quotes
                                    if element.attrib[attribute] == "":
                                        element.attrib[attribute] = '""'
                                    # If the attribute is already listed for the element, add the attrib value to the list for this attrib
                                    if attribute in tag_list[element.tag]:
                                        # Check if the attribute is in the list already, and if it's new then add it to the list
                                        if not ',' + element.attrib[attribute] + ',' in tag_list[element.tag][attribute] \
                                        and not ',' + element.attrib[attribute] + '}' in tag_list[element.tag][attribute] \
                                        and not '{' + element.attrib[attribute] + ',' in tag_list[element.tag][attribute] \
                                        and tag_list[element.tag][attribute] != '{' + element.attrib[attribute] + '}':
                                            # We do this to get a comma delimited list of all the possible values for each attribute (the end bracket tells us where the end of the list is)
                                            if tag_list[element.tag][attribute][-1:] == '}':
                                                new_item = str(tag_list[element.tag][attribute])[:-1] + ',' + element.attrib[attribute] + '}'
                                            else:
                                                new_item = tag_list[element.tag][attribute] + ',' + element.attrib[attribute] + '}'
                                            tag_list[element.tag][attribute] = new_item
                                            unique_attr_val_count += 1
                                    # If we don't have this attribute for this element yet, add it with its value
                                    else:
                                        tag_list[element.tag][attribute] = '{' + element.attrib[attribute] + '}'
                                        unique_attribute_count += 1
                                        unique_attr_val_count += 1
                        else:
                            failed_files_count += 1
                            failed_files_list.append(xml_file)
                            print("Error: file '%s' article_dom returned as '%s'" % (xml_file, article_dom))
                    else:
                        print("File found with non-article extension: %s" % xml_file)
                
                # Generate name for info file and remove any existing ones with that name
                if output_file_path:
                    info_file_path = output_file_path
                    if not '.txt' in output_file_path:
                        info_file_path = ('%s%s') % (output_file_path, '.txt')
                else:
                    info_file_path = xml_folder_path + "-xml_info.txt"
                if os.path.exists(info_file_path):
                    os.remove(info_file_path)
                
                # Write info file
                with open(info_file_path, 'a', encoding="utf-8", errors="surrogateescape") as output_file:
                    # Write gathered data and counts info first
                    output_file.write("XML Tag Data:\n==============\n")
                    output_file.write("Successful Files: %s\n" % successful_files_count)
                    output_file.write("Failed Files:     %s\n" % failed_files_count)
                    output_file.write("Total Files:      %s\n" % total_files_count)
                    if len(failed_files_list) > 0:
                        output_file.write("List of Failed Files:\n")
                        for failed_file in failed_files_list:
                            output_file.write("    %s\n" % failed_file)
                        output_file.write("\n")
                    output_file.write("Total Element Count:          %s\n" % total_elements_count)
                    output_file.write("Unique Element Count:         %s\n" % unique_elements_count)
                    output_file.write("Total Attribute Count:        %s\n" % total_attribute_count)
                    output_file.write("Unique Attribute Count:       %s\n" % unique_attribute_count)
                    output_file.write("Unique Attribute Value Count: %s\n" % unique_attr_val_count)
                    output_file.write("\n-----------------------------------\n\n")
                    # Write any extra info from presets
                    if pub_name:
                        output_file.write("Publication:      %s\n" % pub_name)
                    output_file.write("Encoding:         %s\n" % encoding)
                    output_file.write("XSLT used:        %s\n" % xslt_path)
                    output_file.write("XML Folder Path:  %s\n" % xml_folder_path)
                    edition_total = 0
                    if edition_list:
                        if ',' in edition_list:
                            output_file.write("Editions:\n")
                            for edition_name in edition_list.split(','):
                                output_file.write("    %s\n" % edition_name)
                                edition_total += 1
                        else:
                            output_file.write("Edition: %s\n" % editions_list)
                            edition_total += 1
                    output_file.write("\nTotal Edition Count: %s\n" % edition_total)
                    output_file.write("\n==========================\n\n")

                    output_file.write("\nAll Elements and Attributes (with possible values):\n\n")
                    # Iterate tag list and write sorted list with elements
                    index = 1
                    for element_item in sorted(tag_list):
                        # output_file.write("Tag: ")
                        output_file.write("%s. " % index)
                        output_file.write(element_item)
                        if tag_list[element_item] != '':
                            output_file.write("\n   -Attributes:\n")
                            attr_count = 1
                            for attr_item in sorted(tag_list[element_item]):
                                output_file.write("     (%s) " % attr_count)
                                output_file.write(attr_item)
                                output_file.write(" = ")
                                try:
                                    if tag_list[element_item][attr_item] == "":
                                        output_file.write('""')
                                    elif ',' in tag_list[element_item][attr_item]:
                                        val_count = 1
                                        for attr_val in sorted(tag_list[element_item][attr_item][1:-1].split(',')):
                                            output_file.write("\n         %s - " % val_count)
                                            if attr_val == "":
                                                output_file.write('""')
                                            else:
                                                output_file.write(attr_val)
                                            val_count += 1
                                    else:
                                        output_file.write(tag_list[element_item][attr_item][:-1])
                                except Exception as e:
                                    output_file.write("Error on element!\n")
                                    print("Error on element: %s" % e)
                                    continue
                                output_file.write("\n")
                                attr_count += 1
                        else:
                            output_file.write("\n   No Attributes Found!\n")
                        output_file.write("\n")
                        index += 1
            else:
                print("Supplied xslt file does not exist.")
        else:
            print("Supplied folder does not exist.")
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("Exception creating xml info file: %s - line %s" % (e, exc_traceback.tb_lineno))

def create_eversify_output(presets_path, output_file_path, xml_folder_path, use_xslt2, xslt_path, xslt2_path, pub_name, encoding):
    #Output of this will be a folder containing the article html results


    print("\n\nEVERSIFY OUTPUT --\npresets_path: %s\npub_name: %s\noutput_file_path: %s\nxml_folder_path: %s\nuse_xslt2: %s\nxslt_path: %s\nxslt2_path: %s\nencoding: %s\n\n" %
                      (presets_path, pub_name, output_file_path, xml_folder_path, use_xslt2, xslt_path, xslt2_path, encoding))

    is_pdf_replica = False
    is_hybrid = False
    archive_ext = ''
    zip_path = ''
    articlePath_endswith = ''
    article_ext = ''
    is_docx = False

    # Turn on extensions since we are creating a real output article
    use_ext = True
    save_first_result = True #TODO: add this to the parseable options

    #TODO: make presets processing its own function
    #TODO: Add code here to run 1 or 2 XSLTs on a set of article xml

    # Check for a presets file
    if os.path.exists(presets_path):
        try:
            with open(presets_path, 'r') as presets_file:
                for line in presets_file.readlines():
                    if "pub_name=" in line:
                        pub_name = line.split('pub_name=')[1].strip()
                    if "use_xslt2=" in line:
                        use_xslt2 = False
                        use_xslt2_str = line.split('use_xslt2=')[1].strip()
                        if use_xslt2_str.lower().strip() == 'true':
                            use_xslt2 = True
                    if "output_path=" in line:
                        output_file_path = normalize(line.split('output_path=')[1].strip(), True)
                    if "xml_folder_path=" in line:
                        xml_folder_path = normalize(line.split('xml_folder_path=')[1].strip(), False)
                    if "xslt_path=" in line:
                        xslt_path = normalize(line.split('xslt_path=')[1].strip(), False)
                    if "xslt2_path=" in line:
                        xslt2_path = normalize(line.split('xslt2_path=')[1].strip(), False)
                    if "encoding=" in line:
                        encoding = line.split('encoding=')[1].strip()
                    if "function=" in line:
                        funct = line.split('function=')[1].strip()

            if not xml_folder_path or not xslt_path or not encoding:
                print("\nSome required information was missing from the presets file. Please provide the following information:\n")

            if not encoding:
                encoding = input("From the General tab in the Archive Import Recipe, please copy and paste Encoding:\n")
            if not xslt_path:
                xslt_path = normalize(input("\nPlease enter the full path to the xslt file you would like to use:\n"), False)
            if use_xslt2 and not xslt2_path:
                xslt2_path = normalize(input("\nPlease enter the full path to the 2nd xslt file you would like to use:\n"), False)
            if not xml_folder_path:
                xml_folder_path = normalize(input("\nPlease enter the full path to the folder containing the xml files:\n"), False)
        except Exception as e:
            print("Exception loading presets: %s" % e)

        print("\n\npub_name: %s\noutput_file_path: %s\nxml_folder_path: %s\nuse_xslt2: %s\nxslt_path: %s\nxslt2_path: %s\nencoding: %s\n\n" %
                      (pub_name, output_file_path, xml_folder_path, use_xslt2, xslt_path, xslt2_path, encoding))

    try:
        if os.path.exists(xml_folder_path):
            if os.path.exists(xslt_path):
                # Begin task
                print("\nThank you. Please wait while I generate your output article files...\n\n-----------------------------\n")
                xml_set = XMLProcesser()

                if encoding != '':
                    xml_set.encoding = encoding
                if archive_ext != '':
                    xml_set.archive_ext = archive_ext
                # if zip_path != '':
                #     xml_set.zip_path = zip_path
                if articlePath_endswith != '':
                    xml_set.articlePath_endswith = articlePath_endswith
                if article_ext != '':
                    xml_set.article_ext = article_ext

                if xslt_path != '':
                    xml_set.xslt_path = xslt_path
                if is_docx:
                    xml_set.is_docx = is_docx

                # Get XSLT data from file
                xslt_data = ''
                with open(xslt_path, 'r') as xslt_file:
                    xslt_data = xslt_file.read()

                xslt2_data = ''
                if use_xslt2:
                    if os.path.exists(xslt2_path):
                        with open(xslt2_path, 'r') as xslt2_file:
                            xslt2_data = xslt2_file.read()
                    else:
                        print("\nWARNING: 2nd XSLT file '%s' is missing. Resulting article will be from only the first transformation.\n" % xslt2_path)

                # Variables for later
                total_articles_count = 0
                successful_transforms_count = 0
                successful_files_count = 0

                failed_files_count = 0
                failed_files_list = []

                # Generate name for folder to hold results
                if not output_file_path:
                    output_file_path = xml_folder_path + "_results"

                # If the folder doesn't exist, create it
                if not os.path.exists(output_file_path):
                    os.mkdir(output_file_path)

                # Run through file list and create output
                for xml_file in os.listdir(xml_folder_path):
                    if xml_file.endswith(xml_set.article_ext):
                        total_articles_count += 1
                        full_path = os.path.join(xml_folder_path, xml_file)
                        article_dom = xml_set.process_xml(full_path, xslt_data, xslt2_data, use_ext, use_xslt2, save_first_result)
                        # article_html = innerHtml(article_dom)
                        article_html = str(article_dom)

                        if article_html:
                            successful_transforms_count += 1

                            # Generate name for folder to hold results
                            output_xml_path = os.path.join(output_file_path, "transformed_" + xml_file)

                            # Remove existing output files with the same name
                            if os.path.exists(output_xml_path):
                                os.remove(output_xml_path)

                            print("writing file: %s" % output_xml_path)####
                            # Write output file
                            with codecs.open(output_xml_path, 'w', 'utf-8') as output_file:
                            # with open(output_xml_path, 'w', encoding="utf-8") as output_file:
                                output_file.write(str(article_html))
                                # article_dom.write(output_file, encoding="utf-8", method="xml", pretty_print=True)
                                successful_files_count += 1
                            print("Wrote file: %s" % output_xml_path)####

                        else:
                            failed_files_count += 1
                            failed_files_list.append(xml_file)
                            print("Error: file '%s' article_html returned as '%s'" % (xml_file, article_html))
            else:
                print("Supplied xslt path does not exist: %s" % xslt_path)
                sys.exit()
        else:
            print("Supplied xml folder does not exist: %s" % xml_folder_path)
            sys.exit()
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("Exception creating xml output file: %s - line %s" % (e, exc_traceback.tb_lineno))

def validate_eversify_output(output_article, output_file_path, recipe, ):
    #TODO: make recipe reading and processing its own function
    #TODO: Add code here to validate the parse rules from the recipe

    #This function will require create_eversify_output to run first
    #Output of this will be a file listing the results of each parse rule
    print("Validating parse recipes...")


def main(argv):
    #TODO: add ability to read recipes exported from eversify
    #TODO: add option to select which operation to run --> eversify output, eversify output and xpath validation, or element list
    # Load presets
    print("Attempting to load presets...")
    xml_folder_path = ''
    xslt_path = ''
    use_xslt2 = False
    xslt2_path = ''
    pub_name = ''
    encoding = ''
    presets_path = ''
    output_path = ''
    funct = 'info'

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
                      '-i, --ifile    - Path to the input folder containing XMLs\n'
                      '-o, --ofile    - Path for the ouputfile\n'
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

print("\n-----------------------------\n\nFinished!")
sys.exit()