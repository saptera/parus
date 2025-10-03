# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'desg_sysset.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QButtonGroup, QGroupBox, QHBoxLayout, QLineEdit, QPushButton, QRadioButton,
                               QVBoxLayout, QWidget)


class Ui_SysSetWindow(object):
    def setupUi(self, SysSetWindow):
        if not SysSetWindow.objectName():
            SysSetWindow.setObjectName(u"SysSetWindow")
        SysSetWindow.resize(600, 145)
        SysSetWindow.setMinimumSize(QSize(600, 145))
        SysSetWindow.setMaximumSize(QSize(16777215, 145))
        self.centralWidget = QWidget(SysSetWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.verticalLayout = QVBoxLayout(self.centralWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.cwdBox = QGroupBox(self.centralWidget)
        self.cwdBox.setObjectName(u"cwdBox")
        self.cwdBox.setMinimumSize(QSize(300, 60))
        self.cwdBox.setMaximumSize(QSize(16777215, 60))
        font = QFont()
        font.setBold(True)
        self.cwdBox.setFont(font)
        self.cwdBoxLayout = QHBoxLayout(self.cwdBox)
        self.cwdBoxLayout.setSpacing(10)
        self.cwdBoxLayout.setObjectName(u"cwdBoxLayout")
        self.cwdPath = QLineEdit(self.cwdBox)
        self.cwdPath.setObjectName(u"cwdPath")
        self.cwdPath.setMinimumSize(QSize(0, 22))
        self.cwdPath.setMaximumSize(QSize(16777215, 22))
        font1 = QFont()
        font1.setBold(False)
        self.cwdPath.setFont(font1)
        self.cwdPath.setReadOnly(True)

        self.cwdBoxLayout.addWidget(self.cwdPath)

        self.cwdSelect = QPushButton(self.cwdBox)
        self.cwdSelect.setObjectName(u"cwdSelect")
        self.cwdSelect.setMinimumSize(QSize(80, 24))
        self.cwdSelect.setMaximumSize(QSize(80, 24))
        self.cwdSelect.setFont(font1)

        self.cwdBoxLayout.addWidget(self.cwdSelect)


        self.verticalLayout.addWidget(self.cwdBox)

        self.csButtonBox = QGroupBox(self.centralWidget)
        self.csButtonBox.setObjectName(u"csButtonBox")
        self.csButtonBox.setMinimumSize(QSize(300, 60))
        self.csButtonBox.setMaximumSize(QSize(16777215, 60))
        self.csButtonBox.setFont(font)
        self.csBoxLayout = QHBoxLayout(self.csButtonBox)
        self.csBoxLayout.setObjectName(u"csBoxLayout")
        self.csAuto = QRadioButton(self.csButtonBox)
        self.csButtonGroup = QButtonGroup(SysSetWindow)
        self.csButtonGroup.setObjectName(u"csButtonGroup")
        self.csButtonGroup.addButton(self.csAuto)
        self.csAuto.setObjectName(u"csAuto")
        self.csAuto.setMinimumSize(QSize(50, 0))
        self.csAuto.setFont(font1)
        self.csAuto.setChecked(True)

        self.csBoxLayout.addWidget(self.csAuto)

        self.csLight = QRadioButton(self.csButtonBox)
        self.csButtonGroup.addButton(self.csLight)
        self.csLight.setObjectName(u"csLight")
        self.csLight.setMinimumSize(QSize(50, 0))
        self.csLight.setFont(font1)

        self.csBoxLayout.addWidget(self.csLight)

        self.csDark = QRadioButton(self.csButtonBox)
        self.csButtonGroup.addButton(self.csDark)
        self.csDark.setObjectName(u"csDark")
        self.csDark.setMinimumSize(QSize(50, 0))
        self.csDark.setFont(font1)

        self.csBoxLayout.addWidget(self.csDark)


        self.verticalLayout.addWidget(self.csButtonBox)

        SysSetWindow.setCentralWidget(self.centralWidget)

        self.retranslateUi(SysSetWindow)

        QMetaObject.connectSlotsByName(SysSetWindow)
    # setupUi

    def retranslateUi(self, SysSetWindow):
        SysSetWindow.setWindowTitle(QCoreApplication.translate("SysSetWindow", u"System Settings", None))
        self.cwdBox.setTitle(QCoreApplication.translate("SysSetWindow", u"Default Working Directory", None))
        self.cwdPath.setPlaceholderText(QCoreApplication.translate("SysSetWindow", u"Select a valid path", None))
        self.cwdSelect.setText(QCoreApplication.translate("SysSetWindow", u"Open", None))
        self.csButtonBox.setTitle(QCoreApplication.translate("SysSetWindow", u"Colour Scheme", None))
        self.csAuto.setText(QCoreApplication.translate("SysSetWindow", u"Auto", None))
        self.csLight.setText(QCoreApplication.translate("SysSetWindow", u"Light", None))
        self.csDark.setText(QCoreApplication.translate("SysSetWindow", u"Dark", None))
    # retranslateUi

