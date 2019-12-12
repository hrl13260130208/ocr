import sys
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QApplication,QWidget,QPushButton,QLCDNumber,QVBoxLayout,QPlainTextEdit,QLineEdit,QFileDialog
from PyQt5.QtCore import Qt, pyqtSignal, QTimer,QRect
from PyQt5.QtGui import QIcon,QFont,QColor,QTextFormat


class Example(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()
        self.w = MyWindow2()


    def initUI(self):

        b=QPushButton("test",self)
        b.clicked.connect(self.do)
        l=ClickLine(self)
        l.move(50,50)

        # l1=QLineEdit(self)
        # l1.move(50,100)
        # l1.setText("只能")

        # q=QCodeEditor(self)
        # q.resize(200,200)

        self.setGeometry(300, 300, 350, 250)
        self.setWindowTitle('Main window')
        self.show()
    def do(self):
        self.w.show()


class QCodeEditor(QPlainTextEdit):
    class NumberBar(QWidget):

        def __init__(self, editor):
            QWidget.__init__(self, editor)

            self.editor = editor
            self.editor.blockCountChanged.connect(self.updateWidth)
            self.editor.updateRequest.connect(self.updateContents)
            self.font = QFont()
            self.numberBarColor = QColor("#e8e8e8")

        def paintEvent(self, event):
            pass

        def getWidth(self):
            pass

        def updateWidth(self):
            pass

        def updateContents(self, rect, dy):
            pass

    def __init__(self):
        super(QCodeEditor, self).__init__()
        self.setWindowTitle('微信公众号：学点编程吧--带行号和颜色的文本框')
        self.setFont(QFont("Ubuntu Mono", 12))
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.number_bar = self.NumberBar(self)
        self.currentLineNumber = None
        self.cursorPositionChanged.connect(self.highligtCurrentLine)
        self.setViewportMargins(40, 0, 0, 0)
        self.highligtCurrentLine()

    def resizeEvent(self, *e):
        cr = self.contentsRect()
        rec = QRect(cr.left(), cr.top(), self.number_bar.getWidth(), cr.height())
        self.number_bar.setGeometry(rec)

    def highligtCurrentLine(self):
        newCurrentLineNumber = self.textCursor().blockNumber()
        if newCurrentLineNumber != self.currentLineNumber:
            lineColor = QColor(Qt.yellow).lighter(160)
            self.currentLineNumber = newCurrentLineNumber
            hi_selection = QTextEdit.ExtraSelection()
            hi_selection.format.setBackground(lineColor)
            hi_selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            hi_selection.cursor = self.textCursor()
            hi_selection.cursor.clearSelection()
            self.setExtraSelections([hi_selection])
class MyWindow2(QWidget):
    '''自定义窗口'''
    # 知识点：
    # 1.为了得到返回值用到了自定义的信号/槽
    # 2.为了显示动态数字，使用了计时器

    before_close_signal = pyqtSignal(int)  # 自定义信号（int类型）

    def __init__(self):
        super().__init__()

        self.sec = 0
        self.setWindowTitle('自定义窗口')
        self.resize(200, 150)

        t=QPlainTextEdit(self)
        t.resize(200,100)
        btn1 = QPushButton("测试",self)
        btn1.move(0,100)
        btn2 = QPushButton("关闭",self)
        btn2.move(100,100)
        btn2.clicked.connect(self.closeitem)


    # 默认关闭事件
    def closeitem(self):
        self.close()

class ClickLine(QLineEdit):

    def mousePressEvent(self, QMouseEvent):
        fileName= QFileDialog.getOpenFileName(
            self, 'Open Image', './__data', '*.xls')
        self.setText(fileName[0])


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
    # QCodeEditor()
