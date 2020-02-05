
import pytesseract
from pdf2image import convert_from_path
from pdfminer.pdfparser import  PDFParser,PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal,LAParams
from pdfminer.pdfinterp import PDFTextExtractionNotAllowed
import logging
import os
import sys

from PyQt5 import QtCore,QtGui
from PyQt5.QtCore import  QEventLoop, QTimer
from PyQt5.QtWidgets import QMainWindow, QPushButton, \
    QApplication,QComboBox,QLabel,QLineEdit,QPlainTextEdit
import threading

# logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# # logging.getLogger("elasticsearch").setLevel(logging.ERROR)
# logging.getLogger("pdfminer").setLevel(logging.ERROR)
# logging.getLogger("root").setLevel(logging.ERROR)
# logger=logging.getLogger("logger")

#
# def read_pdf(path):
#     fp = open(path, 'rb')
#     # 用文件对象创建一个PDF文档分析器
#     parser = PDFParser(fp)
#     # 创建一个PDF文档
#     doc = PDFDocument()
#     # 连接分析器，与文档对象
#     parser.set_document(doc)
#     doc.set_parser(parser)
#
#     # 提供初始化密码，如果没有密码，就创建一个空的字符串
#     doc.initialize()
#
#     # 检测文档是否提供txt转换，不提供就忽略
#     if not doc.is_extractable:
#         raise PDFTextExtractionNotAllowed
#     else:
#         # 创建PDF，资源管理器，来共享资源
#         rsrcmgr = PDFResourceManager()
#         # 创建一个PDF设备对象
#         laparams = LAParams()
#         device = PDFPageAggregator(rsrcmgr, laparams=laparams)
#         # 创建一个PDF解释其对象
#         interpreter = PDFPageInterpreter(rsrcmgr, device)
#
#         text = ""
#         # 循环遍历列表，每次处理一个page内容
#         # doc.get_pages() 获取page列表
#         for page in doc.get_pages():
#             interpreter.process_page(page)
#             # 接受该页面的LTPage对象
#             layout = device.get_result()
#             # 这里layout是一个LTPage对象 里面存放着 这个page解析出的各种对象
#             # 一般包括LTTextBox, LTFigure, LTImage, LTTextBoxHorizontal 等等
#             # 想要获取文本就获得对象的text属性，
#             for x in layout:
#                 if (isinstance(x, LTTextBoxHorizontal)):
#                     results = x.get_text()
#
#                     text += results + "\n"
#         return text


class Example(QMainWindow):

    def __init__(self):
        super().__init__()

        self.use_ocr="False"
        self.initUI()
        #
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            stream=sys.stdout)
        logging.root.setLevel(logging.ERROR)
        logging.getLogger("pdfminer").setLevel(logging.ERROR)
        logging.getLogger("Ilogger").setLevel(logging.INFO)
        self.logger = logging.getLogger("Ilogger")
        #



    def initUI(self):
        sys.stdout = EmittingStr(textWritten=self.outputWritten)
        sys.stderr = EmittingStr(textWritten=self.outputWritten)
        lbl = QLabel("PDF文件夹路径:", self)
        lbl.resize(200,30)
        lbl.move(50,50)

        self.pdf_path = QLineEdit(self)
        self.pdf_path.resize(200, 30)
        self.pdf_path.move(50, 85)

        lb2= QLabel("TXT文件夹路径:", self)
        lb2.resize(200,30)
        lb2.move(50,135)

        self.txt_path = QLineEdit(self)
        self.txt_path.resize(200, 30)
        self.txt_path.move(50, 170)

        lb3 = QLabel("使用OCR识别：", self)
        lb3.move(50, 220)


        ocr=QComboBox(self)
        ocr.addItems(["True","False"])
        ocr.setCurrentIndex(1)
        ocr.move(50,255)

        ocr.activated[str].connect(self.ocr_change)

        btn2 = QPushButton("启动", self)
        btn2.move(50, 320)

        btn2.clicked.connect(self.buttonClicked)

        self.textBrowser=QPlainTextEdit(self)
        self.textBrowser.move(50,370)
        self.textBrowser.resize(400,200)

        self.setGeometry(300, 300, 500, 600)
        self.setWindowTitle('PDF转TXT工具')
        self.show()

    def outputWritten(self, text):
        cursor = self.textBrowser.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.textBrowser.setTextCursor(cursor)
        self.textBrowser.ensureCursorVisible()

    def buttonClicked(self):
        # print(self.use_ocr)
        o= self.use_ocr==str(True)
        # print("--------")
        path=os.path.join(os.path.abspath("."),"temp_png")
        if not os.path.exists( path):
            os.mkdir(path)


        if not os.path.exists( self.pdf_path.text()):
            self.logger.error("PDF路径不正确！")
            return
        if not os.path.exists( self.txt_path.text()):
            self.logger.error("TXT路径不正确！")
            return

        # run(pdf_dir=self.pdf_path.text(),txt_dir=self.txt_path.text(),ocr=o,temp_dir=path)
        r=Run_thread(self.logger,pdf_dir=self.pdf_path.text(),txt_dir=self.txt_path.text(),ocr=o,temp_dir=path)
        r.setDaemon(True)
        r.start()



    def ocr_change(self, text):
        self.use_ocr=text

