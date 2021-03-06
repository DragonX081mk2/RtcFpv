# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qtwebviewDemo.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(918, 589)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.webEngineView = QtWebEngineWidgets.QWebEngineView(self.centralwidget)
        self.webEngineView.setGeometry(QtCore.QRect(540, 10, 361, 531))
        self.webEngineView.setUrl(QtCore.QUrl("about:blank"))
        self.webEngineView.setObjectName("webEngineView")
        self.render_label = QtWidgets.QLabel(self.centralwidget)
        self.render_label.setGeometry(QtCore.QRect(30, 10, 471, 321))
        self.render_label.setAutoFillBackground(True)
        self.render_label.setTextFormat(QtCore.Qt.AutoText)
        self.render_label.setScaledContents(True)
        self.render_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop|QtCore.Qt.AlignTrailing)
        self.render_label.setObjectName("render_label")
        self.speedSlider = QtWidgets.QSlider(self.centralwidget)
        self.speedSlider.setGeometry(QtCore.QRect(20, 360, 22, 160))
        self.speedSlider.setMaximum(10)
        self.speedSlider.setPageStep(1)
        self.speedSlider.setProperty("value", 3)
        self.speedSlider.setOrientation(QtCore.Qt.Vertical)
        self.speedSlider.setObjectName("speedSlider")
        self.yawSlider = QtWidgets.QSlider(self.centralwidget)
        self.yawSlider.setGeometry(QtCore.QRect(70, 440, 160, 22))
        self.yawSlider.setMaximum(180)
        self.yawSlider.setProperty("value", 90)
        self.yawSlider.setOrientation(QtCore.Qt.Horizontal)
        self.yawSlider.setInvertedAppearance(True)
        self.yawSlider.setInvertedControls(False)
        self.yawSlider.setObjectName("yawSlider")
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(280, 400, 239, 121))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.forwardButton = QtWidgets.QPushButton(self.layoutWidget)
        self.forwardButton.setObjectName("forwardButton")
        self.gridLayout.addWidget(self.forwardButton, 0, 1, 1, 1)
        self.leftButton = QtWidgets.QPushButton(self.layoutWidget)
        self.leftButton.setObjectName("leftButton")
        self.gridLayout.addWidget(self.leftButton, 1, 0, 1, 1)
        self.rightButton = QtWidgets.QPushButton(self.layoutWidget)
        self.rightButton.setObjectName("rightButton")
        self.gridLayout.addWidget(self.rightButton, 1, 2, 1, 1)
        self.backButton = QtWidgets.QPushButton(self.layoutWidget)
        self.backButton.setObjectName("backButton")
        self.gridLayout.addWidget(self.backButton, 2, 1, 1, 1)
        self.testButton = QtWidgets.QPushButton(self.centralwidget)
        self.testButton.setGeometry(QtCore.QRect(70, 360, 75, 23))
        self.testButton.setObjectName("testButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 918, 23))
        self.menubar.setObjectName("menubar")
        self.menuMenu1 = QtWidgets.QMenu(self.menubar)
        self.menuMenu1.setObjectName("menuMenu1")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menuMenu1.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.render_label.setText(_translate("MainWindow", "live"))
        self.forwardButton.setText(_translate("MainWindow", "?????? W"))
        self.leftButton.setText(_translate("MainWindow", "?????? A"))
        self.rightButton.setText(_translate("MainWindow", "?????? D"))
        self.backButton.setText(_translate("MainWindow", "?????? S"))
        self.testButton.setText(_translate("MainWindow", "testFunc"))
        self.menuMenu1.setTitle(_translate("MainWindow", "Menu1"))
from PyQt5 import QtWebEngineWidgets
