import sys
from PyQt5.QtWidgets import QMainWindow, QAction, QFileDialog, QApplication,QLabel,QWidget,QLineEdit,QTextEdit,QGridLayout
from PyQt5.QtGui import QImage, QPixmap
import numpy as np
import cv2


class Example(QMainWindow,QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):               

        # exitAct = QAction(QIcon('exit.png'), '&Exit', self)
        # exitAct.setShortcut('Ctrl+Q')
        # exitAct.setStatusTip('Exit application')
        # exitAct.triggered.connect(qApp.quit)
        #
        # self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&文件')

        open = QAction("打开", self)
        fileMenu.addAction(open)

        save = QAction("保存", self)
        fileMenu.addAction(save)

        # self.label = QLabel(self)
        # self.label.resize(200, 200)
        # self.label.setStyleSheet("border:2px solid red;")
        # title = QLabel('Title')
        # author = QLabel('Author')
        # review = QLabel('Review')
        #
        # titleEdit = QLineEdit(self)
        # authorEdit = QLineEdit(self)
        # reviewEdit = QTextEdit(self)
        #
        # grid = QGridLayout(self)
        # grid.setSpacing(10)
        #
        # grid.addWidget(title, 1, 0)
        # grid.addWidget(titleEdit, 1, 1)
        #
        # grid.addWidget(author, 2, 0)
        # grid.addWidget(authorEdit, 2, 1)
        #
        # grid.addWidget(review, 3, 0)
        # grid.addWidget(reviewEdit, 3, 1, 5, 1)
        #
        # self.setLayout(grid)







        open.triggered.connect(self.opne_file)
        self.setGeometry(100, 100, 1000, 500)
        self.setWindowTitle('Simple menu')    
        self.show()
    def opne_file(self,label):
        fileName, tmp = QFileDialog.getOpenFileName(
            self, 'Open Image', './__data', '*.png *.jpg *.bmp')

        if fileName is '':
            return

        # 采用opencv函数读取数据
        img = cv2.imread(fileName, -1)

        if img.size == 1:
            return

        self.ptint_image(img,self.label)
    def ptint_image(self,image,label):
        # 提取图像的尺寸和通道, 用于将opencv下的image转换成Qimage
        height, width, channel = image.shape
        print(height,width)
        bytesPerLine = 3 * width
        self.qImg = QImage(image.data, width, height, bytesPerLine,
                           QImage.Format_RGB888).rgbSwapped()

        # 将Qimage显示出来
        label.setPixmap(QPixmap.fromImage(self.qImg))

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())