class EmittingStr(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)  # 定义一个发送str的信号

    def write(self, text):
        self.textWritten.emit(str(text))
        loop = QEventLoop()
        QTimer.singleShot(10, loop.quit)
        loop.exec_()

class Run_thread(threading.Thread):
    def __init__(self,logger,
                 pdf_dir=r"C:\pdfs\jx0927",
                 txt_dir="C:\pdfs\jx0927_txt",
                 ocr=False,
                 temp_dir="C:/temp/png"):

        super().__init__()

        self.pdf_dir=pdf_dir
        self.txt_dir=txt_dir
        self.ocr=ocr
        self.temp_dir=temp_dir
        self.logger=logger



    def run(self):
        if not os.path.exists(self.pdf_dir):
            raise ValueError("pdf目录有误...")
        if not os.path.exists(self.txt_dir):
            os.mkdir(self.txt_dir)
        # print("-----------")
        for i in os.listdir(self.pdf_dir):
            self.logger.info("开始处理文件：" + str(i))
            try:
                txt_name = i.replace(".pdf", ".txt")
                if not self.ocr:
                    text = self.read_pdf(os.path.join(self.pdf_dir, i))
                else:
                    text = self.ocr_read(os.path.join(self.pdf_dir, i))
                with open(os.path.join(self.txt_dir, txt_name), "w+", encoding="utf-8") as f:
                    f.write(text)
            except:
                self.logger.error("处理出错！", exc_info=True)
        self.logger.info("-----完成------")

    def read_pdf(self,path):
        fp = open(path, 'rb')
        parser = PDFParser(fp)
        doc = PDFDocument()
        parser.set_document(doc)
        doc.set_parser(parser)

        doc.initialize()

        if not doc.is_extractable:
            raise PDFTextExtractionNotAllowed
        else:
            rsrcmgr = PDFResourceManager()
            laparams = LAParams()
            device = PDFPageAggregator(rsrcmgr, laparams=laparams)
            interpreter = PDFPageInterpreter(rsrcmgr, device)

            text = ""
            for page in doc.get_pages():
                interpreter.process_page(page)
                layout = device.get_result()

                for x in layout:
                    if (isinstance(x, LTTextBoxHorizontal)):
                        results = x.get_text()
                        text += results + "\n"
            return text

    def ocr_read(self,path):
        text = None
        images = convert_from_path(path)
        for index, img in enumerate(images):
            if index > 1:
                break
            image_path = '%s/page_%s.png' % (self.temp_dir, index)
            self.logger.info("临时图片路径：" + image_path)
            img.save(image_path)
            if text == None:
                text = pytesseract.image_to_string(image_path)
            else:
                text += pytesseract.image_to_string(image_path)

        return text

if __name__ == '__main__':
    # run(pdf_dir=r"Y:\数据配送专用(勿动）\中信所\会议录\zxhy20200204001a\zxhy20200204001a\rabbit2",
    #     txt_dir=r"Y:\数据配送专用(勿动）\中信所\会议录\zxhy20200204001a\zxhy20200204001a\rabbit2_txt",
    #     ocr=True)

    # run(pdf_dir=r"Y:\数据配送专用(勿动）\中信所\会议录\zxhy20191129001\抽取关键词\转过的61",
    #     txt_dir=r"Y:\数据配送专用(勿动）\中信所\会议录\zxhy20191129001\抽取关键词\转过的61_txt",
    #     ocr=True)
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
    # path="C:/public/目次采全文/0108/"
    # print(os.path.abspath("."))