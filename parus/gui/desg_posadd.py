# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'desg_posadd.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QComboBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSizePolicy, QSpacerItem,
                               QVBoxLayout, QWidget)


class Ui_PosAddWindow(object):
    def setupUi(self, PosAddWindow):
        if not PosAddWindow.objectName():
            PosAddWindow.setObjectName(u"PosAddWindow")
        PosAddWindow.resize(400, 150)
        PosAddWindow.setMinimumSize(QSize(400, 150))
        PosAddWindow.setMaximumSize(QSize(16777215, 150))
        self.centralWidget = QWidget(PosAddWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.centralLayout = QVBoxLayout(self.centralWidget)
        self.centralLayout.setObjectName(u"centralLayout")
        self.wfmLayout = QVBoxLayout()
        self.wfmLayout.setSpacing(0)
        self.wfmLayout.setObjectName(u"wfmLayout")
        self.wfmLabel = QLabel(self.centralWidget)
        self.wfmLabel.setObjectName(u"wfmLabel")
        self.wfmLabel.setMinimumSize(QSize(200, 16))
        self.wfmLabel.setMaximumSize(QSize(16777215, 16))

        self.wfmLayout.addWidget(self.wfmLabel)

        self.wfmCombo = QComboBox(self.centralWidget)
        self.wfmCombo.setObjectName(u"wfmCombo")
        self.wfmCombo.setMinimumSize(QSize(200, 22))

        self.wfmLayout.addWidget(self.wfmCombo)


        self.centralLayout.addLayout(self.wfmLayout)

        self.cidLayout = QVBoxLayout()
        self.cidLayout.setSpacing(0)
        self.cidLayout.setObjectName(u"cidLayout")
        self.cidLabel = QLabel(self.centralWidget)
        self.cidLabel.setObjectName(u"cidLabel")
        self.cidLabel.setMinimumSize(QSize(200, 16))
        self.cidLabel.setMaximumSize(QSize(16, 16777215))

        self.cidLayout.addWidget(self.cidLabel)

        self.cidNameLayout = QHBoxLayout()
        self.cidNameLayout.setSpacing(20)
        self.cidNameLayout.setObjectName(u"cidNameLayout")
        self.cidLine = QLineEdit(self.centralWidget)
        self.cidLine.setObjectName(u"cidLine")
        self.cidLine.setMinimumSize(QSize(120, 22))

        self.cidNameLayout.addWidget(self.cidLine)

        self.cidStatus = QLabel(self.centralWidget)
        self.cidStatus.setObjectName(u"cidStatus")
        self.cidStatus.setMinimumSize(QSize(60, 22))
        self.cidStatus.setMaximumSize(QSize(60, 22))
        font = QFont()
        font.setBold(True)
        self.cidStatus.setFont(font)

        self.cidNameLayout.addWidget(self.cidStatus)


        self.cidLayout.addLayout(self.cidNameLayout)


        self.centralLayout.addLayout(self.cidLayout)

        self.ctrlLayout = QHBoxLayout()
        self.ctrlLayout.setObjectName(u"ctrlLayout")
        self.addButton = QPushButton(self.centralWidget)
        self.addButton.setObjectName(u"addButton")
        self.addButton.setMinimumSize(QSize(75, 25))
        self.addButton.setMaximumSize(QSize(16777215, 25))

        self.ctrlLayout.addWidget(self.addButton)

        self.ctrlSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.ctrlLayout.addItem(self.ctrlSpacer)

        self.cancelButton = QPushButton(self.centralWidget)
        self.cancelButton.setObjectName(u"cancelButton")
        self.cancelButton.setMinimumSize(QSize(75, 25))
        self.cancelButton.setMaximumSize(QSize(16777215, 25))

        self.ctrlLayout.addWidget(self.cancelButton)


        self.centralLayout.addLayout(self.ctrlLayout)

        PosAddWindow.setCentralWidget(self.centralWidget)

        self.retranslateUi(PosAddWindow)

        QMetaObject.connectSlotsByName(PosAddWindow)
    # setupUi

    def retranslateUi(self, PosAddWindow):
        PosAddWindow.setWindowTitle(QCoreApplication.translate("PosAddWindow", u"Add Neuron", None))
        self.wfmLabel.setText(QCoreApplication.translate("PosAddWindow", u"Spike Waveform", None))
        self.cidLabel.setText(QCoreApplication.translate("PosAddWindow", u"Cell Name", None))
        self.cidLine.setPlaceholderText(QCoreApplication.translate("PosAddWindow",
                                                                   u"Letters, digits and underscores only. "
                                                                   u"Start with letter.", None))
        self.cidStatus.setText(QCoreApplication.translate("PosAddWindow",
                                                          u"<html><head/><body><p>"
                                                          u"<span style=\"color:#ff0000;\">Invalid<"
                                                          u"/span></p></body></html>", None))
        self.addButton.setText(QCoreApplication.translate("PosAddWindow", u"Add", None))
        self.cancelButton.setText(QCoreApplication.translate("PosAddWindow", u"Cancel", None))
    # retranslateUi

