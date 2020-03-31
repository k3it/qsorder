# from PySide.QtCore import * 
# from PySide.QtGui import *
# from PySide.QtUiTools import *

from PyQt5 import  QtCore, QtGui, uic
from PyQt5.QtWidgets import QApplication, QWidget

import os
import webbrowser

try:
    from winreg import *
except:
    # non-windows platform
    pass

try:
    from . import qsorder_ui
except:
    import qsorder_ui


# import pyqtgraph as pg

# class PlotWidget(pg.PlotWidget):
#     def __init__(self, parent):
#         super(PlotWidget, self).__init__()

class qsorderApp(QWidget):
    def __init__(self,options):
        super(qsorderApp, self).__init__()
        self.options = options
        self.initUI()

    def _register(self):
        webbrowser.open('https://qsorder.hamradiomap.com/register')


    def initUI(self):

        # self.loader = QUiLoader()
        # self.loader.registerCustomWidget(PlotWidget)
        # uifile = os.path.dirname(os.path.realpath(__file__)) + '\qsorder.ui'
        # self.ui = self.loader.load(uifile, self)
        
        self.ui = qsorder_ui.Ui_Form()
        # self.ui = uic.loadUi("qsorder.ui")
        # self.ui.show()

        self.ui.setupUi(self)


        # self.setGeometry(300,300,250,150)
        # self.setWindowTitle('QSORDER')
        # iconfile = os.path.dirname(os.path.realpath(__file__)) + 'qsorder.ico'
        # self.setWindowIcon(QIcon(iconfile))

        # # Create some widgets to be placed inside
        # self.stopbtn = QPushButton('Stop Qsorder')
        # self.text = QTextEdit('some text 73!')
        # self.text.setFont(self.font)

        # self.plot = pg.PlotWidget()


        # ## Create a grid layout to manage the widgets size and position
        # self.layout = QGridLayout()
        # self.setLayout(self.layout)
        # ## Add widgets to the layout in their proper positions
        # self.layout.addWidget(self.text, 1, 0)   # text edit goes in middle-left
        # self.layout.addWidget(self.plot, 0, 1, 3, 2)  # plot goes on right side, spanning 3 rows
        # self.layout.addWidget(self.stopbtn, 0, 0)   # button goes in upper-left

        self.ui.quitButton.clicked.connect(QtCore.QCoreApplication.instance().quit)
        self.ui.getDropbox_btn.clicked.connect(self._register)

        # process arguments
        self.ui.buffer.setValue(self.options.buffer_length)
        self.ui.delay.setValue(self.options.delay)
        self.ui.port.setValue(self.options.port)
        self.ui.drop_key.setText(self.options.drop_key)

        if self.options.path:
            self.ui.path.setText(self.options.path)
        else:
            try:
                aReg = ConnectRegistry(None,HKEY_CURRENT_USER)
                key = OpenKey(aReg, r"Software\N1MM Logger+")
                path = QueryValueEx(key,'userdir')[0] + "\\QsoRecording"
                self.ui.path.setText(path)
            except:
                self.ui.path.setText(os.getcwd())

        self.ui.hotkey.setText(self.options.hot_key.upper())
        self.ui.debug.setChecked(self.options.debug)
        self.ui.continuous.setChecked(self.options.continuous)
        self.ui.so2r.setChecked(self.options.so2r)
        self.ui.station_nr.setValue(self.options.station_nr)


        self.show()

        
