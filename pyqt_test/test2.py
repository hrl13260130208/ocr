import sys
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication,QComboBox


class Example(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.author=None


    def initUI(self):
        self.author=QComboBox(self)
        self.author.addItems(["True","False"])
        print(self.author.currentText())
        # self.author.currentIndexChanged().connect(self.author_change)

        btn2 = QPushButton("Button 2", self)
        btn2.move(150, 50)


        btn2.clicked.connect(self.buttonClicked(self.author))

        self.statusBar()

        self.setGeometry(300, 300, 290, 150)
        self.setWindowTitle('Event sender')
        self.show()


    def buttonClicked(self,author):

        sender = self.sender()
        print(author.currentText())
        self.statusBar().showMessage(sender.text() + ' was pressed')

    def author_change(self):
        pass



if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())