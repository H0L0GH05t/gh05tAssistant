from PyPDF2 import PdfFileMerger, PdfFileReader

startpg = 4
endpg = 30
num_of_zeros = 2

add_zeros = 0
#out_name_template = '%s-%s.pdf' % (startpg, endpg)
out_name_template = 'AAR_report_LTS_00%s.pdf' % startpg

merger = PdfFileMerger()
i = 0
for page in xrange(startpg, endpg+1):
    if page > 9 and page < 99:
        add_zeros = num_of_zeros - 1
    elif page > 99 and page < 999:
        add_zeros = num_of_zeros - 2
    elif page > 999 and page < 9999:
        add_zeros = num_of_zeros - 3
    else:
        add_zeros = num_of_zeros
        
    if num_of_zeros > 0:
        zeros = ''
        for zero in xrange(0,add_zeros):
            zeros = zeros + '0'
  
    filename = 'AAR_report_LTS_%s%s.pdf' % (zeros, page)
    merger.append(PdfFileReader(file(filename, 'rb')))
    i += 1
    
new_name = out_name_template
new_name = "multi-page\\" + new_name
merger.write(new_name)
print "Done making: %s  with %s pages" % (new_name, i)