

import sys
import os
import ctypes
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap
#构造RECT结构体
class RECT(ctypes.Structure):
    _fields_ = [('left', ctypes.c_long),
                ('top', ctypes.c_long),
                ('right', ctypes.c_long),
                ('bottom', ctypes.c_long)]
    def __str__(self):
        return str((self.left, self.top, self.right, self.bottom))
app = QApplication(sys.argv)
HWND = ctypes.windll.user32.FindWindowA(None, "window title")
if HWND == None:
    print("找不到窗口")
    quit()
QPixmap.grabWindow(HWND).save('c:/test.png', 'png')

