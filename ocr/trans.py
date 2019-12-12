
from  googletrans import Translator
import sys
import cv2
import numpy as np
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow, QAction, QFileDialog, QApplication,QLabel,QWidget,QLineEdit,QTextEdit,QGridLayout

# translator = Translator(service_urls=['translate.google.cn'])
# source = '在面对大规模需要翻译的句子时就会很慢'
# text = translator.translate(source,src='zh-cn',dest='en').text
# print(text)



#!/usr/bin/python3
# -*- coding: utf-8 -*-



# class win(QDialog):
#     def __init__(self):
#
#         # 初始化一个img的ndarray, 用于存储图像
#         self.img = np.ndarray(())
#
#         super().__init__()
#         self.initUI()
#
#     def initUI(self):
#         self.resize(400, 300)
#         self.btnOpen = QPushButton('打开', self)
#         self.btnSave = QPushButton('保存', self)
#         self.btnProcess = QPushButton('下一页', self)
#         self.btnQuit = QPushButton('退出', self)
#         self.label = QLabel()
#
#         # 布局设定
#         layout = QGridLayout(self)
#         layout.addWidget(self.label, 0, 1, 3, 4)
#         layout.addWidget(self.btnOpen, 4, 1, 1, 1)
#         layout.addWidget(self.btnSave, 4, 2, 1, 1)
#         layout.addWidget(self.btnProcess, 4, 3, 1, 1)
#         layout.addWidget(self.btnQuit, 4, 4, 1, 1)
#
#         # 信号与槽连接, PyQt5与Qt5相同, 信号可绑定普通成员函数
#         self.btnOpen.clicked.connect(self.openSlot)
#         self.btnSave.clicked.connect(self.saveSlot)
#         self.btnProcess.clicked.connect(self.processSlot)
#         self.btnQuit.clicked.connect(self.close)
#
#     def openSlot(self):
#         # 调用打开文件diglog
#         fileName, tmp = QFileDialog.getOpenFileName(
#             self, 'Open Image', './__data', '*.png *.jpg *.bmp')
#
#         if fileName is '':
#             return
#
#         # 采用opencv函数读取数据
#         self.img = cv.imread(fileName, -1)
#
#         if self.img.size == 1:
#             return
#
#         self.refreshShow()
#
#     def saveSlot(self):
#         # 调用存储文件dialog
#         fileName, tmp = QFileDialog.getSaveFileName(
#             self, 'Save Image', './__data', '*.png *.jpg *.bmp', '*.png')
#
#         if fileName is '':
#             return
#         if self.img.size == 1:
#             return
#
#         # 调用opencv写入图像
#         cv.imwrite(fileName, self.img)
#
#     def processSlot(self):
#         if self.img.size == 1:
#             return
#
#         # 对图像做模糊处理, 窗口设定为5x5
#         self.img = cv.blur(self.img, (5, 5))
#
#         self.refreshShow()
#
#     def refreshShow(self):
#         # 提取图像的尺寸和通道, 用于将opencv下的image转换成Qimage
#         height, width, channel = self.img.shape
#         bytesPerLine = 3 * width
#         self.qImg = QImage(self.img.data, width, height, bytesPerLine,
#                            QImage.Format_RGB888).rgbSwapped()
#
#         # 将Qimage显示出来
#         self.label.setPixmap(QPixmap.fromImage(self.qImg))


class Win(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):

        textEdit = QTextEdit()
        self.setCentralWidget(textEdit)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&文件')

        open = QAction("打开", self)
        fileMenu.addAction(open)

        save = QAction("保存", self)
        fileMenu.addAction(save)


        open.triggered.connect(self.opne_file)
        self.setGeometry(100, 100, 1000, 500)
        self.setWindowTitle('Simple menu')
        self.show()
    def opne_file(self):
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


class MainWin(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        title = QLabel()
        title.setStyleSheet("border:2px solid red;")
        author = QLabel()
        author.setStyleSheet("border:2px solid red;")
        meau = QLabel()
        meau.setStyleSheet("border:2px solid red;")

        titleEdit = QLineEdit()
        authorEdit = QLineEdit()
        reviewEdit = QTextEdit()

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(title, 1, 0)
        grid.addWidget(titleEdit, 1, 1)

        grid.addWidget(author, 2, 0)
        grid.addWidget(authorEdit, 2, 1)

        grid.addWidget(review, 3, 0)
        grid.addWidget(reviewEdit, 3, 1, 5, 1)

        self.setLayout(grid)


        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('Review')
        self.show()


if __name__ == '__main__':


    app = QApplication(sys.argv)
    ex = Win()
    sys.exit(app.exec_())

