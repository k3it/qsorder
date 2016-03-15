# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qsorder.ui'
#
# Created: Tue Mar 15 13:42:36 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(675, 353)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/logo/qsorder.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Form.setWindowIcon(icon)
        Form.setWindowOpacity(0.97)
        self.tabWidget = QtGui.QTabWidget(Form)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 671, 351))
        self.tabWidget.setStyleSheet("background-color: rgb(243, 239, 222);\n"
"background-image: url(:/bkground/ricepaper_v3.png);")
        self.tabWidget.setObjectName("tabWidget")
        self.console_tab = QtGui.QWidget()
        self.console_tab.setObjectName("console_tab")
        self.console = QtGui.QPlainTextEdit(self.console_tab)
        self.console.setGeometry(QtCore.QRect(0, 0, 661, 231))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        self.console.setFont(font)
        self.console.setStyleSheet("border: 0px;")
        self.console.setTabChangesFocus(False)
        self.console.setReadOnly(True)
        self.console.setPlainText("")
        self.console.setBackgroundVisible(False)
        self.console.setCenterOnScroll(False)
        self.console.setObjectName("console")
        self.quitButton_2 = QtGui.QPushButton(self.console_tab)
        self.quitButton_2.setGeometry(QtCore.QRect(510, 270, 101, 23))
        self.quitButton_2.setObjectName("quitButton_2")
        self.manual_dump_btn = QtGui.QPushButton(self.console_tab)
        self.manual_dump_btn.setGeometry(QtCore.QRect(380, 270, 101, 23))
        self.manual_dump_btn.setObjectName("manual_dump_btn")
        self.line = QtGui.QFrame(self.console_tab)
        self.line.setGeometry(QtCore.QRect(350, 240, 20, 81))
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.line_2 = QtGui.QFrame(self.console_tab)
        self.line_2.setGeometry(QtCore.QRect(10, 230, 641, 16))
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.widget = QtGui.QWidget(self.console_tab)
        self.widget.setGeometry(QtCore.QRect(10, 250, 341, 71))
        self.widget.setObjectName("widget")
        self.gridLayout_2 = QtGui.QGridLayout(self.widget)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_4 = QtGui.QLabel(self.widget)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 0, 0, 1, 1)
        self.label_5 = QtGui.QLabel(self.widget)
        self.label_5.setObjectName("label_5")
        self.gridLayout_2.addWidget(self.label_5, 0, 1, 1, 1)
        self.label_6 = QtGui.QLabel(self.widget)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.gridLayout_2.addWidget(self.label_6, 0, 2, 1, 1)
        self.label_16 = QtGui.QLabel(self.widget)
        self.label_16.setObjectName("label_16")
        self.gridLayout_2.addWidget(self.label_16, 0, 3, 1, 1)
        self.label_21 = QtGui.QLabel(self.widget)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_21.setFont(font)
        self.label_21.setObjectName("label_21")
        self.gridLayout_2.addWidget(self.label_21, 1, 0, 1, 1)
        self.label_22 = QtGui.QLabel(self.widget)
        self.label_22.setObjectName("label_22")
        self.gridLayout_2.addWidget(self.label_22, 1, 1, 1, 1)
        self.label_14 = QtGui.QLabel(self.widget)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_14.setFont(font)
        self.label_14.setObjectName("label_14")
        self.gridLayout_2.addWidget(self.label_14, 1, 2, 1, 1)
        self.label_17 = QtGui.QLabel(self.widget)
        self.label_17.setObjectName("label_17")
        self.gridLayout_2.addWidget(self.label_17, 1, 3, 1, 1)
        self.label_23 = QtGui.QLabel(self.widget)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_23.setFont(font)
        self.label_23.setObjectName("label_23")
        self.gridLayout_2.addWidget(self.label_23, 2, 0, 1, 1)
        self.label_24 = QtGui.QLabel(self.widget)
        self.label_24.setObjectName("label_24")
        self.gridLayout_2.addWidget(self.label_24, 2, 1, 1, 1)
        self.label_19 = QtGui.QLabel(self.widget)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_19.setFont(font)
        self.label_19.setObjectName("label_19")
        self.gridLayout_2.addWidget(self.label_19, 2, 2, 1, 1)
        self.label_20 = QtGui.QLabel(self.widget)
        self.label_20.setObjectName("label_20")
        self.gridLayout_2.addWidget(self.label_20, 2, 3, 1, 1)
        self.label_15 = QtGui.QLabel(self.widget)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_15.setFont(font)
        self.label_15.setObjectName("label_15")
        self.gridLayout_2.addWidget(self.label_15, 3, 0, 1, 1)
        self.label_18 = QtGui.QLabel(self.widget)
        self.label_18.setObjectName("label_18")
        self.gridLayout_2.addWidget(self.label_18, 3, 1, 1, 1)
        self.label_25 = QtGui.QLabel(self.widget)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(8)
        font.setWeight(75)
        font.setItalic(False)
        font.setBold(True)
        self.label_25.setFont(font)
        self.label_25.setStyleSheet("")
        self.label_25.setObjectName("label_25")
        self.gridLayout_2.addWidget(self.label_25, 3, 2, 1, 1)
        self.label_26 = QtGui.QLabel(self.widget)
        self.label_26.setObjectName("label_26")
        self.gridLayout_2.addWidget(self.label_26, 3, 3, 1, 1)
        self.tabWidget.addTab(self.console_tab, "")
        self.config_tab = QtGui.QWidget()
        self.config_tab.setObjectName("config_tab")
        self.debug = QtGui.QCheckBox(self.config_tab)
        self.debug.setGeometry(QtCore.QRect(30, 210, 70, 17))
        self.debug.setObjectName("debug")
        self.label_2 = QtGui.QLabel(self.config_tab)
        self.label_2.setGeometry(QtCore.QRect(180, 10, 263, 18))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.continuous = QtGui.QCheckBox(self.config_tab)
        self.continuous.setGeometry(QtCore.QRect(30, 240, 124, 17))
        self.continuous.setObjectName("continuous")
        self.so2r = QtGui.QCheckBox(self.config_tab)
        self.so2r.setGeometry(QtCore.QRect(30, 270, 70, 17))
        self.so2r.setObjectName("so2r")
        self.inputs = QtGui.QComboBox(self.config_tab)
        self.inputs.setGeometry(QtCore.QRect(85, 120, 191, 20))
        self.inputs.setObjectName("inputs")
        self.label_11 = QtGui.QLabel(self.config_tab)
        self.label_11.setGeometry(QtCore.QRect(20, 120, 60, 16))
        self.label_11.setObjectName("label_11")
        self.saveButton = QtGui.QPushButton(self.config_tab)
        self.saveButton.setGeometry(QtCore.QRect(400, 210, 101, 41))
        self.saveButton.setObjectName("saveButton")
        self.applyButton = QtGui.QPushButton(self.config_tab)
        self.applyButton.setGeometry(QtCore.QRect(510, 210, 101, 41))
        self.applyButton.setObjectName("applyButton")
        self.label_12 = QtGui.QLabel(self.config_tab)
        self.label_12.setGeometry(QtCore.QRect(290, 120, 102, 16))
        self.label_12.setObjectName("label_12")
        self.drop_key = QtGui.QLineEdit(self.config_tab)
        self.drop_key.setGeometry(QtCore.QRect(401, 120, 191, 20))
        self.drop_key.setObjectName("drop_key")
        self.commandLinkButton = QtGui.QCommandLinkButton(self.config_tab)
        self.commandLinkButton.setGeometry(QtCore.QRect(400, 150, 172, 41))
        self.commandLinkButton.setObjectName("commandLinkButton")
        self.label_13 = QtGui.QLabel(self.config_tab)
        self.label_13.setGeometry(QtCore.QRect(190, 160, 131, 141))
        self.label_13.setText("")
        self.label_13.setPixmap(QtGui.QPixmap(":/logo/qsorder.png"))
        self.label_13.setScaledContents(True)
        self.label_13.setObjectName("label_13")
        self.quitButton = QtGui.QPushButton(self.config_tab)
        self.quitButton.setGeometry(QtCore.QRect(510, 270, 101, 23))
        self.quitButton.setObjectName("quitButton")
        self.layoutWidget = QtGui.QWidget(self.config_tab)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 171, 161, 22))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtGui.QLabel(self.layoutWidget)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.hotkey = QtGui.QLineEdit(self.layoutWidget)
        self.hotkey.setObjectName("hotkey")
        self.horizontalLayout_3.addWidget(self.hotkey)
        self.layoutWidget1 = QtGui.QWidget(self.config_tab)
        self.layoutWidget1.setGeometry(QtCore.QRect(20, 50, 125, 48))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.gridLayout = QtGui.QGridLayout(self.layoutWidget1)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(self.layoutWidget1)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.buffer = QtGui.QSpinBox(self.layoutWidget1)
        self.buffer.setButtonSymbols(QtGui.QAbstractSpinBox.UpDownArrows)
        self.buffer.setMaximum(1000)
        self.buffer.setProperty("value", 45)
        self.buffer.setObjectName("buffer")
        self.gridLayout.addWidget(self.buffer, 0, 1, 1, 1)
        self.label_7 = QtGui.QLabel(self.layoutWidget1)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 1, 0, 1, 1)
        self.delay = QtGui.QSpinBox(self.layoutWidget1)
        self.delay.setMaximum(1000)
        self.delay.setProperty("value", 20)
        self.delay.setObjectName("delay")
        self.gridLayout.addWidget(self.delay, 1, 1, 1, 1)
        self.layoutWidget2 = QtGui.QWidget(self.config_tab)
        self.layoutWidget2.setGeometry(QtCore.QRect(160, 50, 313, 22))
        self.layoutWidget2.setObjectName("layoutWidget2")
        self.horizontalLayout = QtGui.QHBoxLayout(self.layoutWidget2)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_8 = QtGui.QLabel(self.layoutWidget2)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout.addWidget(self.label_8)
        self.port = QtGui.QSpinBox(self.layoutWidget2)
        self.port.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.port.setMinimum(1024)
        self.port.setMaximum(65535)
        self.port.setProperty("value", 12060)
        self.port.setObjectName("port")
        self.horizontalLayout.addWidget(self.port)
        self.label_10 = QtGui.QLabel(self.layoutWidget2)
        self.label_10.setObjectName("label_10")
        self.horizontalLayout.addWidget(self.label_10)
        self.station_nr = QtGui.QSpinBox(self.layoutWidget2)
        self.station_nr.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.station_nr.setMinimum(0)
        self.station_nr.setMaximum(1024)
        self.station_nr.setProperty("value", 0)
        self.station_nr.setObjectName("station_nr")
        self.horizontalLayout.addWidget(self.station_nr)
        self.widget1 = QtGui.QWidget(self.config_tab)
        self.widget1.setGeometry(QtCore.QRect(160, 80, 451, 24))
        self.widget1.setObjectName("widget1")
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.widget1)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_9 = QtGui.QLabel(self.widget1)
        self.label_9.setObjectName("label_9")
        self.horizontalLayout_2.addWidget(self.label_9)
        self.path = QtGui.QLineEdit(self.widget1)
        self.path.setReadOnly(True)
        self.path.setObjectName("path")
        self.horizontalLayout_2.addWidget(self.path)
        self.horizontalLayout_4.addLayout(self.horizontalLayout_2)
        self.selectDir_btn = QtGui.QToolButton(self.widget1)
        self.selectDir_btn.setObjectName("selectDir_btn")
        self.horizontalLayout_4.addWidget(self.selectDir_btn)
        self.tabWidget.addTab(self.config_tab, "")

        self.retranslateUi(Form)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.quitButton_2, QtCore.SIGNAL("clicked()"), self.quitButton.click)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "QSORDER", None, QtGui.QApplication.UnicodeUTF8))
        self.quitButton_2.setText(QtGui.QApplication.translate("Form", "Exit", None, QtGui.QApplication.UnicodeUTF8))
        self.manual_dump_btn.setText(QtGui.QApplication.translate("Form", "Manual Dump", None, QtGui.QApplication.UnicodeUTF8))
        self.manual_dump_btn.setShortcut(QtGui.QApplication.translate("Form", "Ctrl+Alt+O", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Form", "Rec. Input:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("Form", "input input input input input in", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("Form", "Buffer, sec:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_16.setText(QtGui.QApplication.translate("Form", "555", None, QtGui.QApplication.UnicodeUTF8))
        self.label_21.setText(QtGui.QApplication.translate("Form", "Qsorder status:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_22.setText(QtGui.QApplication.translate("Form", "Not Running", None, QtGui.QApplication.UnicodeUTF8))
        self.label_14.setText(QtGui.QApplication.translate("Form", "Delay, sec:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_17.setText(QtGui.QApplication.translate("Form", "55", None, QtGui.QApplication.UnicodeUTF8))
        self.label_23.setText(QtGui.QApplication.translate("Form", "Dropbox status:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_24.setText(QtGui.QApplication.translate("Form", "Not configured", None, QtGui.QApplication.UnicodeUTF8))
        self.label_19.setText(QtGui.QApplication.translate("Form", "Qs in buffer:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_20.setText(QtGui.QApplication.translate("Form", "55", None, QtGui.QApplication.UnicodeUTF8))
        self.label_15.setText(QtGui.QApplication.translate("Form", "UDP Port:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_18.setText(QtGui.QApplication.translate("Form", "port", None, QtGui.QApplication.UnicodeUTF8))
        self.label_25.setText(QtGui.QApplication.translate("Form", "Qsorder ver:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_26.setText(QtGui.QApplication.translate("Form", "5.5", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.console_tab), QtGui.QApplication.translate("Form", "Qsorder Console", None, QtGui.QApplication.UnicodeUTF8))
        self.debug.setText(QtGui.QApplication.translate("Form", "Debug", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Form", "QSORDER Configuration Parameters", None, QtGui.QApplication.UnicodeUTF8))
        self.continuous.setText(QtGui.QApplication.translate("Form", "Continious Recording", None, QtGui.QApplication.UnicodeUTF8))
        self.so2r.setText(QtGui.QApplication.translate("Form", "SO2R", None, QtGui.QApplication.UnicodeUTF8))
        self.label_11.setText(QtGui.QApplication.translate("Form", "Audio Input:", None, QtGui.QApplication.UnicodeUTF8))
        self.saveButton.setText(QtGui.QApplication.translate("Form", "Save", None, QtGui.QApplication.UnicodeUTF8))
        self.applyButton.setText(QtGui.QApplication.translate("Form", "Apply Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.label_12.setText(QtGui.QApplication.translate("Form", "Dropbox Access Key:", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton.setText(QtGui.QApplication.translate("Form", "Get Dropbox Key", None, QtGui.QApplication.UnicodeUTF8))
        self.quitButton.setText(QtGui.QApplication.translate("Form", "Exit", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Form", "Hot Key: CTRL+ALT+", None, QtGui.QApplication.UnicodeUTF8))
        self.hotkey.setText(QtGui.QApplication.translate("Form", "O", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "Buffer Length:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("Form", "Delay:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("Form", "UDP Port:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_10.setText(QtGui.QApplication.translate("Form", "Station Number:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setText(QtGui.QApplication.translate("Form", "Path:", None, QtGui.QApplication.UnicodeUTF8))
        self.path.setText(QtGui.QApplication.translate("Form", "<current directory>", None, QtGui.QApplication.UnicodeUTF8))
        self.selectDir_btn.setText(QtGui.QApplication.translate("Form", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.config_tab), QtGui.QApplication.translate("Form", "Configuration", None, QtGui.QApplication.UnicodeUTF8))

import bkg_img_rc
