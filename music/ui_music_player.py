# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_music_player.ui'
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
        MainWindow.resize(1242, 562)
        self.action_bat = QAction(MainWindow)
        self.action_bat.setObjectName(u"action_bat")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_7 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setSizeConstraint(QLayout.SetFixedSize)
        self.listengroupBox = QGroupBox(self.centralwidget)
        self.listengroupBox.setObjectName(u"listengroupBox")
        self.verticalLayout = QVBoxLayout(self.listengroupBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.listenlistView = QListView(self.listengroupBox)
        self.listenlistView.setObjectName(u"listenlistView")
        self.listenlistView.setMinimumSize(QSize(300, 0))
        self.listenlistView.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.verticalLayout.addWidget(self.listenlistView)


        self.horizontalLayout_7.addWidget(self.listengroupBox)

        self.widget_10 = QWidget(self.centralwidget)
        self.widget_10.setObjectName(u"widget_10")
        self.verticalLayout_8 = QVBoxLayout(self.widget_10)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.widget_5 = QWidget(self.widget_10)
        self.widget_5.setObjectName(u"widget_5")
        self.horizontalLayout_3 = QHBoxLayout(self.widget_5)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.widget = QWidget(self.widget_5)
        self.widget.setObjectName(u"widget")
        self.verticalLayout_2 = QVBoxLayout(self.widget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.widget_2 = QWidget(self.widget)
        self.widget_2.setObjectName(u"widget_2")
        self.horizontalLayout = QHBoxLayout(self.widget_2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.musicercomboBox = QComboBox(self.widget_2)
        self.musicercomboBox.addItem("")
        self.musicercomboBox.addItem("")
        self.musicercomboBox.addItem("")
        self.musicercomboBox.setObjectName(u"musicercomboBox")

        self.horizontalLayout.addWidget(self.musicercomboBox)

        self.inputlineEdit = QLineEdit(self.widget_2)
        self.inputlineEdit.setObjectName(u"inputlineEdit")

        self.horizontalLayout.addWidget(self.inputlineEdit)

        self.searchButton = QPushButton(self.widget_2)
        self.searchButton.setObjectName(u"searchButton")

        self.horizontalLayout.addWidget(self.searchButton)


        self.verticalLayout_2.addWidget(self.widget_2)

        self.widget_3 = QWidget(self.widget)
        self.widget_3.setObjectName(u"widget_3")
        self.verticalLayout_3 = QVBoxLayout(self.widget_3)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.resultscrollArea = QScrollArea(self.widget_3)
        self.resultscrollArea.setObjectName(u"resultscrollArea")
        self.resultscrollArea.setMinimumSize(QSize(500, 300))
        self.resultscrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 498, 298))
        self.verticalLayout_5 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.resultscrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_3.addWidget(self.resultscrollArea)


        self.verticalLayout_2.addWidget(self.widget_3)


        self.horizontalLayout_3.addWidget(self.widget)


        self.verticalLayout_8.addWidget(self.widget_5)

        self.widget_7 = QWidget(self.widget_10)
        self.widget_7.setObjectName(u"widget_7")
        self.horizontalLayout_5 = QHBoxLayout(self.widget_7)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.processhorizontalSlider = QSlider(self.widget_7)
        self.processhorizontalSlider.setObjectName(u"processhorizontalSlider")
        self.processhorizontalSlider.setOrientation(Qt.Horizontal)

        self.horizontalLayout_5.addWidget(self.processhorizontalSlider)

        self.frame_3 = QFrame(self.widget_7)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.VLine)
        self.frame_3.setFrameShadow(QFrame.Raised)

        self.horizontalLayout_5.addWidget(self.frame_3)

        self.timelabel = QLabel(self.widget_7)
        self.timelabel.setObjectName(u"timelabel")

        self.horizontalLayout_5.addWidget(self.timelabel)


        self.verticalLayout_8.addWidget(self.widget_7)

        self.widget_4 = QWidget(self.widget_10)
        self.widget_4.setObjectName(u"widget_4")
        self.horizontalLayout_2 = QHBoxLayout(self.widget_4)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.voicepushButton = QPushButton(self.widget_4)
        self.voicepushButton.setObjectName(u"voicepushButton")

        self.horizontalLayout_2.addWidget(self.voicepushButton)

        self.voicehorizontalSlider = QSlider(self.widget_4)
        self.voicehorizontalSlider.setObjectName(u"voicehorizontalSlider")
        self.voicehorizontalSlider.setOrientation(Qt.Horizontal)

        self.horizontalLayout_2.addWidget(self.voicehorizontalSlider)

        self.lastpushButton = QPushButton(self.widget_4)
        self.lastpushButton.setObjectName(u"lastpushButton")

        self.horizontalLayout_2.addWidget(self.lastpushButton)

        self.playpushButton = QPushButton(self.widget_4)
        self.playpushButton.setObjectName(u"playpushButton")

        self.horizontalLayout_2.addWidget(self.playpushButton)

        self.nextpushButton = QPushButton(self.widget_4)
        self.nextpushButton.setObjectName(u"nextpushButton")

        self.horizontalLayout_2.addWidget(self.nextpushButton)

        self.modepushButton = QPushButton(self.widget_4)
        self.modepushButton.setObjectName(u"modepushButton")

        self.horizontalLayout_2.addWidget(self.modepushButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.downloadtoolButton = QToolButton(self.widget_4)
        self.downloadtoolButton.setObjectName(u"downloadtoolButton")

        self.horizontalLayout_2.addWidget(self.downloadtoolButton)

        self.hideandshowpushButton = QPushButton(self.widget_4)
        self.hideandshowpushButton.setObjectName(u"hideandshowpushButton")

        self.horizontalLayout_2.addWidget(self.hideandshowpushButton)


        self.verticalLayout_8.addWidget(self.widget_4)


        self.horizontalLayout_7.addWidget(self.widget_10)

        self.downloadgroupBox = QGroupBox(self.centralwidget)
        self.downloadgroupBox.setObjectName(u"downloadgroupBox")
        self.verticalLayout_4 = QVBoxLayout(self.downloadgroupBox)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.downloadlistView = QListView(self.downloadgroupBox)
        self.downloadlistView.setObjectName(u"downloadlistView")
        self.downloadlistView.setMinimumSize(QSize(300, 0))
        self.downloadlistView.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.verticalLayout_4.addWidget(self.downloadlistView)


        self.horizontalLayout_7.addWidget(self.downloadgroupBox)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1242, 22))
        self.menu = QMenu(self.menubar)
        self.menu.setObjectName(u"menu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menu.menuAction())
        self.menu.addAction(self.action_bat)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MusicPlayer", None))
        self.action_bat.setText(QCoreApplication.translate("MainWindow", u"\u5bfc\u51fabat\u811a\u672c\u6587\u4ef6", None))
        self.listengroupBox.setTitle(QCoreApplication.translate("MainWindow", u"\u64ad\u653e\u5217\u8868", None))
        self.musicercomboBox.setItemText(0, QCoreApplication.translate("MainWindow", u"\u54aa\u5495", None))
        self.musicercomboBox.setItemText(1, QCoreApplication.translate("MainWindow", u"\u7f51\u6613\u4e91", None))
        self.musicercomboBox.setItemText(2, QCoreApplication.translate("MainWindow", u"\u9177\u72d7", None))

        self.searchButton.setText("")
        self.timelabel.setText(QCoreApplication.translate("MainWindow", u"--/--", None))
        self.voicepushButton.setText("")
        self.lastpushButton.setText("")
        self.playpushButton.setText("")
        self.nextpushButton.setText("")
        self.modepushButton.setText("")
        self.downloadtoolButton.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.hideandshowpushButton.setText("")
        self.downloadgroupBox.setTitle(QCoreApplication.translate("MainWindow", u"\u4e0b\u8f7d\u5217\u8868", None))
        self.menu.setTitle(QCoreApplication.translate("MainWindow", u"\u8bbe\u7f6e", None))
    # retranslateUi

