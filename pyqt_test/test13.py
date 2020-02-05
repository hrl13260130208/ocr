import sys
import pytesseract
import os
from PyQt5.QtWidgets import QMainWindow,QLabel,QComboBox,QPushButton,QTextEdit,QWidget,QRubberBand,QApplication
from PyQt5.QtCore import pyqtSignal,QRect,QPoint

class Example(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.lang="eng"
        self.path = os.path.join(os.path.abspath("."), "temp_image.jpg")





    def initUI(self):
        lbl = QLabel("语言：", self)
        lbl.move(25,30)

        la=QComboBox(self)
        la.addItems(["英语","日语","中文简体"])
        la.move(75,30)
        la.activated[str].connect(self.author_change)

        btn2 = QPushButton("截图", self)
        btn2.move(400, 30)

        btn2.clicked.connect(self.buttonClicked)

        self.t=QTextEdit(self)
        self.t.move(10,70)
        self.t.resize(580,300)

        self.setMouseTracking(True)

        self.setGeometry(300, 300, 600, 400)
        self.setWindowTitle('识别工具')
        self.show()


    def buttonClicked(self):
        self.showMinimized()

        # print(path,lang_code,self.lang)
        self.s = screen(self.path)
        self.s.close_signal.connect(self.ocr)

        self.s.show()




    def ocr(self):

        text=pytesseract.image_to_string(self.path, self.lang)
        self.t.setText(text)
        os.remove(self.path)
        self.showNormal()


    def author_change(self, text):
        if text == "日语":
            self.lang = "jpn"
        elif text =="中文简体":
            self.lang="chi_sim"



class screen(QWidget):
    close_signal = pyqtSignal()
    def __init__(self,image_path):
        super().__init__()

        # self.close_signal.connect(self.ocr)
        self.image_path=image_path
        self.cut = False
        self.setMouseTracking(True)
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        # print("=======")
        self.showFullScreen()
        self.setWindowOpacity(0.5)

    def mousePressEvent(self, event):
        self.cut = True
        self.start_x = event.x()
        self.start_y = event.y()

    def mouseReleaseEvent(self, event):
        self.cut = False
        r = self.rubberBand.geometry()
        print(r.getRect())

        self.setWindowOpacity(0)
        self.screen = QApplication.primaryScreen()
        screenshot = self.screen.grabWindow(QApplication.desktop().winId(), r.x(), r.y(),
                                            r.width(), r.height())
        screenshot.save(self.image_path)
        # screenshot.save(r"C:\temp\png\a.jpg")
        # text = pytesseract.image_to_string(self.image_path)
        # print(text)
        self.close_signal.emit()
        self.close()

    def mouseMoveEvent(self, event):

        if self.cut:
            end_x = event.x()
            end_y = event.y()

            self.rect = QRect(QPoint(self.start_x, self.start_y), QPoint(end_x, end_y))
            self.rubberBand.setGeometry(self.rect)
            self.rubberBand.show()

    # def ocr(self):
    #     text = pytesseract.image_to_string(self.image_path)
    #     print(text)

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
