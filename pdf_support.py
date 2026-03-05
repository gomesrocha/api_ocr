import PyPDF2

class PDFExtractor:
    def __init__(self, pdf_file):
        self.pdf_file = pdf_file

    def extract_text(self):
        try:
            with open(self.pdf_file, 'rb') as file:
                reader = PyPDF2.PdfFileReader(file)
                if reader.isEncrypted:
                    reader.decrypt('')
                text = ''\n'.join([reader.getPage(i).extractText() for i in range(reader.numPages)])
            return text
        except Exception as e:
            return str(e)

# Example usage:
# extractor = PDFExtractor('document.pdf')
# print(extractor.extract_text())