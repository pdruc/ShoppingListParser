import configparser

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

cnf = configparser.ConfigParser()
cnf.read('configuration.cfg')

COL_TEXT_BLOCK_NUM = cnf.get('namespace', 'col_text_block_num')
COL_TEXT_LINE_OBJ = cnf.get('namespace', 'col_text_line_obj')
COL_TEXT_LINE = cnf.get('namespace', 'col_text_line')
COL_TEXT_LINE_CENTER_X = cnf.get('namespace', 'col_text_line_center_x')
COL_TEXT_LINE_CENTER_Y = cnf.get('namespace', 'col_text_line_center_y')
COL_TEXT_LINE_HEIGHT = cnf.get('namespace', 'col_text_line_height')
COL_TEXT_LINE_WIDTH = cnf.get('namespace', 'col_text_line_width')
COL_X0 = cnf.get('namespace', 'col_x0')
COL_X1 = cnf.get('namespace', 'col_x1')
COL_Y0 = cnf.get('namespace', 'col_y0')
COL_Y1 = cnf.get('namespace', 'col_y1')


class DataExtracotr:
    attributes_to_keep = ['x0', 'y0', 'x1', 'y1', 'width', 'height']
    attributes_to_keep_renamed = [COL_X0, COL_Y0,  COL_X1, COL_Y1, COL_TEXT_LINE_WIDTH, COL_TEXT_LINE_HEIGHT]

    def __init__(self, path_pdf):
        self.path_pdf = path_pdf
        self.layout = None
        self.textline_obj = None
        self.textline_str = None
        self.content = None

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

        return pd.DataFrame(textlines, columns=[COL_TEXT_BLOCK_NUM, COL_TEXT_LINE_OBJ])

    def _extract_textlines_str(self):
        return [obj.get_text().encode('utf-8').replace('\xc2\xa0', ' ') for obj in self.textline_obj['b']]

    def _decompose_texlines(self):
        # Attributes concerning position - original ones
        df = pd.DataFrame([{k: textline.__dict__[k] for k in self.attributes_to_keep}
                           for textline in self.textline_obj[COL_TEXT_LINE_OBJ]])
        df.columns = self.attributes_to_keep_renamed

        # Attributes concerning position - derivate
        df[COL_TEXT_LINE_CENTER_X] = df[[COL_X0, COL_X1]].mean(axis=1)
        df[COL_TEXT_LINE_CENTER_Y] = df[[COL_Y0, COL_Y1]].mean(axis=1)

        # Attributes concerning text
        df[COL_TEXT_BLOCK_NUM] = self.textline_obj[COL_TEXT_BLOCK_NUM]
        df[COL_TEXT_LINE] = [obj.get_text().replace('\t', ' ').rstrip() for obj in self.textline_obj[COL_TEXT_LINE_OBJ]]

        return df

    def run(self):
        if __name__ == '__main__':
            self.layout = self._extract_layout()
            self.textline_obj = self._extract_textlines_obj()
            self.content = self._decompose_texlines()

    def draw_boxes(self):
        pass


if __name__ == '__main__':
    data_extractor = DataExtracotr('data/lista_zakupow.pdf')
    data_extractor.run()
    print()