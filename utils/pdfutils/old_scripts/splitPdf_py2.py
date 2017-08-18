from PyPDF2 import PdfFileWriter, PdfFileReader
import sys, os

pdf_path = input('Enter full pdf path in quotes with / isntead of \: ')
num_of_sections = int(input('Enter number of sections: '))
sections = []

i = 0
for i in xrange(i, num_of_sections):
    sections.append(input('Enter name of section %s in quotes: ' % int(i+1)))
    i += 1

#pdf_path = "de.PDF"
input_path = PdfFileReader(file(pdf_path, "rb"), strict=False)
#num_of_sections = 12
#sections = ["Layout (Mantel)",
#"Inhalt",
#"Gelesen",
#"Gesehen",
#"Schwerpunkt",
#"Politik",
#"Literatur",
#"Kultur",
#"Sport",
#"Auslandschweizer-Organisation",
#"Aus dem Bundeshaus",
#"Echo"]


for section in sections:
    startpg = int(input('Enter the start page for %s: ' % section))
    endpg = int(input('Enter the end page for %s: ' % section))
    output = PdfFileWriter()
    for x in xrange(startpg-1, endpg):
        output.addPage(input_path.getPage(x))
    output_path = '%s_%s.pdf' % (section, startpg)
    output_stream = file(os.path.join('sections',output_path), "wb")
    output.write(output_stream)
    print "split %s" % (output_path)
    output_stream.close()

print "Done splitting %s" % (pdf_path)