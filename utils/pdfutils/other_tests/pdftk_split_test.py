import os, sys, traceback
import re, datetime
import subprocess
import tempfile
import shutil
import zipfile

from django.utils.encoding import smart_text

#pdf_library_available = False
#try:
#    sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '../..'))
#    import pypdftk
#    from pypdftk import get_num_pages, split
#    pdf_library_available = True
#except Exception as e:
#    print('Could not import library: %s' % e)
#    sys.exit()
        
#start at page 1
#original_file_name = 'Weidwerk_05-2015_1.pdf'
#start at page 4
#original_file_name = 'Weidwerk_05-2015_4.pdf'
#file_type = 'pdf'
#zip starting at page 1
#original_file_name = 'test_zip1.zip'
#file_path = 'Weidwerk_05-2015_1.pdf'
file_type = 'zip'
#zip starting at page 4
original_file_name = 'test_zip4.zip'
file_path = 'Weidwerk_05-2015_4.pdf'


parse_rule = '(?i)(?P<publication_name>.*)_(?P<publication_date_month>\\d{2,2})-(?P<publication_date_year>\\d{4,4})_(?P<page_number>\\d\\d).pdf'
first_section = 'TITEL'

pdf_file_pattern = '(?i)(?P<file_name>.*?).pdf'
re_pdf = re.compile(pdf_file_pattern)

