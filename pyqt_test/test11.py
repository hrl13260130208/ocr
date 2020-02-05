import sys
from PyQt5.QtWidgets import QMainWindow, QPushButton, \
    QApplication,QComboBox,QLabel,QFileDialog,QLineEdit,QPlainTextEdit,QWidget
from PyQt5.QtCore import pyqtSignal




class showconfig(QWidget):
    '''自定义窗口'''

    before_close_signal = pyqtSignal(int)  # 自定义信号（int类型）
    def __init__(self,text):
        super().__init__()

        self.setWindowTitle('配置窗口')
        self.resize(300, 100)

        self.t=QPlainTextEdit(self)
        self.t.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.t.resize(400,400)
        self.t.setPlainText(text)

        # btn1 = QPushButton("更新",self)
        # btn1.move(100,400)
        # btn1.clicked.connect(self.up_config)
        #
        # btn2 = QPushButton("关闭",self)
        # btn2.move(250,400)
        # btn2.clicked.connect(self.closeitem)


    # def up_config(self):
    #     text=self.t.toPlainText()
    #     with open(self.file_path,"w+",encoding="utf-8") as f:
    #         f.write(text)
    #     config_to_dict(self.file_path,self.config)
    #     self.close()


    # 默认关闭事件
    # def closeitem(self):
    #     self.close()


class Example(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()
        y_text="放行"
        n_text="扣发"
        self.show_window_y = showconfig(y_text)
        self.show_window_n = showconfig(n_text)


    def initUI(self):



        self.le = QLineEdit(self)
        self.le.move(20,20)
        self.le.resize(560,400)
        # get_filename_path, ok = QFileDialog.getOpenFileName(self,
        #                                                     "选取单个文件",
        #                                                     "C:/",
        #                                                     "All Files (*);;Text Files (*.txt)")

        btn2 = QPushButton("审读", self)
        btn2.move(250, 450)

        btn2.clicked.connect(self.buttonClicked)

        # log=QPlainTextEdit(self)
        # log.move(50,300)
        # log.setTabStopDistance(
        #     QtGui.QFontMetricsF(log.font()).width(' ') * 10)


        self.setGeometry(300, 300, 600, 500)
        self.setWindowTitle('审读工具')
        self.show()


    def buttonClicked(self):

        # sender = self.sender()
        print(self.le.text())
        #todo


        self.show_window_y.show()



    # def author_change(self, text):
    #     self.author=text
    # def abs_change(self,text):
    #     self.abs=text




if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())