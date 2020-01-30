import pdfminer
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

import pandas as pd


class DataExtracotr:
    def __init__(self, path_pdf):
        self.path_pdf = path_pdf
        self.layout = None
        self.textline_obj = None

    def _extract_layout(self):
        pdf_file = open(self.path_pdf, 'rb')
        pdf_parser = PDFParser(pdf_file)
        document = PDFDocument(pdf_parser)
        if not document.is_extractable:
            raise PDFTextExtractionNotAllowed

        resource_manager = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(resource_manager, laparams=laparams)
        interpreter = PDFPageInterpreter(resource_manager, device)

        for page in PDFPage.create_pages(document):
            interpreter.process_page(page)
            return device.get_result()

    def _extract_textlines_obj(self):
        textlines = []
        for i, obj in enumerate(self.layout._objs):
            if isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
                for sub_obj in obj:
                    if isinstance(sub_obj, pdfminer.layout.LTTextLine):
                        textlines.append([i, sub_obj])

        return pd.DataFrame(textlines, columns=['a','b'])

    def run(self):
        if __name__ == '__main__':
            self.layout = self._extract_layout()
            self.textline_obj = self._extract_textlines_obj()


if __name__ == '__main__':
    data_extractor = DataExtracotr('data/lista_zakupow.pdf')
    data_extractor.run()
    print()