def is_numeric(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def get_page_range(matchdict, parse_name):
    result = 0
    if matchdict and parse_name:
        value = matchdict.get(parse_name, None)
        if value is not None and is_numeric(value):
            result = int(value)
        if value is not None and not is_numeric(value):
            if "-" in value: first_page, last_page = value.split('-')
            else: first_page = value
            if is_numeric(first_page): result = int(first_page)
            else: result = 0
    return result
    
def check_for_multiple_page_pdf(file_path, file_name):
        try:
            #create a folder with the name of the original file and a datetime stamp for split pdf files
            date_stamp = str(datetime.datetime.now())
            date_stamp = ''.join( c for c in date_stamp if c not in '-.:')
            date_stamp = date_stamp.replace(' ', '_')
            date_stamp = date_stamp[0:13]
            extract_path = os.path.dirname(os.path.abspath(file_path))
            original_basename = original_file_name.replace('.zip', '')
            original_basename = original_basename.replace('.tar', '')
            original_basename = original_basename.replace('.pdf', '')
            extract_path = os.path.join(extract_path, original_basename + '_split_pdfs_' + date_stamp)
            basename, extension = os.path.splitext(file_name)
            
            if file_type == 'pdf':
                print("Confirmed pdf running cmd...")
                check_pages_cmd = "pdftk %s dump_data" % file_name
                process = subprocess.Popen(check_pages_cmd, shell=True, stdout=subprocess.PIPE, )
                output, unused_err = process.communicate()
                output_test = output.decode('utf-8').split('\n')
                got_page_count = False
                for line in output_test:
                    if not isinstance(line, int) and line.lower().startswith('numberofpages'):
                        number_of_pages = int(line.split(':')[1])
                        got_page_count = True
                        print("Pdf has %s pages. Returning..." % number_of_pages)
                if not got_page_count:
                    print("The NumberOfPages dumpdata could not be found in pdf %s. It will process only the first page." % )
                    number_of_pages = 1
                return number_of_pages, extract_path
            else:
                #the file is in a zip and needs to be extracted first before it can be checked for page count
                if extension.lower() == '.pdf':
                    dir_path, filename = os.path.split(file_name)
                    original_path = os.path.join(extract_path, 'original')
                    
                    if not isinstance(filename, str):
                        try:
                            str(filename, "ascii")
                        except UnicodeError:
                            try:
                                str(filename, "utf-8")
                            except UnicodeError:
                                filename = filename.decode("cp437")
                            else:
                                pass
                        else:
                            # value was valid ASCII data
                            pass
                    #temporary fix to strip out difficult characters from file names
                    #filename = unicode(filename, errors='replace')
                    
                    if not os.path.exists(original_path): os.makedirs(original_path, 0o777)
                    write_path = os.path.join(original_path, filename)
                    with open(write_path, 'wb') as f:
                        f.write(archive_file.read(file_name))
                    
                    pdf_path = os.path.join(original_path, filename)
                    print("Confirmed zip running cmd on %s..." % file_name)
                    check_pages_cmd = "pdftk %s dump_data" % file_name
                    process = subprocess.Popen(check_pages_cmd, shell=True, stdout=subprocess.PIPE, )
                    output, unused_err = process.communicate()
                    output_test = output.decode('utf-8').split('\n')
                    for line in output_test:
                        if not isinstance(line, int) and line.lower().startswith('numberofpages'):
                            number_of_pages = int(line.split(':')[1])
                            print("Pdf has %s pages. Returning..." % number_of_pages)
                    return number_of_pages, pdf_path, extract_path, extension
                else:
                    #file is not a pdf
                    if not isinstance(file_name, str):
                        try:
                            str(file_name, "ascii")
                        except UnicodeError:
                            try:
                                str(file_name, "utf-8")
                            except UnicodeError:
                                file_name = file_name.decode("cp437")
                            else:
                                pass
                        else:
                            # value was valid ASCII data
                            pass
                    pdf_path = os.path.join(extract_path, file_name)
                    return 0, pdf_path, extract_path, extension
            
        except Exception as e:
                #print('')
                #try:
                    #import traceback, 'at line %s',
                exc_type, exc_value, exc_traceback = sys.exc_info()
                line = exc_traceback.tb_lineno
                print('Unable to check PDF for multiple pages, exception at line %s: %s' % (line, e))
                print('--------------------\n\n\n')
                #except Exception:
                #    print('Unable to check PDF for multiple pages: %s' % e)

def split_multiple_page_pdf(number_of_pages, file_path, original_name, split_path):
        try:
            #name the new file using the same name pattern as the original file
            dir_path, filename = os.path.split(original_name)
            base, ext = os.path.splitext(filename)
            if len(parse_rule):
                if not isinstance(filename, str):
                    try:
                        str(filename, "ascii")
                    except UnicodeError:
                        try:
                            str(filename, "utf-8")
                        except UnicodeError:
                            filename = filename.decode("cp437")
                            filename = filename.encode("utf-8")
                        else:
                            pass
                    else:
                        # value was valid ASCII data
                        pass
                unicode_filename = smart_text(filename, 'utf-8')
                new_file_name = parse_rule
                #allow for page_number to be something other than a number by swapping '\d' for '.*?'
                check = ''.join(i for i in ('<page_number>\\d\\d)','<page_number>\\d*','<page_number>\\d\\d\\d)', '<page_name>\\d\\d?', '<page_name>\\d\\d\\d\\d') if i in new_file_name)
                if check:
                    if ')' in check: check = check.replace(')', '')
                    new_file_name = new_file_name.replace(check, '<page_number>.*?')
                    if "??" in new_file_name: new_file_name =  new_file_name.replace("??", '?')
                #compensate for if pub year is not named
                if "\\d\\d\\d\\d" in new_file_name:
                    new_file_name = new_file_name.replace("\\d\\d\\d\\d", '(?P<publication_date_year>\\d{4,4})')
                if "?_\\" in new_file_name:
                    new_file_name = new_file_name.replace("?_\\","?\\")
                if "*.pdf" in new_file_name:
                    new_file_name = new_file_name.replace("*.pdf", ".pdf")
                    
                try:
                    print("\nMatching: \n%s\n%s\n" % (new_file_name,unicode_filename))
                    m = re.match(new_file_name, unicode_filename)
                except Exception as e:
                    print('Error matching parse name for %s: %s' % (unicode_filename, e))
                    m = None
                if m is not None:
                    matchdict = m.groupdict()
                    #new_file_name = parse_rule
                    
                    #check for the what page number to start numbering by
                    page_num = get_page_range(matchdict, 'page_number')
                    page_name = get_page_range(matchdict, 'page_name')
                    page_num1 = get_page_range(matchdict, 'page_number1')
                    page_num2 = get_page_range(matchdict, 'page_number2')
                    page_selector = get_page_range(matchdict, 'page_selector')
                    if page_selector == 1 and page_num1 > 0:
                        starting_page_number = str(page_num1)
                    elif page_selector == 2 and page_num2 > 0:
                        starting_page_number = str(page_num2)
                    elif page_num > 0:
                        starting_page_number = str(page_num)
                    elif page_name > 0:
                        starting_page_number = str(page_name)
                    else:
                        starting_page_number = '1'
                        
                    #make a string template using the parse_rule
                    new_file_name = new_file_name.replace("(?i)", '')
                    new_file_name = new_file_name.replace("\\d", '')
                    new_file_name = new_file_name.replace("\\w", '')
                    new_file_name = new_file_name.replace("?P", '')
                    new_file_name = new_file_name.replace(".*?", '')
                    new_file_name = new_file_name.replace(".*", '')
                    new_file_name = new_file_name.replace(".)", '')
                    new_file_name = new_file_name.replace("*?", '')
                    new_file_name = new_file_name.replace(".pdf", '')
                    new_file_name = ''.join( c for c in new_file_name if  c not in '?()<>*{},1234567890\\' )
                    
                    #TODO: make the parsing rules into a dictionary to use to replace info in the new_file_name template
                    #find the parsing name from the original file name
                    main_section = matchdict.get('main_section', '')
                    section_name = matchdict.get('section_name', '')
                    page_name = matchdict.get('page_name', 'pageName')
                    edition_name = matchdict.get('edition_name', 'editionName')
                    publication_name = matchdict.get('publication_name', 'pubName')
                    publisher_name = matchdict.get('publisher_name', 'publisherName')
                    pub_abrv = matchdict.get('pub_abrv', 'pub_abrv')
                    other_stuff = matchdict.get('other_stuff', 'otherStuff')
                    other_stuff1 = matchdict.get('other_stuff1', 'otherStuff1')
                    other_stuff2 = matchdict.get('other_stuff2', 'otherStuff2')
                    publication_date_year = matchdict.get('publication_date_year', '0000')
                    publication_date_month = matchdict.get('publication_date_month', '00')
                    publication_date_day = matchdict.get('publication_date_day', '00')
                    
                    #check to see if there's a required number of digits for the page number and add zeros where needed
                    parse_list = ('<page_number>\\d*', '<page_number>\\d?',
                                  '<page_number>\\d\\d)','<page_name>\\d\\d?',
                                  '<page_number>\\d\\d\\d)', '<page_number>\\d\\d\\d?',
                                  '<page_name>\\d\\d\\d\\d')
                    add_zeros = ''.join(i for i in parse_list if i in parse_rule)
                    if add_zeros:
                        zeros_to_add = add_zeros.count("\\d")
                        page_number = '%0' + str(zeros_to_add) + 'd'
                        
                    #replace the sections in the template
                    new_file_name = new_file_name.replace('page_number', page_number)
                    new_file_name = new_file_name.replace('page_name', page_number)
                    new_file_name = new_file_name.replace('section_name', section_name)
                    new_file_name = new_file_name.replace('main_section', main_section)
                    new_file_name = new_file_name.replace('page_name', page_name)
                    new_file_name = new_file_name.replace('edition_name', edition_name)
                    new_file_name = new_file_name.replace('publication_name', publication_name)
                    new_file_name = new_file_name.replace('publisher_name', publisher_name)
                    new_file_name = new_file_name.replace('pub_abrv', pub_abrv)
                    new_file_name = new_file_name.replace('other_stuff', other_stuff)
                    new_file_name = new_file_name.replace('other_stuff1', other_stuff1)
                    new_file_name = new_file_name.replace('other_stuff2', other_stuff2)
                    new_file_name = new_file_name.replace('publication_date_year', publication_date_year)
                    new_file_name = new_file_name.replace('publication_date_month', publication_date_month)
                    new_file_name = new_file_name.replace('publication_date_day', publication_date_day)
                    
                    #replaces leading '.' caused by parsing rule with leading wildcard
                    if new_file_name[0] == '.':
                        new_file_name = new_file_name.lstrip('.')
                    
                    #write the new one page pdf file to the same directory as the original
                    new_file_path = os.path.join(split_path, new_file_name)
                    if os.path.exists(new_file_path + ext):
                        new_file_path = new_file_path + '-%d' #safety in case it tries to override a file
                else:
                    #the parsing name doesn't match or is missing a piece, so default to original name + index
                    print('Could not match file name to parsing rule')
                    
                    new_file_path = os.path.join(split_path, base) + '_%d'
                    if os.path.exists(new_file_path + ext):
                        new_file_path = new_file_path + '-%d' #safety in case it tries to override a file
            else:
                print('Could not find parsing rule')
                #file_dirname = os.path.dirname(os.path.abspath(file_path))
                new_file_path =  os.path.join(split_path, base) + '_%d'
                if os.path.exists(new_file_path + ext):
                    new_file_path = new_file_path + '-%d' #safety in case it tries to override a file
            
            new_file_path = new_file_path + ".pdf"

            split_cmd = 'pdftk %s burst output %s' %(file_path, new_file_path)
            process = subprocess.Popen(split_cmd, shell=True, stdout=subprocess.PIPE, )
            output, unused_err = process.communicate()
                
            new_paths = []
            for page in range(number_of_pages, 0, -1):
                new_page_number = str(page)
                if add_zeros:
                    zeros_to_add = add_zeros.count("\\d")
                    if int(page) > 9 and int(page) < 99:
                        zeros_to_add = zeros_to_add - 1
                    elif int(page) > 99 and int(page) < 999:
                        zeros_to_add = zeros_to_add - 2
                    elif int(page) > 999 and int(page) < 9999:
                        zeros_to_add = zeros_to_add - 3
                    elif int(page) > 9999 and int(page) < 99999:
                        zeros_to_add = zeros_to_add - 4
                    if zeros_to_add > 0:
                        for zero in range(1, zeros_to_add):
                            new_page_number = '0' + str(page)
                path = new_file_path.replace(page_number, new_page_number)
                print("****PATH: %s ----- PAGE: %s"%(path,page))####
                if int(starting_page_number) > 1:
                    print("STARTING PAGE: %s\n" % starting_page_number)
                    new_page_number = str(page+int(starting_page_number))
                    if add_zeros:
                        zeros_to_add = add_zeros.count("\\d")
                        if int(page) > 9 and int(page) < 99:
                            zeros_to_add = zeros_to_add - 1
                        elif int(page) > 99 and int(page) < 999:
                            zeros_to_add = zeros_to_add - 2
                        elif int(page) > 999 and int(page) < 9999:
                            zeros_to_add = zeros_to_add - 3
                        elif int(page) > 9999 and int(page) < 99999:
                            zeros_to_add = zeros_to_add - 4
                        if zeros_to_add > 0:
                            for zero in range(1, zeros_to_add):
                                new_page_number = '0' + str(page + int(starting_page_number))
                    fixed_new_path = new_file_path.replace(page_number, new_page_number)
                    os.rename(path, fixed_new_path)
                new_paths.append(path)

            return new_paths
        except Exception as e:
            print('')
            try:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print('Unable to split PDF pages, exception: %s at line %s' % (e, exc_traceback.tb_lineno) )
            except Exception:
                print('Unable to split PDF pages')

##############################################                

if original_file_name.startswith('.'):
    #file is not valid pdf or archive
    print("File is not valid")
elif file_type == 'pdf':
    print("File is PDF. Moving on to check page numbers...")
    number_of_pages, split_path = check_for_multiple_page_pdf(file_path, original_file_name)
    extract_path = split_path
    if number_of_pages > 1:
        if not os.path.exists(split_path): os.makedirs(split_path, 0o777)
        print("Entering split pages for %s with %s pages" % (file_path, number_of_pages))
        new_paths = split_multiple_page_pdf(number_of_pages, file_path, original_file_name, split_path)
        for new_path in new_paths:
            print("The new pdf path is %s and would move on to processing next."%new_path)
    else:
        print("The file %s did not need splitting and would move on to processing next."% original_file_name)
else:
    archive_file = zipfile.ZipFile(original_file_name)
    for index, file_in_zip in enumerate(archive_file.namelist()):
        if os.path.basename(file_in_zip).startswith('.'):
            #file is not valid pdf or archive
            continue
        if file_in_zip.endswith('.pdf'):
            number_of_pages, pdf_path, extract_path, extension = check_for_multiple_page_pdf(file_path, file_in_zip)
            if number_of_pages > 1 and extension.lower() == '.pdf':
                new_paths = split_multiple_page_pdf(number_of_pages, pdf_path, file_in_zip, extract_path)
                for new_path in new_paths:
                    print("The new pdf path is %s and would move on to processing next."% new_path)
                if os.path.exists(pdf_path): 
                    os.remove(pdf_path)
            else:
                #delete the extracted file if it exists and use the one in the zip instead
                if os.path.exists(pdf_path): 
                    os.remove(pdf_path)
                if extension.lower() == '.pdf': 
                    print("The file %s in the zip did not need splitting and would move on to processing next."% file_in_zip)
try:
    #remove the empty directories leftover
    extract_path = os.path.dirname(os.path.abspath(extract_path))
    if os.path.exists(extract_path) and os.listdir(extract_path):
        for root, dirs, files in os.walk(extract_path,topdown=False):
            for name in dirs:
                    fname = os.path.join(root,name)
                    if not os.listdir(fname):
                        os.rmdir(fname)
        if os.path.exists(extract_path) and not os.listdir(extract_path):
            os.removedirs(extract_path)
except Exception as e:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    print("FAILED at line %s: "%(exc_traceback.tb_lineno, e))
