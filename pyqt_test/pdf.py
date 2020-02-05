import sys
from PyQt5.QtWidgets import QMainWindow, QPushButton, \
    QApplication,QComboBox,QLabel,QFileDialog,QLineEdit,QPlainTextEdit
from PyQt5.QtGui import QFont


class Example(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.author=None
        self.abs=None



    def initUI(self):
        QFont()
        lbl = QLabel("抽取项目：", self)
        lbl.move(50,50)
        lb2 = QLabel("作者：", self)
        lb2.move(50, 100)

        author=QComboBox(self)
        author.addItems(["True","False"])
        author.move(100,100)

        author.activated[str].connect(self.author_change)
        lb3 = QLabel("摘要：", self)
        lb3.move(50, 150)

        abs = QComboBox(self)
        abs.addItems(["True", "False"])
        abs.move(100, 150)

        abs.activated[str].connect(self.abs_change)

        lb4 = QLabel("EXCEL路径：", self)
        lb4.move(50, 200)

        self.le = QLineEdit(self)
        self.le.move(150,200)
        # get_filename_path, ok = QFileDialog.getOpenFileName(self,
        #                                                     "选取单个文件",
        #                                                     "C:/",
        #                                                     "All Files (*);;Text Files (*.txt)")

        btn2 = QPushButton("启动", self)
        btn2.move(50, 250)

        btn2.clicked.connect(self.buttonClicked)

        # log=QPlainTextEdit(self)
        # log.move(50,300)
        # log.setTabStopDistance(
        #     QtGui.QFontMetricsF(log.font()).width(' ') * 10)


        self.setGeometry(300, 300, 500, 600)
        self.setWindowTitle('PDF抽取工具')
        self.show()


    def buttonClicked(self):

        sender = self.sender()
        print(self.abs,self.author,self.le.text())


    def author_change(self, text):
        self.author=text
    def abs_change(self,text):
        self.abs=text


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())