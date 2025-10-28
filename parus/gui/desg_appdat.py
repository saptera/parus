# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'desg_appdat.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QSpacerItem, QToolButton,
                               QVBoxLayout, QWidget)


class Ui_ParusDatWindow(object):
    def setupUi(self, ParusDatWindow):
        if not ParusDatWindow.objectName():
            ParusDatWindow.setObjectName(u"ParusDatWindow")
        ParusDatWindow.resize(830, 470)
        ParusDatWindow.setMinimumSize(QSize(830, 470))
        ParusDatWindow.setMaximumSize(QSize(830, 470))
        self.centralWidget = QWidget(ParusDatWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.centralLayout = QVBoxLayout(self.centralWidget)
        self.centralLayout.setObjectName(u"centralLayout")
        self.settingLayout = QHBoxLayout()
        self.settingLayout.setSpacing(0)
        self.settingLayout.setObjectName(u"settingLayout")
        self.settingSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.settingLayout.addItem(self.settingSpacer)

        self.settingButton = QToolButton(self.centralWidget)
        self.settingButton.setObjectName(u"settingButton")
        self.settingButton.setMinimumSize(QSize(30, 20))
        self.settingButton.setMaximumSize(QSize(30, 20))

        self.settingLayout.addWidget(self.settingButton)


        self.centralLayout.addLayout(self.settingLayout)

        self.logoFrame = QFrame(self.centralWidget)
        self.logoFrame.setObjectName(u"logoFrame")
        self.logoFrame.setMinimumSize(QSize(540, 150))
        self.logoFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.logoFrame.setFrameShadow(QFrame.Shadow.Plain)
        self.logoLayout = QVBoxLayout(self.logoFrame)
        self.logoLayout.setSpacing(0)
        self.logoLayout.setObjectName(u"logoLayout")
        self.logoLayout.setContentsMargins(0, 0, 0, 0)

        self.centralLayout.addWidget(self.logoFrame)

        self.titleLayout = QHBoxLayout()
        self.titleLayout.setObjectName(u"titleLayout")
        self.titleLineL = QFrame(self.centralWidget)
        self.titleLineL.setObjectName(u"titleLineL")
        self.titleLineL.setMinimumSize(QSize(100, 0))
        self.titleLineL.setFrameShadow(QFrame.Shadow.Sunken)
        self.titleLineL.setFrameShape(QFrame.Shape.HLine)

        self.titleLayout.addWidget(self.titleLineL)

        self.titleLabel = QLabel(self.centralWidget)
        self.titleLabel.setObjectName(u"titleLabel")
        self.titleLabel.setMinimumSize(QSize(200, 30))
        self.titleLabel.setMaximumSize(QSize(16777215, 30))
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setItalic(True)
        self.titleLabel.setFont(font)
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.titleLayout.addWidget(self.titleLabel)

        self.titleLineR = QFrame(self.centralWidget)
        self.titleLineR.setObjectName(u"titleLineR")
        self.titleLineR.setMinimumSize(QSize(100, 0))
        self.titleLineR.setFrameShadow(QFrame.Shadow.Sunken)
        self.titleLineR.setFrameShape(QFrame.Shape.HLine)

        self.titleLayout.addWidget(self.titleLineR)

        self.titleLayout.setStretch(0, 1)
        self.titleLayout.setStretch(2, 1)

        self.centralLayout.addLayout(self.titleLayout)

        self.ctrlFrame = QFrame(self.centralWidget)
        self.ctrlFrame.setObjectName(u"ctrlFrame")
        self.ctrlFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.ctrlFrame.setFrameShadow(QFrame.Shadow.Plain)
        self.ctrlLayout = QVBoxLayout(self.ctrlFrame)
        self.ctrlLayout.setObjectName(u"ctrlLayout")
        self.modInfButton = QPushButton(self.ctrlFrame)
        self.modInfButton.setObjectName(u"modInfButton")
        self.modInfButton.setMinimumSize(QSize(300, 40))
        self.modInfButton.setMaximumSize(QSize(16777215, 40))
        font1 = QFont()
        font1.setPointSize(16)
        font1.setBold(True)
        self.modInfButton.setFont(font1)

        self.ctrlLayout.addWidget(self.modInfButton)

        self.spkSrtButton = QPushButton(self.ctrlFrame)
        self.spkSrtButton.setObjectName(u"spkSrtButton")
        self.spkSrtButton.setMinimumSize(QSize(300, 40))
        self.spkSrtButton.setMaximumSize(QSize(16777215, 40))
        self.spkSrtButton.setFont(font1)

        self.ctrlLayout.addWidget(self.spkSrtButton)

        self.resVerButton = QPushButton(self.ctrlFrame)
        self.resVerButton.setObjectName(u"resVerButton")
        self.resVerButton.setMinimumSize(QSize(300, 40))
        self.resVerButton.setMaximumSize(QSize(16777215, 40))
        self.resVerButton.setFont(font1)

        self.ctrlLayout.addWidget(self.resVerButton)


        self.centralLayout.addWidget(self.ctrlFrame)

        self.centralLayout.setStretch(1, 1)
        ParusDatWindow.setCentralWidget(self.centralWidget)

        self.retranslateUi(ParusDatWindow)

        QMetaObject.connectSlotsByName(ParusDatWindow)
    # setupUi

    def retranslateUi(self, ParusDatWindow):
        ParusDatWindow.setWindowTitle(QCoreApplication.translate("ParusDatWindow", u"Parus Data Pipeline", None))
        self.settingButton.setText(QCoreApplication.translate("ParusDatWindow", u"...", None))
        self.titleLabel.setText(QCoreApplication.translate("ParusDatWindow", u"Data Processing", None))
        self.modInfButton.setText(QCoreApplication.translate("ParusDatWindow", u"Signal Separation", None))
        self.spkSrtButton.setText(QCoreApplication.translate("ParusDatWindow", u"Spike Sorting", None))
        self.resVerButton.setText(QCoreApplication.translate("ParusDatWindow", u"View Results", None))
    # retranslateUi

