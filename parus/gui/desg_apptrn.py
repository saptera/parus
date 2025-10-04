# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'desg_apptrn.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QSpacerItem, QToolButton,
                               QVBoxLayout, QWidget)


class Ui_ParusTrnWindow(object):
    def setupUi(self, ParusTrnWindow):
        if not ParusTrnWindow.objectName():
            ParusTrnWindow.setObjectName(u"ParusTrnWindow")
        ParusTrnWindow.resize(830, 470)
        ParusTrnWindow.setMinimumSize(QSize(830, 470))
        ParusTrnWindow.setMaximumSize(QSize(830, 470))
        self.centralWidget = QWidget(ParusTrnWindow)
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
        self.arcMksButton = QPushButton(self.ctrlFrame)
        self.arcMksButton.setObjectName(u"arcMksButton")
        self.arcMksButton.setMinimumSize(QSize(300, 40))
        self.arcMksButton.setMaximumSize(QSize(16777215, 40))
        font1 = QFont()
        font1.setPointSize(16)
        font1.setBold(True)
        self.arcMksButton.setFont(font1)

        self.ctrlLayout.addWidget(self.arcMksButton)

        self.datGenButton = QPushButton(self.ctrlFrame)
        self.datGenButton.setObjectName(u"datGenButton")
        self.datGenButton.setMinimumSize(QSize(300, 40))
        self.datGenButton.setMaximumSize(QSize(16777215, 40))
        self.datGenButton.setFont(font1)

        self.ctrlLayout.addWidget(self.datGenButton)

        self.modTrnButton = QPushButton(self.ctrlFrame)
        self.modTrnButton.setObjectName(u"modTrnButton")
        self.modTrnButton.setMinimumSize(QSize(300, 40))
        self.modTrnButton.setMaximumSize(QSize(16777215, 40))
        self.modTrnButton.setFont(font1)

        self.ctrlLayout.addWidget(self.modTrnButton)


        self.centralLayout.addWidget(self.ctrlFrame)

        self.centralLayout.setStretch(1, 1)
        ParusTrnWindow.setCentralWidget(self.centralWidget)

        self.retranslateUi(ParusTrnWindow)

        QMetaObject.connectSlotsByName(ParusTrnWindow)
    # setupUi

    def retranslateUi(self, ParusTrnWindow):
        ParusTrnWindow.setWindowTitle(QCoreApplication.translate("ParusTrnWindow", u"Parus Model Training", None))
        self.settingButton.setText(QCoreApplication.translate("ParusTrnWindow", u"...", None))
        self.titleLabel.setText(QCoreApplication.translate("ParusTrnWindow", u"Model Training", None))
        self.arcMksButton.setText(QCoreApplication.translate("ParusTrnWindow", u"Create Archive Signal", None))
        self.datGenButton.setText(QCoreApplication.translate("ParusTrnWindow", u"Dataset Generation", None))
        self.modTrnButton.setText(QCoreApplication.translate("ParusTrnWindow", u"Model Training", None))
    # retranslateUi

