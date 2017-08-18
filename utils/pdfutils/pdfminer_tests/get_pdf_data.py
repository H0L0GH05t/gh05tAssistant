from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.converter import TextConverter, PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTChar
import simplejson

def get_data():
    print("START")
    # pdf_path = "auto_link-tester_doc-01.pdf"
    # pdf_path = "link_page.pdf"
    # pdf_path = "cpd_edition.pdf"
    # pdf_path = "2015-03-17_SRV_1502_EN_04_Mailbag.pdf"
    pdf_path = "2015-03-17_SRV_1502_EN_28_news.admin.ch.pdf"

    print('PDF: %s' % pdf_path)

    # Extract clickable coordinates and url
    pdf_data = []


    #Set up parser and document
    openpdf = open(pdf_path, 'rb')
    parser = PDFParser(openpdf)
    document = PDFDocument()

    #Set parser to document and initialize
    parser.set_document(document)
    document.set_parser(parser)
    document.initialize('')

    #Create a PDF resource manager object that stores shared resources
    rsrcmgr = PDFResourceManager()
    #set parameters for analysis
    laparams = LAParams()

    #Create PDF device interpreter objects
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    print("start iterating pages")
    #Process each page
    index = 0
    for page in document.get_pages():
        print("----Page-----")
        interpreter.process_page(page)

        #check for existing link objects
        uri_objs = []
        if page.annots:
            obj = page.annots
            test_obj = page.contents
            if not isinstance(obj, list):
                obj = obj.resolve()
            if isinstance(obj, list):
                for v in obj:
                    uri = ''
                    coords = []
                    objref = v.resolve()
                    # print("\nobjref: %s\n\n" % objref)
                    if str(objref['Subtype']) == '/Link' and 'A' in objref:
                        if type((objref['A'])) == dict:
                            uri = objref['A']['URI']
                            coords = objref['Rect']
                            uri_objs.append(objref['A']['URI'])
                        else:
                            uri_obj = objref['A'].resolve()
                            print("===\nobjref['A']: %s\n" % uri_obj)
                            if 'URI' in uri_obj:
                                uri = uri_obj['URI']
                                coords = objref['Rect']
                                uri_objs.append(uri_obj['URI'])
                            elif 'F' in uri_obj:
                                print("----> No 'URI' found for link obj: \n%s\n" % objref)
                                if uri_obj['F'] == dict:
                                    print("F is dict: %s" % uri_obj['F'])
                                else:
                                    gotor_obj = uri_obj['F'].resolve()
                                    print("Resolved gotor_obj: %s" % gotor_obj)

                        #print("\nuri: %s -- pg id (%s) -- attrs: %s " % (uri, page.pageid, page.attrs))
                        pdf_data.append({"page_number":page.pageid,
                                         "coordinates":coords,
                                         "url":uri})

                    elif str(objref['Subtype']) == '/Link':
                        print("\n---->> No 'A' found for link: %s\n" % objref)

    pdf_data_json = simplejson.dumps(pdf_data)

try:
    get_data()
except Exception as e:
    print("FAILED: %s" % e)

print("---------END---------")