# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_login.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(287, 258)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.widget = QWidget(Dialog)
        self.widget.setObjectName(u"widget")
        self.verticalLayout_2 = QVBoxLayout(self.widget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.widget_2 = QWidget(self.widget)
        self.widget_2.setObjectName(u"widget_2")
        self.horizontalLayout = QHBoxLayout(self.widget_2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.widget_2)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.loginidlineEdit = QLineEdit(self.widget_2)
        self.loginidlineEdit.setObjectName(u"loginidlineEdit")

        self.horizontalLayout.addWidget(self.loginidlineEdit)


        self.verticalLayout_2.addWidget(self.widget_2)

        self.frame = QFrame(self.widget)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.HLine)
        self.frame.setFrameShadow(QFrame.Raised)

        self.verticalLayout_2.addWidget(self.frame)

        self.widget_3 = QWidget(self.widget)
        self.widget_3.setObjectName(u"widget_3")
        self.horizontalLayout_2 = QHBoxLayout(self.widget_3)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_2 = QLabel(self.widget_3)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_2.addWidget(self.label_2)

        self.passwordlineEdit = QLineEdit(self.widget_3)
        self.passwordlineEdit.setObjectName(u"passwordlineEdit")
        self.passwordlineEdit.setEchoMode(QLineEdit.Password)

        self.horizontalLayout_2.addWidget(self.passwordlineEdit)


        self.verticalLayout_2.addWidget(self.widget_3)

        self.verifywidget = QWidget(self.widget)
        self.verifywidget.setObjectName(u"verifywidget")
        self.verifywidget.setEnabled(True)
        self.verticalLayout_3 = QVBoxLayout(self.verifywidget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.frame_2 = QFrame(self.verifywidget)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.HLine)
        self.frame_2.setFrameShadow(QFrame.Raised)

        self.verticalLayout_3.addWidget(self.frame_2)

        self.widget_4 = QWidget(self.verifywidget)
        self.widget_4.setObjectName(u"widget_4")
        self.horizontalLayout_4 = QHBoxLayout(self.widget_4)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_3 = QLabel(self.widget_4)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_4.addWidget(self.label_3)

        self.verifylineEdit = QLineEdit(self.widget_4)
        self.verifylineEdit.setObjectName(u"verifylineEdit")

        self.horizontalLayout_4.addWidget(self.verifylineEdit, 0, Qt.AlignHCenter)

        self.verifyimglabel = QLabel(self.widget_4)
        self.verifyimglabel.setObjectName(u"verifyimglabel")

        self.horizontalLayout_4.addWidget(self.verifyimglabel)


        self.verticalLayout_3.addWidget(self.widget_4)


        self.verticalLayout_2.addWidget(self.verifywidget)

        self.messagelabel = QLabel(self.widget)
        self.messagelabel.setObjectName(u"messagelabel")
        self.messagelabel.setFrameShape(QFrame.NoFrame)
        self.messagelabel.setFrameShadow(QFrame.Raised)

        self.verticalLayout_2.addWidget(self.messagelabel)


        self.verticalLayout.addWidget(self.widget)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"\u8d26\u53f7:", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"\u5bc6\u7801:", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"\u9a8c\u8bc1\u7801:", None))
        self.verifyimglabel.setText("")
        self.messagelabel.setText("")
    # retranslateUi

