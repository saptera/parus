# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'desg_arcmrk.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QComboBox, QDateEdit, QFrame, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                               QSpinBox, QStatusBar, QTimeEdit, QVBoxLayout, QWidget)


class Ui_ParusArcWindow(object):
    def setupUi(self, ParusArcWindow):
        if not ParusArcWindow.objectName():
            ParusArcWindow.setObjectName(u"ParusArcWindow")
        ParusArcWindow.resize(760, 950)
        ParusArcWindow.setMinimumSize(QSize(760, 950))
        ParusArcWindow.setMaximumSize(QSize(16777215, 950))
        self.centralWidget = QWidget(ParusArcWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.centralLayout = QVBoxLayout(self.centralWidget)
        self.centralLayout.setObjectName(u"centralLayout")
        self.dataFrame = QFrame(self.centralWidget)
        self.dataFrame.setObjectName(u"dataFrame")
        self.dataFrame.setMinimumSize(QSize(740, 220))
        self.dataFrame.setMaximumSize(QSize(16777215, 220))
        self.dataFrame.setFrameShape(QFrame.Shape.Box)
        self.dataFrame.setFrameShadow(QFrame.Shadow.Sunken)
        self.dataLayout = QVBoxLayout(self.dataFrame)
        self.dataLayout.setObjectName(u"dataLayout")
        self.dataLayout.setContentsMargins(-1, 0, -1, 6)
        self.dataLabel = QLabel(self.dataFrame)
        self.dataLabel.setObjectName(u"dataLabel")
        self.dataLabel.setMinimumSize(QSize(200, 25))
        self.dataLabel.setMaximumSize(QSize(16777215, 25))
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.dataLabel.setFont(font)

        self.dataLayout.addWidget(self.dataLabel)

        self.dataLine = QFrame(self.dataFrame)
        self.dataLine.setObjectName(u"dataLine")
        self.dataLine.setMinimumSize(QSize(200, 0))
        self.dataLine.setFrameShape(QFrame.Shape.HLine)
        self.dataLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.dataLayout.addWidget(self.dataLine)

        self.srcFileBox = QGroupBox(self.dataFrame)
        self.srcFileBox.setObjectName(u"srcFileBox")
        self.srcFileBox.setMinimumSize(QSize(650, 55))
        self.srcFileBox.setMaximumSize(QSize(16777215, 55))
        font1 = QFont()
        font1.setBold(True)
        self.srcFileBox.setFont(font1)
        self.srcBoxLayout = QHBoxLayout(self.srcFileBox)
        self.srcBoxLayout.setSpacing(10)
        self.srcBoxLayout.setObjectName(u"srcBoxLayout")
        self.srcBoxLayout.setContentsMargins(-1, 6, -1, 6)
        self.srcFilePath = QLineEdit(self.srcFileBox)
        self.srcFilePath.setObjectName(u"srcFilePath")
        self.srcFilePath.setMinimumSize(QSize(500, 25))
        self.srcFilePath.setMaximumSize(QSize(16777215, 25))
        font2 = QFont()
        font2.setPointSize(9)
        font2.setBold(False)
        self.srcFilePath.setFont(font2)

        self.srcBoxLayout.addWidget(self.srcFilePath)

        self.srcFileSelect = QPushButton(self.srcFileBox)
        self.srcFileSelect.setObjectName(u"srcFileSelect")
        self.srcFileSelect.setMinimumSize(QSize(80, 24))
        self.srcFileSelect.setMaximumSize(QSize(80, 24))
        font3 = QFont()
        font3.setPointSize(9)
        font3.setBold(True)
        self.srcFileSelect.setFont(font3)

        self.srcBoxLayout.addWidget(self.srcFileSelect)


        self.dataLayout.addWidget(self.srcFileBox)

        self.datSelLayout = QHBoxLayout()
        self.datSelLayout.setObjectName(u"datSelLayout")
        self.datSelLayout.setContentsMargins(9, -1, 9, -1)
        self.datChnLayout = QVBoxLayout()
        self.datChnLayout.setSpacing(0)
        self.datChnLayout.setObjectName(u"datChnLayout")
        self.datChnLabel = QLabel(self.dataFrame)
        self.datChnLabel.setObjectName(u"datChnLabel")
        self.datChnLabel.setMinimumSize(QSize(0, 20))
        self.datChnLabel.setMaximumSize(QSize(16777215, 20))
        self.datChnLabel.setFont(font3)

        self.datChnLayout.addWidget(self.datChnLabel)

        self.datChnCombo = QComboBox(self.dataFrame)
        self.datChnCombo.setObjectName(u"datChnCombo")
        self.datChnCombo.setMinimumSize(QSize(120, 25))
        self.datChnCombo.setMaximumSize(QSize(120, 25))
        self.datChnCombo.setFont(font2)

        self.datChnLayout.addWidget(self.datChnCombo)


        self.datSelLayout.addLayout(self.datChnLayout)

        self.datWfmLayout = QVBoxLayout()
        self.datWfmLayout.setSpacing(0)
        self.datWfmLayout.setObjectName(u"datWfmLayout")
        self.datWfmLabel = QLabel(self.dataFrame)
        self.datWfmLabel.setObjectName(u"datWfmLabel")
        self.datWfmLabel.setMinimumSize(QSize(0, 20))
        self.datWfmLabel.setMaximumSize(QSize(16777215, 20))
        self.datWfmLabel.setFont(font3)

        self.datWfmLayout.addWidget(self.datWfmLabel)

        self.datWfmCombo = QComboBox(self.dataFrame)
        self.datWfmCombo.setObjectName(u"datWfmCombo")
        self.datWfmCombo.setMinimumSize(QSize(120, 25))
        self.datWfmCombo.setMaximumSize(QSize(120, 25))
        self.datWfmCombo.setFont(font2)

        self.datWfmLayout.addWidget(self.datWfmCombo)


        self.datSelLayout.addLayout(self.datWfmLayout)

        self.datSpkLayout = QVBoxLayout()
        self.datSpkLayout.setSpacing(0)
        self.datSpkLayout.setObjectName(u"datSpkLayout")
        self.datSpkLabel = QLabel(self.dataFrame)
        self.datSpkLabel.setObjectName(u"datSpkLabel")
        self.datSpkLabel.setMinimumSize(QSize(0, 20))
        self.datSpkLabel.setMaximumSize(QSize(16777215, 20))
        self.datSpkLabel.setFont(font3)

        self.datSpkLayout.addWidget(self.datSpkLabel)

        self.datSpkCombo = QComboBox(self.dataFrame)
        self.datSpkCombo.setObjectName(u"datSpkCombo")
        self.datSpkCombo.setMinimumSize(QSize(120, 25))
        self.datSpkCombo.setMaximumSize(QSize(120, 25))
        self.datSpkCombo.setFont(font2)

        self.datSpkLayout.addWidget(self.datSpkCombo)


        self.datSelLayout.addLayout(self.datSpkLayout)

        self.smpAntLayout = QVBoxLayout()
        self.smpAntLayout.setSpacing(0)
        self.smpAntLayout.setObjectName(u"smpAntLayout")
        self.smpAntLabel = QLabel(self.dataFrame)
        self.smpAntLabel.setObjectName(u"smpAntLabel")
        self.smpAntLabel.setMinimumSize(QSize(0, 20))
        self.smpAntLabel.setMaximumSize(QSize(16777215, 20))
        self.smpAntLabel.setFont(font3)

        self.smpAntLayout.addWidget(self.smpAntLabel)

        self.smpAntSpinbox = QSpinBox(self.dataFrame)
        self.smpAntSpinbox.setObjectName(u"smpAntSpinbox")
        self.smpAntSpinbox.setMinimumSize(QSize(120, 25))
        self.smpAntSpinbox.setMaximumSize(QSize(16777215, 25))
        self.smpAntSpinbox.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.smpAntSpinbox.setMaximum(10000)
        self.smpAntSpinbox.setValue(10)

        self.smpAntLayout.addWidget(self.smpAntSpinbox)


        self.datSelLayout.addLayout(self.smpAntLayout)

        self.smpPstLayout = QVBoxLayout()
        self.smpPstLayout.setSpacing(0)
        self.smpPstLayout.setObjectName(u"smpPstLayout")
        self.smpPstLabel = QLabel(self.dataFrame)
        self.smpPstLabel.setObjectName(u"smpPstLabel")
        self.smpPstLabel.setMinimumSize(QSize(0, 20))
        self.smpPstLabel.setMaximumSize(QSize(16777215, 20))
        self.smpPstLabel.setFont(font3)

        self.smpPstLayout.addWidget(self.smpPstLabel)

        self.smpPstSpinbox = QSpinBox(self.dataFrame)
        self.smpPstSpinbox.setObjectName(u"smpPstSpinbox")
        self.smpPstSpinbox.setMinimumSize(QSize(120, 25))
        self.smpPstSpinbox.setMaximumSize(QSize(16777215, 25))
        self.smpPstSpinbox.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.smpPstSpinbox.setMaximum(100000)
        self.smpPstSpinbox.setValue(20)

        self.smpPstLayout.addWidget(self.smpPstSpinbox)


        self.datSelLayout.addLayout(self.smpPstLayout)


        self.dataLayout.addLayout(self.datSelLayout)

        self.dstDirBox = QGroupBox(self.dataFrame)
        self.dstDirBox.setObjectName(u"dstDirBox")
        self.dstDirBox.setMinimumSize(QSize(650, 55))
        self.dstDirBox.setMaximumSize(QSize(16777215, 55))
        self.dstDirBox.setFont(font1)
        self.dstBoxLayout = QHBoxLayout(self.dstDirBox)
        self.dstBoxLayout.setSpacing(10)
        self.dstBoxLayout.setObjectName(u"dstBoxLayout")
        self.dstBoxLayout.setContentsMargins(-1, 6, -1, 6)
        self.dstDirPath = QLineEdit(self.dstDirBox)
        self.dstDirPath.setObjectName(u"dstDirPath")
        self.dstDirPath.setMinimumSize(QSize(500, 25))
        self.dstDirPath.setMaximumSize(QSize(16777215, 25))
        self.dstDirPath.setFont(font2)

        self.dstBoxLayout.addWidget(self.dstDirPath)

        self.dstDirSelect = QPushButton(self.dstDirBox)
        self.dstDirSelect.setObjectName(u"dstDirSelect")
        self.dstDirSelect.setMinimumSize(QSize(80, 24))
        self.dstDirSelect.setMaximumSize(QSize(80, 24))
        self.dstDirSelect.setFont(font3)

        self.dstBoxLayout.addWidget(self.dstDirSelect)


        self.dataLayout.addWidget(self.dstDirBox)


        self.centralLayout.addWidget(self.dataFrame)

        self.metaFrame = QFrame(self.centralWidget)
        self.metaFrame.setObjectName(u"metaFrame")
        self.metaFrame.setMinimumSize(QSize(740, 640))
        self.metaFrame.setMaximumSize(QSize(16777215, 640))
        self.metaFrame.setFrameShape(QFrame.Shape.Box)
        self.metaFrame.setFrameShadow(QFrame.Shadow.Sunken)
        self.metaLayout = QVBoxLayout(self.metaFrame)
        self.metaLayout.setObjectName(u"metaLayout")
        self.metaLayout.setContentsMargins(-1, 0, -1, 6)
        self.metaLabel = QLabel(self.metaFrame)
        self.metaLabel.setObjectName(u"metaLabel")
        self.metaLabel.setMinimumSize(QSize(200, 25))
        self.metaLabel.setMaximumSize(QSize(16777215, 25))
        self.metaLabel.setFont(font)

        self.metaLayout.addWidget(self.metaLabel)

        self.metaLine = QFrame(self.metaFrame)
        self.metaLine.setObjectName(u"metaLine")
        self.metaLine.setMinimumSize(QSize(200, 0))
        self.metaLine.setFrameShape(QFrame.Shape.HLine)
        self.metaLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.metaLayout.addWidget(self.metaLine)

        self.ognGroup = QGroupBox(self.metaFrame)
        self.ognGroup.setObjectName(u"ognGroup")
        self.ognGroup.setMinimumSize(QSize(530, 125))
        self.ognGroup.setMaximumSize(QSize(16777215, 125))
        font4 = QFont()
        font4.setPointSize(10)
        font4.setBold(True)
        self.ognGroup.setFont(font4)
        self.ognLayout = QVBoxLayout(self.ognGroup)
        self.ognLayout.setObjectName(u"ognLayout")
        self.ognLayout.setContentsMargins(-1, 0, -1, 6)
        self.ognStdLayout = QHBoxLayout()
        self.ognStdLayout.setObjectName(u"ognStdLayout")
        self.ognGenLayout = QVBoxLayout()
        self.ognGenLayout.setSpacing(0)
        self.ognGenLayout.setObjectName(u"ognGenLayout")
        self.ognGenLabel = QLabel(self.ognGroup)
        self.ognGenLabel.setObjectName(u"ognGenLabel")
        self.ognGenLabel.setMinimumSize(QSize(0, 20))
        self.ognGenLabel.setMaximumSize(QSize(16777215, 20))
        self.ognGenLabel.setFont(font3)

        self.ognGenLayout.addWidget(self.ognGenLabel)

        self.ognGenLine = QLineEdit(self.ognGroup)
        self.ognGenLine.setObjectName(u"ognGenLine")
        self.ognGenLine.setMinimumSize(QSize(120, 25))
        self.ognGenLine.setMaximumSize(QSize(16777215, 25))
        font5 = QFont()
        font5.setPointSize(9)
        font5.setBold(False)
        font5.setItalic(True)
        self.ognGenLine.setFont(font5)

        self.ognGenLayout.addWidget(self.ognGenLine)


        self.ognStdLayout.addLayout(self.ognGenLayout)

        self.ognSpcLayout = QVBoxLayout()
        self.ognSpcLayout.setSpacing(0)
        self.ognSpcLayout.setObjectName(u"ognSpcLayout")
        self.ognSpcLabel = QLabel(self.ognGroup)
        self.ognSpcLabel.setObjectName(u"ognSpcLabel")
        self.ognSpcLabel.setMinimumSize(QSize(0, 20))
        self.ognSpcLabel.setMaximumSize(QSize(16777215, 20))
        self.ognSpcLabel.setFont(font3)

        self.ognSpcLayout.addWidget(self.ognSpcLabel)

        self.ognSpcLine = QLineEdit(self.ognGroup)
        self.ognSpcLine.setObjectName(u"ognSpcLine")
        self.ognSpcLine.setMinimumSize(QSize(120, 25))
        self.ognSpcLine.setMaximumSize(QSize(16777215, 25))
        self.ognSpcLine.setFont(font5)

        self.ognSpcLayout.addWidget(self.ognSpcLine)


        self.ognStdLayout.addLayout(self.ognSpcLayout)

        self.ognStrLayout = QVBoxLayout()
        self.ognStrLayout.setSpacing(0)
        self.ognStrLayout.setObjectName(u"ognStrLayout")
        self.ognStrLabel = QLabel(self.ognGroup)
        self.ognStrLabel.setObjectName(u"ognStrLabel")
        self.ognStrLabel.setMinimumSize(QSize(0, 20))
        self.ognStrLabel.setMaximumSize(QSize(16777215, 20))
        self.ognStrLabel.setFont(font3)

        self.ognStrLayout.addWidget(self.ognStrLabel)

        self.ognStrLine = QLineEdit(self.ognGroup)
        self.ognStrLine.setObjectName(u"ognStrLine")
        self.ognStrLine.setMinimumSize(QSize(120, 25))
        self.ognStrLine.setMaximumSize(QSize(16777215, 25))
        self.ognStrLine.setFont(font2)

        self.ognStrLayout.addWidget(self.ognStrLine)


        self.ognStdLayout.addLayout(self.ognStrLayout)

        self.ognModLayout = QVBoxLayout()
        self.ognModLayout.setSpacing(0)
        self.ognModLayout.setObjectName(u"ognModLayout")
        self.ognModLabel = QLabel(self.ognGroup)
        self.ognModLabel.setObjectName(u"ognModLabel")
        self.ognModLabel.setMinimumSize(QSize(0, 20))
        self.ognModLabel.setMaximumSize(QSize(16777215, 20))
        self.ognModLabel.setFont(font3)

        self.ognModLayout.addWidget(self.ognModLabel)

        self.ognModLine = QLineEdit(self.ognGroup)
        self.ognModLine.setObjectName(u"ognModLine")
        self.ognModLine.setMinimumSize(QSize(120, 25))
        self.ognModLine.setMaximumSize(QSize(16777215, 25))
        self.ognModLine.setFont(font2)

        self.ognModLayout.addWidget(self.ognModLine)


        self.ognStdLayout.addLayout(self.ognModLayout)


        self.ognLayout.addLayout(self.ognStdLayout)

        self.ognNoteLayout = QVBoxLayout()
        self.ognNoteLayout.setSpacing(0)
        self.ognNoteLayout.setObjectName(u"ognNoteLayout")
        self.ognNoteLabel = QLabel(self.ognGroup)
        self.ognNoteLabel.setObjectName(u"ognNoteLabel")
        self.ognNoteLabel.setMinimumSize(QSize(0, 20))
        self.ognNoteLabel.setMaximumSize(QSize(16777215, 20))
        self.ognNoteLabel.setFont(font3)

        self.ognNoteLayout.addWidget(self.ognNoteLabel)

        self.ognNoteLine = QLineEdit(self.ognGroup)
        self.ognNoteLine.setObjectName(u"ognNoteLine")
        self.ognNoteLine.setMinimumSize(QSize(500, 25))
        self.ognNoteLine.setMaximumSize(QSize(16777215, 25))
        self.ognNoteLine.setFont(font2)

        self.ognNoteLayout.addWidget(self.ognNoteLine)


        self.ognLayout.addLayout(self.ognNoteLayout)


        self.metaLayout.addWidget(self.ognGroup)

        self.sigGroup = QGroupBox(self.metaFrame)
        self.sigGroup.setObjectName(u"sigGroup")
        self.sigGroup.setMinimumSize(QSize(530, 125))
        self.sigGroup.setMaximumSize(QSize(16777215, 125))
        self.sigGroup.setFont(font4)
        self.sigLayout = QVBoxLayout(self.sigGroup)
        self.sigLayout.setObjectName(u"sigLayout")
        self.sigLayout.setContentsMargins(-1, 0, -1, 6)
        self.sigStdLayout = QHBoxLayout()
        self.sigStdLayout.setObjectName(u"sigStdLayout")
        self.sigRegLayout = QVBoxLayout()
        self.sigRegLayout.setSpacing(0)
        self.sigRegLayout.setObjectName(u"sigRegLayout")
        self.sigRegLabel = QLabel(self.sigGroup)
        self.sigRegLabel.setObjectName(u"sigRegLabel")
        self.sigRegLabel.setMinimumSize(QSize(0, 20))
        self.sigRegLabel.setMaximumSize(QSize(16777215, 20))
        self.sigRegLabel.setFont(font3)

        self.sigRegLayout.addWidget(self.sigRegLabel)

        self.sigRegLine = QLineEdit(self.sigGroup)
        self.sigRegLine.setObjectName(u"sigRegLine")
        self.sigRegLine.setMinimumSize(QSize(120, 25))
        self.sigRegLine.setMaximumSize(QSize(16777215, 25))
        self.sigRegLine.setFont(font2)

        self.sigRegLayout.addWidget(self.sigRegLine)


        self.sigStdLayout.addLayout(self.sigRegLayout)

        self.sigCelLayout = QVBoxLayout()
        self.sigCelLayout.setSpacing(0)
        self.sigCelLayout.setObjectName(u"sigCelLayout")
        self.sigCelLabel = QLabel(self.sigGroup)
        self.sigCelLabel.setObjectName(u"sigCelLabel")
        self.sigCelLabel.setMinimumSize(QSize(0, 20))
        self.sigCelLabel.setMaximumSize(QSize(16777215, 20))
        self.sigCelLabel.setFont(font3)

        self.sigCelLayout.addWidget(self.sigCelLabel)

        self.sigCelLine = QLineEdit(self.sigGroup)
        self.sigCelLine.setObjectName(u"sigCelLine")
        self.sigCelLine.setMinimumSize(QSize(120, 25))
        self.sigCelLine.setMaximumSize(QSize(16777215, 25))
        self.sigCelLine.setFont(font2)

        self.sigCelLayout.addWidget(self.sigCelLine)


        self.sigStdLayout.addLayout(self.sigCelLayout)

        self.sigTypLayout = QVBoxLayout()
        self.sigTypLayout.setSpacing(0)
        self.sigTypLayout.setObjectName(u"sigTypLayout")
        self.sigTypLabel = QLabel(self.sigGroup)
        self.sigTypLabel.setObjectName(u"sigTypLabel")
        self.sigTypLabel.setMinimumSize(QSize(0, 20))
        self.sigTypLabel.setMaximumSize(QSize(16777215, 20))
        self.sigTypLabel.setFont(font3)

        self.sigTypLayout.addWidget(self.sigTypLabel)

        self.sigTypLine = QLineEdit(self.sigGroup)
        self.sigTypLine.setObjectName(u"sigTypLine")
        self.sigTypLine.setMinimumSize(QSize(120, 25))
        self.sigTypLine.setMaximumSize(QSize(16777215, 25))
        self.sigTypLine.setFont(font2)

        self.sigTypLayout.addWidget(self.sigTypLine)


        self.sigStdLayout.addLayout(self.sigTypLayout)


        self.sigLayout.addLayout(self.sigStdLayout)

        self.sigNoteLayout = QVBoxLayout()
        self.sigNoteLayout.setSpacing(0)
        self.sigNoteLayout.setObjectName(u"sigNoteLayout")
        self.sigNoteLabel = QLabel(self.sigGroup)
        self.sigNoteLabel.setObjectName(u"sigNoteLabel")
        self.sigNoteLabel.setMinimumSize(QSize(0, 20))
        self.sigNoteLabel.setMaximumSize(QSize(16777215, 20))
        self.sigNoteLabel.setFont(font3)

        self.sigNoteLayout.addWidget(self.sigNoteLabel)

        self.sigNoteLine = QLineEdit(self.sigGroup)
        self.sigNoteLine.setObjectName(u"sigNoteLine")
        self.sigNoteLine.setMinimumSize(QSize(500, 25))
        self.sigNoteLine.setMaximumSize(QSize(16777215, 25))
        self.sigNoteLine.setFont(font2)

        self.sigNoteLayout.addWidget(self.sigNoteLine)


        self.sigLayout.addLayout(self.sigNoteLayout)


        self.metaLayout.addWidget(self.sigGroup)

        self.sysGroup = QGroupBox(self.metaFrame)
        self.sysGroup.setObjectName(u"sysGroup")
        self.sysGroup.setMinimumSize(QSize(660, 125))
        self.sysGroup.setMaximumSize(QSize(16777215, 125))
        self.sysGroup.setFont(font4)
        self.sysLayout = QVBoxLayout(self.sysGroup)
        self.sysLayout.setObjectName(u"sysLayout")
        self.sysLayout.setContentsMargins(-1, 0, -1, 6)
        self.sysStdLayout = QHBoxLayout()
        self.sysStdLayout.setObjectName(u"sysStdLayout")
        self.sysTypLayout = QVBoxLayout()
        self.sysTypLayout.setSpacing(0)
        self.sysTypLayout.setObjectName(u"sysTypLayout")
        self.sysTypLabel = QLabel(self.sysGroup)
        self.sysTypLabel.setObjectName(u"sysTypLabel")
        self.sysTypLabel.setMinimumSize(QSize(0, 20))
        self.sysTypLabel.setMaximumSize(QSize(16777215, 20))
        self.sysTypLabel.setFont(font3)

        self.sysTypLayout.addWidget(self.sysTypLabel)

        self.sysTypCombo = QComboBox(self.sysGroup)
        self.sysTypCombo.addItem("")
        self.sysTypCombo.addItem("")
        self.sysTypCombo.setObjectName(u"sysTypCombo")
        self.sysTypCombo.setMinimumSize(QSize(120, 25))
        self.sysTypCombo.setMaximumSize(QSize(120, 25))
        self.sysTypCombo.setFont(font2)

        self.sysTypLayout.addWidget(self.sysTypCombo)


        self.sysStdLayout.addLayout(self.sysTypLayout)

        self.sysMfrLayout = QVBoxLayout()
        self.sysMfrLayout.setSpacing(0)
        self.sysMfrLayout.setObjectName(u"sysMfrLayout")
        self.sysMfrLabel = QLabel(self.sysGroup)
        self.sysMfrLabel.setObjectName(u"sysMfrLabel")
        self.sysMfrLabel.setMinimumSize(QSize(0, 20))
        self.sysMfrLabel.setMaximumSize(QSize(16777215, 20))
        self.sysMfrLabel.setFont(font3)

        self.sysMfrLayout.addWidget(self.sysMfrLabel)

        self.sysMfrLine = QLineEdit(self.sysGroup)
        self.sysMfrLine.setObjectName(u"sysMfrLine")
        self.sysMfrLine.setMinimumSize(QSize(120, 25))
        self.sysMfrLine.setMaximumSize(QSize(16777215, 25))
        font6 = QFont()
        font6.setPointSize(9)
        font6.setBold(False)
        font6.setItalic(False)
        self.sysMfrLine.setFont(font6)

        self.sysMfrLayout.addWidget(self.sysMfrLine)


        self.sysStdLayout.addLayout(self.sysMfrLayout)

        self.sysPrtLayout = QVBoxLayout()
        self.sysPrtLayout.setSpacing(0)
        self.sysPrtLayout.setObjectName(u"sysPrtLayout")
        self.sysPrtLabel = QLabel(self.sysGroup)
        self.sysPrtLabel.setObjectName(u"sysPrtLabel")
        self.sysPrtLabel.setMinimumSize(QSize(0, 20))
        self.sysPrtLabel.setMaximumSize(QSize(16777215, 20))
        self.sysPrtLabel.setFont(font3)

        self.sysPrtLayout.addWidget(self.sysPrtLabel)

        self.sysPrtLine = QLineEdit(self.sysGroup)
        self.sysPrtLine.setObjectName(u"sysPrtLine")
        self.sysPrtLine.setMinimumSize(QSize(120, 25))
        self.sysPrtLine.setMaximumSize(QSize(16777215, 25))
        self.sysPrtLine.setFont(font6)

        self.sysPrtLayout.addWidget(self.sysPrtLine)


        self.sysStdLayout.addLayout(self.sysPrtLayout)

        self.sysSrnLayout = QVBoxLayout()
        self.sysSrnLayout.setSpacing(0)
        self.sysSrnLayout.setObjectName(u"sysSrnLayout")
        self.sysSrnLabel = QLabel(self.sysGroup)
        self.sysSrnLabel.setObjectName(u"sysSrnLabel")
        self.sysSrnLabel.setMinimumSize(QSize(0, 20))
        self.sysSrnLabel.setMaximumSize(QSize(16777215, 20))
        self.sysSrnLabel.setFont(font3)

        self.sysSrnLayout.addWidget(self.sysSrnLabel)

        self.sysSrnLine = QLineEdit(self.sysGroup)
        self.sysSrnLine.setObjectName(u"sysSrnLine")
        self.sysSrnLine.setMinimumSize(QSize(120, 25))
        self.sysSrnLine.setMaximumSize(QSize(16777215, 25))
        self.sysSrnLine.setFont(font2)

        self.sysSrnLayout.addWidget(self.sysSrnLine)


        self.sysStdLayout.addLayout(self.sysSrnLayout)

        self.sysSocLayout = QVBoxLayout()
        self.sysSocLayout.setSpacing(0)
        self.sysSocLayout.setObjectName(u"sysSocLayout")
        self.sysSocLabel = QLabel(self.sysGroup)
        self.sysSocLabel.setObjectName(u"sysSocLabel")
        self.sysSocLabel.setMinimumSize(QSize(0, 20))
        self.sysSocLabel.setMaximumSize(QSize(16777215, 20))
        self.sysSocLabel.setFont(font3)

        self.sysSocLayout.addWidget(self.sysSocLabel)

        self.sysSocLine = QLineEdit(self.sysGroup)
        self.sysSocLine.setObjectName(u"sysSocLine")
        self.sysSocLine.setMinimumSize(QSize(120, 25))
        self.sysSocLine.setMaximumSize(QSize(16777215, 25))
        self.sysSocLine.setFont(font2)

        self.sysSocLayout.addWidget(self.sysSocLine)


        self.sysStdLayout.addLayout(self.sysSocLayout)


        self.sysLayout.addLayout(self.sysStdLayout)

        self.sysNoteLayout = QVBoxLayout()
        self.sysNoteLayout.setSpacing(0)
        self.sysNoteLayout.setObjectName(u"sysNoteLayout")
        self.sysNoteLabel = QLabel(self.sysGroup)
        self.sysNoteLabel.setObjectName(u"sysNoteLabel")
        self.sysNoteLabel.setMinimumSize(QSize(0, 20))
        self.sysNoteLabel.setMaximumSize(QSize(16777215, 20))
        self.sysNoteLabel.setFont(font3)

        self.sysNoteLayout.addWidget(self.sysNoteLabel)

        self.sysNoteLine = QLineEdit(self.sysGroup)
        self.sysNoteLine.setObjectName(u"sysNoteLine")
        self.sysNoteLine.setMinimumSize(QSize(500, 25))
        self.sysNoteLine.setMaximumSize(QSize(16777215, 25))
        self.sysNoteLine.setFont(font2)

        self.sysNoteLayout.addWidget(self.sysNoteLine)


        self.sysLayout.addLayout(self.sysNoteLayout)


        self.metaLayout.addWidget(self.sysGroup)

        self.prbGroup = QGroupBox(self.metaFrame)
        self.prbGroup.setObjectName(u"prbGroup")
        self.prbGroup.setMinimumSize(QSize(660, 125))
        self.prbGroup.setMaximumSize(QSize(16777215, 125))
        self.prbGroup.setFont(font4)
        self.prbLayout = QVBoxLayout(self.prbGroup)
        self.prbLayout.setObjectName(u"prbLayout")
        self.prbLayout.setContentsMargins(-1, 0, -1, 6)
        self.prbStdLayout = QHBoxLayout()
        self.prbStdLayout.setObjectName(u"prbStdLayout")
        self.prbTypLayout = QVBoxLayout()
        self.prbTypLayout.setSpacing(0)
        self.prbTypLayout.setObjectName(u"prbTypLayout")
        self.prbTypLabel = QLabel(self.prbGroup)
        self.prbTypLabel.setObjectName(u"prbTypLabel")
        self.prbTypLabel.setFont(font3)

        self.prbTypLayout.addWidget(self.prbTypLabel)

        self.prbTypLine = QLineEdit(self.prbGroup)
        self.prbTypLine.setObjectName(u"prbTypLine")
        self.prbTypLine.setMinimumSize(QSize(120, 25))
        self.prbTypLine.setMaximumSize(QSize(16777215, 25))
        self.prbTypLine.setFont(font2)

        self.prbTypLayout.addWidget(self.prbTypLine)


        self.prbStdLayout.addLayout(self.prbTypLayout)

        self.prbMfrLayout = QVBoxLayout()
        self.prbMfrLayout.setSpacing(0)
        self.prbMfrLayout.setObjectName(u"prbMfrLayout")
        self.prbMfrLabel = QLabel(self.prbGroup)
        self.prbMfrLabel.setObjectName(u"prbMfrLabel")
        self.prbMfrLabel.setMinimumSize(QSize(0, 20))
        self.prbMfrLabel.setMaximumSize(QSize(16777215, 20))
        self.prbMfrLabel.setFont(font3)

        self.prbMfrLayout.addWidget(self.prbMfrLabel)

        self.prbMfrLine = QLineEdit(self.prbGroup)
        self.prbMfrLine.setObjectName(u"prbMfrLine")
        self.prbMfrLine.setMinimumSize(QSize(120, 25))
        self.prbMfrLine.setMaximumSize(QSize(16777215, 25))
        self.prbMfrLine.setFont(font6)

        self.prbMfrLayout.addWidget(self.prbMfrLine)


        self.prbStdLayout.addLayout(self.prbMfrLayout)

        self.prbPrtLayout = QVBoxLayout()
        self.prbPrtLayout.setSpacing(0)
        self.prbPrtLayout.setObjectName(u"prbPrtLayout")
        self.prbPrtLabel = QLabel(self.prbGroup)
        self.prbPrtLabel.setObjectName(u"prbPrtLabel")
        self.prbPrtLabel.setMinimumSize(QSize(0, 20))
        self.prbPrtLabel.setMaximumSize(QSize(16777215, 20))
        self.prbPrtLabel.setFont(font3)

        self.prbPrtLayout.addWidget(self.prbPrtLabel)

        self.prbPrtLine = QLineEdit(self.prbGroup)
        self.prbPrtLine.setObjectName(u"prbPrtLine")
        self.prbPrtLine.setMinimumSize(QSize(120, 25))
        self.prbPrtLine.setMaximumSize(QSize(16777215, 25))
        self.prbPrtLine.setFont(font6)

        self.prbPrtLayout.addWidget(self.prbPrtLine)


        self.prbStdLayout.addLayout(self.prbPrtLayout)

        self.prbSrnLayout = QVBoxLayout()
        self.prbSrnLayout.setSpacing(0)
        self.prbSrnLayout.setObjectName(u"prbSrnLayout")
        self.prbSrnLabel = QLabel(self.prbGroup)
        self.prbSrnLabel.setObjectName(u"prbSrnLabel")
        self.prbSrnLabel.setMinimumSize(QSize(0, 20))
        self.prbSrnLabel.setMaximumSize(QSize(16777215, 20))
        self.prbSrnLabel.setFont(font3)

        self.prbSrnLayout.addWidget(self.prbSrnLabel)

        self.prbSrnLine = QLineEdit(self.prbGroup)
        self.prbSrnLine.setObjectName(u"prbSrnLine")
        self.prbSrnLine.setMinimumSize(QSize(120, 25))
        self.prbSrnLine.setMaximumSize(QSize(16777215, 25))
        self.prbSrnLine.setFont(font2)

        self.prbSrnLayout.addWidget(self.prbSrnLine)


        self.prbStdLayout.addLayout(self.prbSrnLayout)

        self.prbChnLayout = QVBoxLayout()
        self.prbChnLayout.setSpacing(0)
        self.prbChnLayout.setObjectName(u"prbChnLayout")
        self.prbChnLabel = QLabel(self.prbGroup)
        self.prbChnLabel.setObjectName(u"prbChnLabel")
        self.prbChnLabel.setMinimumSize(QSize(0, 20))
        self.prbChnLabel.setMaximumSize(QSize(16777215, 20))
        self.prbChnLabel.setFont(font3)

        self.prbChnLayout.addWidget(self.prbChnLabel)

        self.prbChnSpinbox = QSpinBox(self.prbGroup)
        self.prbChnSpinbox.setObjectName(u"prbChnSpinbox")
        self.prbChnSpinbox.setMinimumSize(QSize(120, 25))
        self.prbChnSpinbox.setMaximumSize(QSize(16777215, 25))
        self.prbChnSpinbox.setFont(font2)
        self.prbChnSpinbox.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.prbChnSpinbox.setMaximum(10000)

        self.prbChnLayout.addWidget(self.prbChnSpinbox)


        self.prbStdLayout.addLayout(self.prbChnLayout)


        self.prbLayout.addLayout(self.prbStdLayout)

        self.prbNoteLayout = QVBoxLayout()
        self.prbNoteLayout.setSpacing(0)
        self.prbNoteLayout.setObjectName(u"prbNoteLayout")
        self.prbNoteLabel = QLabel(self.prbGroup)
        self.prbNoteLabel.setObjectName(u"prbNoteLabel")
        self.prbNoteLabel.setMinimumSize(QSize(0, 20))
        self.prbNoteLabel.setMaximumSize(QSize(16777215, 20))
        self.prbNoteLabel.setFont(font3)

        self.prbNoteLayout.addWidget(self.prbNoteLabel)

        self.prbNoteLine = QLineEdit(self.prbGroup)
        self.prbNoteLine.setObjectName(u"prbNoteLine")
        self.prbNoteLine.setMinimumSize(QSize(500, 25))
        self.prbNoteLine.setMaximumSize(QSize(16777215, 25))
        self.prbNoteLine.setFont(font2)

        self.prbNoteLayout.addWidget(self.prbNoteLine)


        self.prbLayout.addLayout(self.prbNoteLayout)


        self.metaLayout.addWidget(self.prbGroup)

        self.dtmGroup = QGroupBox(self.metaFrame)
        self.dtmGroup.setObjectName(u"dtmGroup")
        self.dtmGroup.setMinimumSize(QSize(400, 72))
        self.dtmGroup.setMaximumSize(QSize(16777215, 72))
        self.dtmGroup.setFont(font4)
        self.dtmLayout = QHBoxLayout(self.dtmGroup)
        self.dtmLayout.setSpacing(50)
        self.dtmLayout.setObjectName(u"dtmLayout")
        self.dtmLayout.setContentsMargins(-1, 0, -1, 6)
        self.dateLayout = QVBoxLayout()
        self.dateLayout.setSpacing(0)
        self.dateLayout.setObjectName(u"dateLayout")
        self.dateLabel = QLabel(self.dtmGroup)
        self.dateLabel.setObjectName(u"dateLabel")
        self.dateLabel.setMinimumSize(QSize(0, 20))
        self.dateLabel.setMaximumSize(QSize(16777215, 20))
        self.dateLabel.setFont(font3)

        self.dateLayout.addWidget(self.dateLabel)

        self.recDate = QDateEdit(self.dtmGroup)
        self.recDate.setObjectName(u"recDate")
        self.recDate.setMinimumSize(QSize(120, 25))
        self.recDate.setMaximumSize(QSize(16777215, 25))
        self.recDate.setFont(font2)
        self.recDate.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.recDate.setCalendarPopup(True)

        self.dateLayout.addWidget(self.recDate)


        self.dtmLayout.addLayout(self.dateLayout)

        self.timeLayout = QVBoxLayout()
        self.timeLayout.setSpacing(0)
        self.timeLayout.setObjectName(u"timeLayout")
        self.timeLabel = QLabel(self.dtmGroup)
        self.timeLabel.setObjectName(u"timeLabel")
        self.timeLabel.setMinimumSize(QSize(0, 20))
        self.timeLabel.setMaximumSize(QSize(16777215, 20))
        self.timeLabel.setFont(font3)

        self.timeLayout.addWidget(self.timeLabel)

        self.recTime = QTimeEdit(self.dtmGroup)
        self.recTime.setObjectName(u"recTime")
        self.recTime.setMinimumSize(QSize(120, 25))
        self.recTime.setMaximumSize(QSize(16777215, 25))
        self.recTime.setFont(font2)
        self.recTime.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.timeLayout.addWidget(self.recTime)


        self.dtmLayout.addLayout(self.timeLayout)


        self.metaLayout.addWidget(self.dtmGroup)


        self.centralLayout.addWidget(self.metaFrame)

        self.procLayout = QHBoxLayout()
        self.procLayout.setSpacing(20)
        self.procLayout.setObjectName(u"procLayout")
        self.previewButton = QPushButton(self.centralWidget)
        self.previewButton.setObjectName(u"previewButton")
        self.previewButton.setMinimumSize(QSize(200, 35))
        self.previewButton.setMaximumSize(QSize(16777215, 35))
        self.previewButton.setFont(font)

        self.procLayout.addWidget(self.previewButton)

        self.saveButton = QPushButton(self.centralWidget)
        self.saveButton.setObjectName(u"saveButton")
        self.saveButton.setMinimumSize(QSize(500, 35))
        self.saveButton.setMaximumSize(QSize(16777215, 35))
        self.saveButton.setFont(font)

        self.procLayout.addWidget(self.saveButton)


        self.centralLayout.addLayout(self.procLayout)

        ParusArcWindow.setCentralWidget(self.centralWidget)
        self.statBar = QStatusBar(ParusArcWindow)
        self.statBar.setObjectName(u"statBar")
        ParusArcWindow.setStatusBar(self.statBar)

        self.retranslateUi(ParusArcWindow)

        QMetaObject.connectSlotsByName(ParusArcWindow)
    # setupUi

    def retranslateUi(self, ParusArcWindow):
        ParusArcWindow.setWindowTitle(QCoreApplication.translate("ParusArcWindow", u"Parus - Archived Signal Creator", None))
        self.dataLabel.setText(QCoreApplication.translate("ParusArcWindow", u"Data File IO", None))
        self.srcFileBox.setTitle(QCoreApplication.translate("ParusArcWindow", u"Source Data File", None))
        self.srcFilePath.setPlaceholderText(QCoreApplication.translate("ParusArcWindow", u"Select data file", None))
        self.srcFileSelect.setText(QCoreApplication.translate("ParusArcWindow", u"Select", None))
        self.datChnLabel.setText(QCoreApplication.translate("ParusArcWindow", u"Channel", None))
        self.datWfmLabel.setText(QCoreApplication.translate("ParusArcWindow", u"Waveform", None))
        self.datSpkLabel.setText(QCoreApplication.translate("ParusArcWindow", u"Spike", None))
        self.smpAntLabel.setText(QCoreApplication.translate("ParusArcWindow", u"Anterior Samples", None))
        self.smpAntSpinbox.setSuffix(QCoreApplication.translate("ParusArcWindow", u" pt", None))
        self.smpPstLabel.setText(QCoreApplication.translate("ParusArcWindow", u"Posterior Samples", None))
        self.smpPstSpinbox.setSuffix(QCoreApplication.translate("ParusArcWindow", u" pt", None))
        self.dstDirBox.setTitle(QCoreApplication.translate("ParusArcWindow", u"Output Directory", None))
        self.dstDirPath.setPlaceholderText(QCoreApplication.translate("ParusArcWindow", u"Select output folder", None))
        self.dstDirSelect.setText(QCoreApplication.translate("ParusArcWindow", u"Open", None))
        self.metaLabel.setText(QCoreApplication.translate("ParusArcWindow", u"Metadata", None))
        self.ognGroup.setTitle(QCoreApplication.translate("ParusArcWindow", u"Organism Data", None))
        self.ognGenLabel.setText(QCoreApplication.translate("ParusArcWindow", u"Genus", None))
        self.ognGenLine.setPlaceholderText(QCoreApplication.translate("ParusArcWindow", u"Generic name", None))
        self.ognSpcLabel.setText(QCoreApplication.translate("ParusArcWindow", u"Species", None))
        self.ognSpcLine.setPlaceholderText(QCoreApplication.translate("ParusArcWindow", u"Specific epithet", None))
        self.ognStrLabel.setText(QCoreApplication.translate("ParusArcWindow", u"Strain", None))
        self.ognStrLine.setPlaceholderText(QCoreApplication.translate("ParusArcWindow", u"Strain identifier", None))
        self.ognModLabel.setText(QCoreApplication.translate("ParusArcWindow", u"Modification", None))
        self.ognModLine.setPlaceholderText(QCoreApplication.translate("ParusArcWindow", u"Genetic modification", None))
        self.ognNoteLabel.setText(QCoreApplication.translate("ParusArcWindow", u"Notes", None))
        self.ognNoteLine.setPlaceholderText(QCoreApplication.translate("ParusArcWindow", u"Extra notes", None))
        self.sigGroup.setTitle(QCoreApplication.translate("ParusArcWindow", u"Signal Feature", None))
        self.sigRegLabel.setText(QCoreApplication.translate("ParusArcWindow", u"Region", None))
        self.sigRegLine.setPlaceholderText(QCoreApplication.translate("ParusArcWindow", u"Separate by space, Allen Brain Atlas style ", None))
        self.sigCelLabel.setText(QCoreApplication.translate("ParusArcWindow", u"Cell Type", None))
        self.sigCelLine.setPlaceholderText(QCoreApplication.translate("ParusArcWindow", u"Cell type information", None))
        self.sigTypLabel.setText(QCoreApplication.translate("ParusArcWindow", u"Signal Type", None))
        self.sigTypLine.setPlaceholderText(QCoreApplication.translate("ParusArcWindow", u"Signal type for grouping", None))
        self.sigNoteLabel.setText(QCoreApplication.translate("ParusArcWindow", u"Notes", None))
        self.sigNoteLine.setPlaceholderText(QCoreApplication.translate("ParusArcWindow", u"Extra notes", None))
        self.sysGroup.setTitle(QCoreApplication.translate("ParusArcWindow", u"Recoding System", None))
        self.sysTypLabel.setText(QCoreApplication.translate("ParusArcWindow", u"Type", None))
        self.sysTypCombo.setItemText(0, QCoreApplication.translate("ParusArcWindow", u"Digital", None))
        self.sysTypCombo.setItemText(1, QCoreApplication.translate("ParusArcWindow", u"Analog", None))

        self.sysMfrLabel.setText(QCoreApplication.translate("ParusArcWindow", u"Manufacture", None))
        self.sysMfrLine.setPlaceholderText(QCoreApplication.translate("ParusArcWindow", u"Manufacture name", None))
        self.sysPrtLabel.setText(QCoreApplication.translate("ParusArcWindow", u"Part Number", None))
        self.sysPrtLine.setPlaceholderText(QCoreApplication.translate("ParusArcWindow", u"Part or model", None))
        self.sysSrnLabel.setText(QCoreApplication.translate("ParusArcWindow", u"Serial Number", None))
        self.sysSrnLine.setPlaceholderText(QCoreApplication.translate("ParusArcWindow", u"Serial or batch", None))
        self.sysSocLabel.setText(QCoreApplication.translate("ParusArcWindow", u"Socket", None))
        self.sysSocLine.setPlaceholderText(QCoreApplication.translate("ParusArcWindow", u"Recording socket", None))
        self.sysNoteLabel.setText(QCoreApplication.translate("ParusArcWindow", u"Notes", None))
        self.sysNoteLine.setPlaceholderText(QCoreApplication.translate("ParusArcWindow", u"Extra notes", None))
        self.prbGroup.setTitle(QCoreApplication.translate("ParusArcWindow", u"Probe Infomation", None))
        self.prbTypLabel.setText(QCoreApplication.translate("ParusArcWindow", u"Type", None))
        self.prbTypLine.setPlaceholderText(QCoreApplication.translate("ParusArcWindow", u"Type abbreviation", None))
        self.prbMfrLabel.setText(QCoreApplication.translate("ParusArcWindow", u"Manufacture", None))
        self.prbMfrLine.setPlaceholderText(QCoreApplication.translate("ParusArcWindow", u"Manufacture name", None))
        self.prbPrtLabel.setText(QCoreApplication.translate("ParusArcWindow", u"Part Number", None))
        self.prbPrtLine.setPlaceholderText(QCoreApplication.translate("ParusArcWindow", u"Part or model", None))
        self.prbSrnLabel.setText(QCoreApplication.translate("ParusArcWindow", u"Serial Number", None))
        self.prbSrnLine.setPlaceholderText(QCoreApplication.translate("ParusArcWindow", u"Serial or batch", None))
        self.prbChnLabel.setText(QCoreApplication.translate("ParusArcWindow", u"Channel", None))
        self.prbNoteLabel.setText(QCoreApplication.translate("ParusArcWindow", u"Notes", None))
        self.prbNoteLine.setPlaceholderText(QCoreApplication.translate("ParusArcWindow", u"Extra notes", None))
        self.dtmGroup.setTitle(QCoreApplication.translate("ParusArcWindow", u"Data Datetime", None))
        self.dateLabel.setText(QCoreApplication.translate("ParusArcWindow", u"Date", None))
        self.recDate.setDisplayFormat(QCoreApplication.translate("ParusArcWindow", u"yyyy-MM-dd", None))
        self.timeLabel.setText(QCoreApplication.translate("ParusArcWindow", u"Time", None))
        self.recTime.setDisplayFormat(QCoreApplication.translate("ParusArcWindow", u"hh:mm:ss", None))
        self.previewButton.setText(QCoreApplication.translate("ParusArcWindow", u"Preview", None))
        self.saveButton.setText(QCoreApplication.translate("ParusArcWindow", u"Save Archived Signal", None))
    # retranslateUi

