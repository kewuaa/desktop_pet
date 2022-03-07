# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_translate.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(478, 387)
        self.action = QAction(MainWindow)
        self.action.setObjectName(u"action")
        self.action_bat = QAction(MainWindow)
        self.action_bat.setObjectName(u"action_bat")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.from_comboBox = QComboBox(self.widget)
        self.from_comboBox.setObjectName(u"from_comboBox")

        self.horizontalLayout.addWidget(self.from_comboBox)

        self.exchangeButton = QPushButton(self.widget)
        self.exchangeButton.setObjectName(u"exchangeButton")

        self.horizontalLayout.addWidget(self.exchangeButton, 0, Qt.AlignHCenter)

        self.to_comboBox = QComboBox(self.widget)
        self.to_comboBox.setObjectName(u"to_comboBox")

        self.horizontalLayout.addWidget(self.to_comboBox)

        self.frame = QFrame(self.widget)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)

        self.horizontalLayout.addWidget(self.frame)

        self.domain_comboBox = QComboBox(self.widget)
        self.domain_comboBox.setObjectName(u"domain_comboBox")

        self.horizontalLayout.addWidget(self.domain_comboBox)


        self.verticalLayout.addWidget(self.widget)

        self.widget_2 = QWidget(self.centralwidget)
        self.widget_2.setObjectName(u"widget_2")
        self.horizontalLayout_2 = QHBoxLayout(self.widget_2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.from_textEdit = QTextEdit(self.widget_2)
        self.from_textEdit.setObjectName(u"from_textEdit")

        self.horizontalLayout_2.addWidget(self.from_textEdit)

        self.to_textEdit = QTextEdit(self.widget_2)
        self.to_textEdit.setObjectName(u"to_textEdit")
        self.to_textEdit.setReadOnly(True)

        self.horizontalLayout_2.addWidget(self.to_textEdit)


        self.verticalLayout.addWidget(self.widget_2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 478, 22))
        self.menu = QMenu(self.menubar)
        self.menu.setObjectName(u"menu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menu.menuAction())
        self.menu.addAction(self.action)
        self.menu.addAction(self.action_bat)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"\u767e\u5ea6\u7ffb\u8bd1", None))
        self.action.setText(QCoreApplication.translate("MainWindow", u"\u590d\u5236\u7ffb\u8bd1\u7ed3\u679c", None))
        self.action_bat.setText(QCoreApplication.translate("MainWindow", u"\u5bfc\u51fabat\u811a\u672c\u6587\u4ef6", None))
        self.exchangeButton.setText("")
        self.menu.setTitle(QCoreApplication.translate("MainWindow", u"\u7f16\u8f91", None))
    # retranslateUi

