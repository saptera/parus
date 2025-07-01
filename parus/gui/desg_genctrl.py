# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'desg_genctrl.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject,  QSize, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QComboBox, QDoubleSpinBox, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QSpinBox, QStatusBar, QTextEdit, QVBoxLayout, QWidget)


class Ui_ParusGenWindow(object):
    def setupUi(self, ParusGenWindow):
        if not ParusGenWindow.objectName():
            ParusGenWindow.setObjectName(u"ParusGenWindow")
        ParusGenWindow.resize(1175, 1010)
        ParusGenWindow.setMinimumSize(QSize(1175, 1010))
        ParusGenWindow.setMaximumSize(QSize(1175, 1010))
        self.centralWidget = QWidget(ParusGenWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.centralWidget.setMinimumSize(QSize(1175, 1000))
        self.centralWidget.setMaximumSize(QSize(1175, 1000))
        self.mainLayout = QVBoxLayout(self.centralWidget)
        self.mainLayout.setObjectName(u"mainLayout")
        self.conFrame = QFrame(self.centralWidget)
        self.conFrame.setObjectName(u"conFrame")
        self.conFrame.setMinimumSize(QSize(1150, 220))
        self.conFrame.setMaximumSize(QSize(1150, 220))
        self.conFrame.setFrameShape(QFrame.Shape.Box)
        self.conFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.conFrameLayout = QGridLayout(self.conFrame)
        self.conFrameLayout.setObjectName(u"conFrameLayout")
        self.conFrameLayout.setHorizontalSpacing(9)
        self.conFrameLayout.setContentsMargins(-1, 0, -1, 5)
        self.procConsole = QTextEdit(self.conFrame)
        self.procConsole.setObjectName(u"procConsole")
        self.procConsole.setMinimumSize(QSize(1000, 0))

        self.conFrameLayout.addWidget(self.procConsole, 1, 0, 1, 1)

        self.procConLabel = QLabel(self.conFrame)
        self.procConLabel.setObjectName(u"procConLabel")
        self.procConLabel.setMinimumSize(QSize(1110, 28))
        self.procConLabel.setMaximumSize(QSize(16777215, 28))
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.procConLabel.setFont(font)

        self.conFrameLayout.addWidget(self.procConLabel, 0, 0, 1, 2)

        self.conCtrlLayout = QVBoxLayout()
        self.conCtrlLayout.setSpacing(12)
        self.conCtrlLayout.setObjectName(u"conCtrlLayout")
        self.procConClear = QPushButton(self.conFrame)
        self.procConClear.setObjectName(u"procConClear")
        self.procConClear.setMinimumSize(QSize(100, 30))
        self.procConClear.setMaximumSize(QSize(100, 30))
        font1 = QFont()
        font1.setBold(True)
        self.procConClear.setFont(font1)

        self.conCtrlLayout.addWidget(self.procConClear)

        self.procConCopy = QPushButton(self.conFrame)
        self.procConCopy.setObjectName(u"procConCopy")
        self.procConCopy.setMinimumSize(QSize(100, 30))
        self.procConCopy.setMaximumSize(QSize(100, 30))
        self.procConCopy.setFont(font1)

        self.conCtrlLayout.addWidget(self.procConCopy)

        self.procConScroll = QPushButton(self.conFrame)
        self.procConScroll.setObjectName(u"procConScroll")
        self.procConScroll.setMinimumSize(QSize(100, 50))
        self.procConScroll.setMaximumSize(QSize(100, 50))
        self.procConScroll.setFont(font1)
        self.procConScroll.setCheckable(True)
        self.procConScroll.setChecked(True)

        self.conCtrlLayout.addWidget(self.procConScroll)


        self.conFrameLayout.addLayout(self.conCtrlLayout, 1, 1, 1, 1)


        self.mainLayout.addWidget(self.conFrame)

        self.argFrame = QFrame(self.centralWidget)
        self.argFrame.setObjectName(u"argFrame")
        self.argFrame.setMinimumSize(QSize(1150, 755))
        self.argFrame.setMaximumSize(QSize(1150, 755))
        self.argFrame.setFrameShape(QFrame.Shape.Box)
        self.argFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.argFrameLayout = QVBoxLayout(self.argFrame)
        self.argFrameLayout.setObjectName(u"argFrameLayout")
        self.argFrameLayout.setContentsMargins(-1, 5, -1, 5)
        self.genSimFrame = QFrame(self.argFrame)
        self.genSimFrame.setObjectName(u"genSimFrame")
        self.genSimFrame.setMinimumSize(QSize(1132, 570))
        self.genSimFrame.setMaximumSize(QSize(1132, 570))
        self.genSimFrame.setFrameShape(QFrame.Shape.Box)
        self.genSimFrame.setFrameShadow(QFrame.Shadow.Sunken)
        self.genSimLayout = QGridLayout(self.genSimFrame)
        self.genSimLayout.setObjectName(u"genSimLayout")
        self.genSimLayout.setHorizontalSpacing(20)
        self.genSimLayout.setContentsMargins(-1, 0, -1, -1)
        self.genSimLabelSeparator = QFrame(self.genSimFrame)
        self.genSimLabelSeparator.setObjectName(u"genSimLabelSeparator")
        self.genSimLabelSeparator.setMinimumSize(QSize(1110, 0))
        self.genSimLabelSeparator.setFrameShape(QFrame.Shape.HLine)
        self.genSimLabelSeparator.setFrameShadow(QFrame.Shadow.Sunken)

        self.genSimLayout.addWidget(self.genSimLabelSeparator, 1, 0, 1, 4)

        self.sigBox = QGroupBox(self.genSimFrame)
        self.sigBox.setObjectName(u"sigBox")
        self.sigBox.setMinimumSize(QSize(1110, 60))
        self.sigBox.setMaximumSize(QSize(16777215, 60))
        self.sigBox.setFont(font1)
        self.sigBoxLayout = QHBoxLayout(self.sigBox)
        self.sigBoxLayout.setSpacing(10)
        self.sigBoxLayout.setObjectName(u"sigBoxLayout")
        self.sigPath = QLineEdit(self.sigBox)
        self.sigPath.setObjectName(u"sigPath")
        self.sigPath.setMinimumSize(QSize(1000, 22))
        self.sigPath.setMaximumSize(QSize(16777215, 22))
        font2 = QFont()
        font2.setBold(False)
        self.sigPath.setFont(font2)

        self.sigBoxLayout.addWidget(self.sigPath)

        self.sigSelect = QPushButton(self.sigBox)
        self.sigSelect.setObjectName(u"sigSelect")
        self.sigSelect.setMinimumSize(QSize(80, 24))
        self.sigSelect.setMaximumSize(QSize(80, 24))
        self.sigSelect.setFont(font2)

        self.sigBoxLayout.addWidget(self.sigSelect)


        self.genSimLayout.addWidget(self.sigBox, 2, 0, 1, 4)

        self.noiBox = QGroupBox(self.genSimFrame)
        self.noiBox.setObjectName(u"noiBox")
        self.noiBox.setMinimumSize(QSize(1110, 60))
        self.noiBox.setMaximumSize(QSize(16777215, 60))
        self.noiBox.setFont(font1)
        self.noiBoxLayout = QHBoxLayout(self.noiBox)
        self.noiBoxLayout.setSpacing(10)
        self.noiBoxLayout.setObjectName(u"noiBoxLayout")
        self.noiPath = QLineEdit(self.noiBox)
        self.noiPath.setObjectName(u"noiPath")
        self.noiPath.setMinimumSize(QSize(1000, 22))
        self.noiPath.setMaximumSize(QSize(16777215, 22))
        self.noiPath.setFont(font2)

        self.noiBoxLayout.addWidget(self.noiPath)

        self.noiSelect = QPushButton(self.noiBox)
        self.noiSelect.setObjectName(u"noiSelect")
        self.noiSelect.setMinimumSize(QSize(80, 24))
        self.noiSelect.setMaximumSize(QSize(80, 24))
        self.noiSelect.setFont(font2)

        self.noiBoxLayout.addWidget(self.noiSelect)


        self.genSimLayout.addWidget(self.noiBox, 3, 0, 1, 4)

        self.outBox = QGroupBox(self.genSimFrame)
        self.outBox.setObjectName(u"outBox")
        self.outBox.setMinimumSize(QSize(1110, 60))
        self.outBox.setMaximumSize(QSize(16777215, 60))
        self.outBox.setFont(font1)
        self.outBoxLayout = QHBoxLayout(self.outBox)
        self.outBoxLayout.setSpacing(10)
        self.outBoxLayout.setObjectName(u"outBoxLayout")
        self.outPath = QLineEdit(self.outBox)
        self.outPath.setObjectName(u"outPath")
        self.outPath.setMinimumSize(QSize(1000, 22))
        self.outPath.setMaximumSize(QSize(16777215, 22))
        self.outPath.setFont(font2)

        self.outBoxLayout.addWidget(self.outPath)

        self.outSelect = QPushButton(self.outBox)
        self.outSelect.setObjectName(u"outSelect")
        self.outSelect.setMinimumSize(QSize(80, 24))
        self.outSelect.setMaximumSize(QSize(80, 24))
        self.outSelect.setFont(font2)

        self.outBoxLayout.addWidget(self.outSelect)


        self.genSimLayout.addWidget(self.outBox, 4, 0, 1, 4)

        self.setBaseBox = QGroupBox(self.genSimFrame)
        self.setBaseBox.setObjectName(u"setBaseBox")
        self.setBaseBox.setMinimumSize(QSize(530, 80))
        self.setBaseBox.setMaximumSize(QSize(16777215, 80))
        self.setBaseBox.setFont(font1)
        self.setBaseBoxLayout = QHBoxLayout(self.setBaseBox)
        self.setBaseBoxLayout.setSpacing(18)
        self.setBaseBoxLayout.setObjectName(u"setBaseBoxLayout")
        self.sampCntLayout = QVBoxLayout()
        self.sampCntLayout.setSpacing(4)
        self.sampCntLayout.setObjectName(u"sampCntLayout")
        self.sampCntLabel = QLabel(self.setBaseBox)
        self.sampCntLabel.setObjectName(u"sampCntLabel")
        self.sampCntLabel.setMinimumSize(QSize(120, 16))
        self.sampCntLabel.setMaximumSize(QSize(16777215, 16))
        self.sampCntLabel.setFont(font1)

        self.sampCntLayout.addWidget(self.sampCntLabel)

        self.sampCnt = QSpinBox(self.setBaseBox)
        self.sampCnt.setObjectName(u"sampCnt")
        self.sampCnt.setMinimumSize(QSize(120, 22))
        self.sampCnt.setMaximumSize(QSize(16777215, 22))
        self.sampCnt.setFont(font2)
        self.sampCnt.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.sampCnt.setMaximum(16777215)
        self.sampCnt.setValue(100000)

        self.sampCntLayout.addWidget(self.sampCnt)


        self.setBaseBoxLayout.addLayout(self.sampCntLayout)

        self.sampLenLayout = QVBoxLayout()
        self.sampLenLayout.setSpacing(4)
        self.sampLenLayout.setObjectName(u"sampLenLayout")
        self.sampLenLabel = QLabel(self.setBaseBox)
        self.sampLenLabel.setObjectName(u"sampLenLabel")
        self.sampLenLabel.setMinimumSize(QSize(120, 16))
        self.sampLenLabel.setMaximumSize(QSize(16777215, 16))
        self.sampLenLabel.setFont(font1)

        self.sampLenLayout.addWidget(self.sampLenLabel)

        self.sampLen = QDoubleSpinBox(self.setBaseBox)
        self.sampLen.setObjectName(u"sampLen")
        self.sampLen.setMinimumSize(QSize(120, 22))
        self.sampLen.setMaximumSize(QSize(16777215, 22))
        self.sampLen.setFont(font2)
        self.sampLen.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.sampLen.setMinimum(1.000000000000000)
        self.sampLen.setMaximum(1000.000000000000000)
        self.sampLen.setValue(15.000000000000000)

        self.sampLenLayout.addWidget(self.sampLen)


        self.setBaseBoxLayout.addLayout(self.sampLenLayout)

        self.sampFreqLayout = QVBoxLayout()
        self.sampFreqLayout.setSpacing(4)
        self.sampFreqLayout.setObjectName(u"sampFreqLayout")
        self.sampFreqLabel = QLabel(self.setBaseBox)
        self.sampFreqLabel.setObjectName(u"sampFreqLabel")
        self.sampFreqLabel.setMinimumSize(QSize(120, 16))
        self.sampFreqLabel.setMaximumSize(QSize(16777215, 16))
        self.sampFreqLabel.setFont(font1)

        self.sampFreqLayout.addWidget(self.sampFreqLabel)

        self.sampFreq = QSpinBox(self.setBaseBox)
        self.sampFreq.setObjectName(u"sampFreq")
        self.sampFreq.setMinimumSize(QSize(120, 22))
        self.sampFreq.setMaximumSize(QSize(16777215, 22))
        self.sampFreq.setFont(font2)
        self.sampFreq.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.sampFreq.setMaximum(100000)
        self.sampFreq.setValue(20000)

        self.sampFreqLayout.addWidget(self.sampFreq)


        self.setBaseBoxLayout.addLayout(self.sampFreqLayout)

        self.exEgLayout = QVBoxLayout()
        self.exEgLayout.setSpacing(4)
        self.exEgLayout.setObjectName(u"exEgLayout")
        self.exEgLabel = QLabel(self.setBaseBox)
        self.exEgLabel.setObjectName(u"exEgLabel")
        self.exEgLabel.setMinimumSize(QSize(90, 16))
        self.exEgLabel.setMaximumSize(QSize(16777215, 16))
        self.exEgLabel.setFont(font1)

        self.exEgLayout.addWidget(self.exEgLabel)

        self.exEg = QSpinBox(self.setBaseBox)
        self.exEg.setObjectName(u"exEg")
        self.exEg.setMinimumSize(QSize(90, 22))
        self.exEg.setMaximumSize(QSize(16777215, 22))
        self.exEg.setFont(font2)
        self.exEg.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.exEg.setMaximum(16777215)
        self.exEg.setValue(100)

        self.exEgLayout.addWidget(self.exEg)


        self.setBaseBoxLayout.addLayout(self.exEgLayout)


        self.genSimLayout.addWidget(self.setBaseBox, 5, 0, 1, 2)

        self.setRateBox = QGroupBox(self.genSimFrame)
        self.setRateBox.setObjectName(u"setRateBox")
        self.setRateBox.setMinimumSize(QSize(559, 80))
        self.setRateBox.setMaximumSize(QSize(16777215, 80))
        self.setRateBox.setFont(font1)
        self.setRateBoxLayout = QHBoxLayout(self.setRateBox)
        self.setRateBoxLayout.setSpacing(10)
        self.setRateBoxLayout.setObjectName(u"setRateBoxLayout")
        self.spkGrpMthdLayout = QVBoxLayout()
        self.spkGrpMthdLayout.setSpacing(4)
        self.spkGrpMthdLayout.setObjectName(u"spkGrpMthdLayout")
        self.spkGrpMthdLabel = QLabel(self.setRateBox)
        self.spkGrpMthdLabel.setObjectName(u"spkGrpMthdLabel")
        self.spkGrpMthdLabel.setMinimumSize(QSize(100, 16))
        self.spkGrpMthdLabel.setMaximumSize(QSize(16777215, 16))
        self.spkGrpMthdLabel.setFont(font1)

        self.spkGrpMthdLayout.addWidget(self.spkGrpMthdLabel)

        self.spkGrpMthd = QComboBox(self.setRateBox)
        self.spkGrpMthd.addItem("")
        self.spkGrpMthd.addItem("")
        self.spkGrpMthd.addItem("")
        self.spkGrpMthd.setObjectName(u"spkGrpMthd")
        self.spkGrpMthd.setMinimumSize(QSize(100, 22))
        self.spkGrpMthd.setMaximumSize(QSize(16777215, 22))
        self.spkGrpMthd.setFont(font2)

        self.spkGrpMthdLayout.addWidget(self.spkGrpMthd)


        self.setRateBoxLayout.addLayout(self.spkGrpMthdLayout)

        self.spkGrpRateLayout = QVBoxLayout()
        self.spkGrpRateLayout.setSpacing(4)
        self.spkGrpRateLayout.setObjectName(u"spkGrpRateLayout")
        self.spkGrpRateLabel = QLabel(self.setRateBox)
        self.spkGrpRateLabel.setObjectName(u"spkGrpRateLabel")
        self.spkGrpRateLabel.setMinimumSize(QSize(120, 16))
        self.spkGrpRateLabel.setMaximumSize(QSize(16777215, 16))
        self.spkGrpRateLabel.setFont(font1)

        self.spkGrpRateLayout.addWidget(self.spkGrpRateLabel)

        self.spkGrpRate = QLineEdit(self.setRateBox)
        self.spkGrpRate.setObjectName(u"spkGrpRate")
        self.spkGrpRate.setMinimumSize(QSize(300, 22))
        self.spkGrpRate.setMaximumSize(QSize(16777215, 22))
        self.spkGrpRate.setFont(font2)

        self.spkGrpRateLayout.addWidget(self.spkGrpRate)


        self.setRateBoxLayout.addLayout(self.spkGrpRateLayout)

        self.setRateSeparator = QFrame(self.setRateBox)
        self.setRateSeparator.setObjectName(u"setRateSeparator")
        self.setRateSeparator.setFrameShape(QFrame.Shape.VLine)
        self.setRateSeparator.setFrameShadow(QFrame.Shadow.Sunken)

        self.setRateBoxLayout.addWidget(self.setRateSeparator)

        self.noiOlyRateLayout = QVBoxLayout()
        self.noiOlyRateLayout.setSpacing(4)
        self.noiOlyRateLayout.setObjectName(u"noiOlyRateLayout")
        self.noiOnlyRateLabel = QLabel(self.setRateBox)
        self.noiOnlyRateLabel.setObjectName(u"noiOnlyRateLabel")
        self.noiOnlyRateLabel.setMinimumSize(QSize(100, 16))
        self.noiOnlyRateLabel.setMaximumSize(QSize(16777215, 16))
        self.noiOnlyRateLabel.setFont(font1)

        self.noiOlyRateLayout.addWidget(self.noiOnlyRateLabel)

        self.noiOnlyRate = QDoubleSpinBox(self.setRateBox)
        self.noiOnlyRate.setObjectName(u"noiOnlyRate")
        self.noiOnlyRate.setMinimumSize(QSize(100, 22))
        self.noiOnlyRate.setMaximumSize(QSize(16777215, 22))
        self.noiOnlyRate.setFont(font2)
        self.noiOnlyRate.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.noiOnlyRate.setMinimum(0.000000000000000)
        self.noiOnlyRate.setMaximum(100.000000000000000)
        self.noiOnlyRate.setSingleStep(5.000000000000000)
        self.noiOnlyRate.setValue(5.000000000000000)

        self.noiOlyRateLayout.addWidget(self.noiOnlyRate)


        self.setRateBoxLayout.addLayout(self.noiOlyRateLayout)


        self.genSimLayout.addWidget(self.setRateBox, 5, 2, 1, 2)

        self.setOccrBox = QGroupBox(self.genSimFrame)
        self.setOccrBox.setObjectName(u"setOccrBox")
        self.setOccrBox.setMinimumSize(QSize(422, 80))
        self.setOccrBox.setMaximumSize(QSize(16777215, 80))
        self.setOccrBox.setFont(font1)
        self.setOccrBoxLayout = QHBoxLayout(self.setOccrBox)
        self.setOccrBoxLayout.setSpacing(18)
        self.setOccrBoxLayout.setObjectName(u"setOccrBoxLayout")
        self.minSpkFreqLayout = QVBoxLayout()
        self.minSpkFreqLayout.setSpacing(4)
        self.minSpkFreqLayout.setObjectName(u"minSpkFreqLayout")
        self.minSpkFreqLabel = QLabel(self.setOccrBox)
        self.minSpkFreqLabel.setObjectName(u"minSpkFreqLabel")
        self.minSpkFreqLabel.setMinimumSize(QSize(120, 16))
        self.minSpkFreqLabel.setMaximumSize(QSize(16777215, 16))
        self.minSpkFreqLabel.setFont(font1)

        self.minSpkFreqLayout.addWidget(self.minSpkFreqLabel)

        self.minSpkFreq = QSpinBox(self.setOccrBox)
        self.minSpkFreq.setObjectName(u"minSpkFreq")
        self.minSpkFreq.setMinimumSize(QSize(120, 22))
        self.minSpkFreq.setMaximumSize(QSize(16777215, 22))
        self.minSpkFreq.setFont(font2)
        self.minSpkFreq.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.minSpkFreq.setMaximum(500)
        self.minSpkFreq.setValue(50)

        self.minSpkFreqLayout.addWidget(self.minSpkFreq)


        self.setOccrBoxLayout.addLayout(self.minSpkFreqLayout)

        self.maxSpkFreqLayout = QVBoxLayout()
        self.maxSpkFreqLayout.setSpacing(4)
        self.maxSpkFreqLayout.setObjectName(u"maxSpkFreqLayout")
        self.maxSpkFreqLabel = QLabel(self.setOccrBox)
        self.maxSpkFreqLabel.setObjectName(u"maxSpkFreqLabel")
        self.maxSpkFreqLabel.setMinimumSize(QSize(120, 16))
        self.maxSpkFreqLabel.setMaximumSize(QSize(16777215, 16))
        self.maxSpkFreqLabel.setFont(font1)

        self.maxSpkFreqLayout.addWidget(self.maxSpkFreqLabel)

        self.maxSpkFreq = QSpinBox(self.setOccrBox)
        self.maxSpkFreq.setObjectName(u"maxSpkFreq")
        self.maxSpkFreq.setMinimumSize(QSize(120, 22))
        self.maxSpkFreq.setMaximumSize(QSize(16777215, 22))
        self.maxSpkFreq.setFont(font2)
        self.maxSpkFreq.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.maxSpkFreq.setMaximum(500)
        self.maxSpkFreq.setValue(100)

        self.maxSpkFreqLayout.addWidget(self.maxSpkFreq)


        self.setOccrBoxLayout.addLayout(self.maxSpkFreqLayout)

        self.chnCellCntLayout = QVBoxLayout()
        self.chnCellCntLayout.setSpacing(4)
        self.chnCellCntLayout.setObjectName(u"chnCellCntLayout")
        self.chnCellCntLabel = QLabel(self.setOccrBox)
        self.chnCellCntLabel.setObjectName(u"chnCellCntLabel")
        self.chnCellCntLabel.setMinimumSize(QSize(120, 16))
        self.chnCellCntLabel.setMaximumSize(QSize(16777215, 16))
        self.chnCellCntLabel.setFont(font1)

        self.chnCellCntLayout.addWidget(self.chnCellCntLabel)

        self.chnCellCnt = QSpinBox(self.setOccrBox)
        self.chnCellCnt.setObjectName(u"chnCellCnt")
        self.chnCellCnt.setMinimumSize(QSize(120, 22))
        self.chnCellCnt.setMaximumSize(QSize(16777215, 22))
        self.chnCellCnt.setFont(font2)
        self.chnCellCnt.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.chnCellCnt.setMinimum(1)
        self.chnCellCnt.setMaximum(10)
        self.chnCellCnt.setValue(5)

        self.chnCellCntLayout.addWidget(self.chnCellCnt)


        self.setOccrBoxLayout.addLayout(self.chnCellCntLayout)


        self.genSimLayout.addWidget(self.setOccrBox, 6, 0, 1, 1)

        self.setMultBox = QGroupBox(self.genSimFrame)
        self.setMultBox.setObjectName(u"setMultBox")
        self.setMultBox.setMinimumSize(QSize(667, 80))
        self.setMultBox.setMaximumSize(QSize(16777215, 80))
        self.setMultBox.setFont(font1)
        self.setMultBoxLayout = QHBoxLayout(self.setMultBox)
        self.setMultBoxLayout.setSpacing(18)
        self.setMultBoxLayout.setObjectName(u"setMultBoxLayout")
        self.setMultBoxLayout.setContentsMargins(-1, 7, -1, 7)
        self.sigMultFacLayout = QVBoxLayout()
        self.sigMultFacLayout.setSpacing(4)
        self.sigMultFacLayout.setObjectName(u"sigMultFacLayout")
        self.sigMultFacLabel = QLabel(self.setMultBox)
        self.sigMultFacLabel.setObjectName(u"sigMultFacLabel")
        self.sigMultFacLabel.setMinimumSize(QSize(250, 16))
        self.sigMultFacLabel.setMaximumSize(QSize(16777215, 16))
        self.sigMultFacLabel.setFont(font1)

        self.sigMultFacLayout.addWidget(self.sigMultFacLabel)

        self.sigMultLvlLayout = QHBoxLayout()
        self.sigMultLvlLayout.setSpacing(12)
        self.sigMultLvlLayout.setObjectName(u"sigMultLvlLayout")
        self.sigMultMinLayout = QHBoxLayout()
        self.sigMultMinLayout.setSpacing(0)
        self.sigMultMinLayout.setObjectName(u"sigMultMinLayout")
        self.sigMultMinLabel = QLabel(self.setMultBox)
        self.sigMultMinLabel.setObjectName(u"sigMultMinLabel")
        self.sigMultMinLabel.setFont(font2)

        self.sigMultMinLayout.addWidget(self.sigMultMinLabel)

        self.sigMultMin = QDoubleSpinBox(self.setMultBox)
        self.sigMultMin.setObjectName(u"sigMultMin")
        self.sigMultMin.setMinimumSize(QSize(120, 22))
        self.sigMultMin.setMaximumSize(QSize(16777215, 22))
        self.sigMultMin.setFont(font2)
        self.sigMultMin.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.sigMultMin.setMinimum(0.100000000000000)
        self.sigMultMin.setMaximum(10.000000000000000)
        self.sigMultMin.setSingleStep(0.500000000000000)
        self.sigMultMin.setValue(0.800000000000000)

        self.sigMultMinLayout.addWidget(self.sigMultMin)


        self.sigMultLvlLayout.addLayout(self.sigMultMinLayout)

        self.sigMultMaxLayout = QHBoxLayout()
        self.sigMultMaxLayout.setSpacing(0)
        self.sigMultMaxLayout.setObjectName(u"sigMultMaxLayout")
        self.sigMultMaxLabel = QLabel(self.setMultBox)
        self.sigMultMaxLabel.setObjectName(u"sigMultMaxLabel")
        self.sigMultMaxLabel.setFont(font2)

        self.sigMultMaxLayout.addWidget(self.sigMultMaxLabel)

        self.sigMultMax = QDoubleSpinBox(self.setMultBox)
        self.sigMultMax.setObjectName(u"sigMultMax")
        self.sigMultMax.setMinimumSize(QSize(120, 22))
        self.sigMultMax.setMaximumSize(QSize(16777215, 22))
        self.sigMultMax.setFont(font2)
        self.sigMultMax.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.sigMultMax.setMinimum(0.100000000000000)
        self.sigMultMax.setMaximum(10.000000000000000)
        self.sigMultMax.setSingleStep(0.500000000000000)
        self.sigMultMax.setValue(1.500000000000000)

        self.sigMultMaxLayout.addWidget(self.sigMultMax)


        self.sigMultLvlLayout.addLayout(self.sigMultMaxLayout)


        self.sigMultFacLayout.addLayout(self.sigMultLvlLayout)


        self.setMultBoxLayout.addLayout(self.sigMultFacLayout)

        self.setMultSeparator = QFrame(self.setMultBox)
        self.setMultSeparator.setObjectName(u"setMultSeparator")
        self.setMultSeparator.setFrameShape(QFrame.Shape.VLine)
        self.setMultSeparator.setFrameShadow(QFrame.Shadow.Sunken)

        self.setMultBoxLayout.addWidget(self.setMultSeparator)

        self.noiMultFacLayout = QVBoxLayout()
        self.noiMultFacLayout.setSpacing(4)
        self.noiMultFacLayout.setObjectName(u"noiMultFacLayout")
        self.noiMultFacLabel = QLabel(self.setMultBox)
        self.noiMultFacLabel.setObjectName(u"noiMultFacLabel")
        self.noiMultFacLabel.setMinimumSize(QSize(250, 16))
        self.noiMultFacLabel.setMaximumSize(QSize(16777215, 16))
        self.noiMultFacLabel.setFont(font1)

        self.noiMultFacLayout.addWidget(self.noiMultFacLabel)

        self.noiMultLvlLayout = QHBoxLayout()
        self.noiMultLvlLayout.setSpacing(12)
        self.noiMultLvlLayout.setObjectName(u"noiMultLvlLayout")
        self.noiMultMinLayout = QHBoxLayout()
        self.noiMultMinLayout.setSpacing(0)
        self.noiMultMinLayout.setObjectName(u"noiMultMinLayout")
        self.noiMultMinLabel = QLabel(self.setMultBox)
        self.noiMultMinLabel.setObjectName(u"noiMultMinLabel")
        self.noiMultMinLabel.setFont(font2)

        self.noiMultMinLayout.addWidget(self.noiMultMinLabel)

        self.noiMultMin = QDoubleSpinBox(self.setMultBox)
        self.noiMultMin.setObjectName(u"noiMultMin")
        self.noiMultMin.setMinimumSize(QSize(120, 22))
        self.noiMultMin.setMaximumSize(QSize(16777215, 22))
        self.noiMultMin.setFont(font2)
        self.noiMultMin.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.noiMultMin.setMinimum(0.100000000000000)
        self.noiMultMin.setMaximum(10.000000000000000)
        self.noiMultMin.setSingleStep(0.500000000000000)
        self.noiMultMin.setValue(1.000000000000000)

        self.noiMultMinLayout.addWidget(self.noiMultMin)


        self.noiMultLvlLayout.addLayout(self.noiMultMinLayout)

        self.noiMultMaxLayout = QHBoxLayout()
        self.noiMultMaxLayout.setSpacing(0)
        self.noiMultMaxLayout.setObjectName(u"noiMultMaxLayout")
        self.noiMultMaxLabel = QLabel(self.setMultBox)
        self.noiMultMaxLabel.setObjectName(u"noiMultMaxLabel")
        self.noiMultMaxLabel.setFont(font2)

        self.noiMultMaxLayout.addWidget(self.noiMultMaxLabel)

        self.noiMultMax = QDoubleSpinBox(self.setMultBox)
        self.noiMultMax.setObjectName(u"noiMultMax")
        self.noiMultMax.setMinimumSize(QSize(120, 22))
        self.noiMultMax.setMaximumSize(QSize(16777215, 22))
        self.noiMultMax.setFont(font2)
        self.noiMultMax.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.noiMultMax.setMinimum(0.100000000000000)
        self.noiMultMax.setMaximum(10.000000000000000)
        self.noiMultMax.setSingleStep(0.500000000000000)
        self.noiMultMax.setValue(2.500000000000000)

        self.noiMultMaxLayout.addWidget(self.noiMultMax)


        self.noiMultLvlLayout.addLayout(self.noiMultMaxLayout)


        self.noiMultFacLayout.addLayout(self.noiMultLvlLayout)


        self.setMultBoxLayout.addLayout(self.noiMultFacLayout)


        self.genSimLayout.addWidget(self.setMultBox, 6, 1, 1, 3)

        self.setBslnBox = QGroupBox(self.genSimFrame)
        self.setBslnBox.setObjectName(u"setBslnBox")
        self.setBslnBox.setMinimumSize(QSize(645, 145))
        self.setBslnBox.setMaximumSize(QSize(16777215, 145))
        self.setBslnBox.setFont(font1)
        self.setBslnLayout = QVBoxLayout(self.setBslnBox)
        self.setBslnLayout.setObjectName(u"setBslnLayout")
        self.bslAgmtSetLayout = QGridLayout()
        self.bslAgmtSetLayout.setObjectName(u"bslAgmtSetLayout")
        self.bslAgmtSetLayout.setHorizontalSpacing(18)
        self.bslAgmtSetLayout.setVerticalSpacing(4)
        self.bslAgmtMthdLabel = QLabel(self.setBslnBox)
        self.bslAgmtMthdLabel.setObjectName(u"bslAgmtMthdLabel")
        self.bslAgmtMthdLabel.setMinimumSize(QSize(65, 16))
        self.bslAgmtMthdLabel.setMaximumSize(QSize(16777215, 16))
        self.bslAgmtMthdLabel.setFont(font1)

        self.bslAgmtSetLayout.addWidget(self.bslAgmtMthdLabel, 0, 0, 1, 1)

        self.bslNosLabel = QLabel(self.setBslnBox)
        self.bslNosLabel.setObjectName(u"bslNosLabel")
        self.bslNosLabel.setMinimumSize(QSize(120, 16))
        self.bslNosLabel.setMaximumSize(QSize(16777215, 16))
        self.bslNosLabel.setFont(font2)

        self.bslAgmtSetLayout.addWidget(self.bslNosLabel, 0, 1, 1, 1)

        self.bslCstLabel = QLabel(self.setBslnBox)
        self.bslCstLabel.setObjectName(u"bslCstLabel")
        self.bslCstLabel.setMinimumSize(QSize(120, 16))
        self.bslCstLabel.setMaximumSize(QSize(16777215, 16))
        self.bslCstLabel.setFont(font2)

        self.bslAgmtSetLayout.addWidget(self.bslCstLabel, 0, 2, 1, 1)

        self.bslLinLabel = QLabel(self.setBslnBox)
        self.bslLinLabel.setObjectName(u"bslLinLabel")
        self.bslLinLabel.setMinimumSize(QSize(120, 16))
        self.bslLinLabel.setMaximumSize(QSize(16777215, 16))
        self.bslLinLabel.setFont(font2)

        self.bslAgmtSetLayout.addWidget(self.bslLinLabel, 0, 3, 1, 1)

        self.bslSinLabel = QLabel(self.setBslnBox)
        self.bslSinLabel.setObjectName(u"bslSinLabel")
        self.bslSinLabel.setMinimumSize(QSize(120, 16))
        self.bslSinLabel.setMaximumSize(QSize(16777215, 16))
        self.bslSinLabel.setFont(font2)

        self.bslAgmtSetLayout.addWidget(self.bslSinLabel, 0, 4, 1, 1)

        self.bslAgmtRateLabel = QLabel(self.setBslnBox)
        self.bslAgmtRateLabel.setObjectName(u"bslAgmtRateLabel")
        self.bslAgmtRateLabel.setMinimumSize(QSize(65, 16))
        self.bslAgmtRateLabel.setMaximumSize(QSize(16777215, 16))
        self.bslAgmtRateLabel.setFont(font1)

        self.bslAgmtSetLayout.addWidget(self.bslAgmtRateLabel, 1, 0, 1, 1)

        self.bslNos = QDoubleSpinBox(self.setBslnBox)
        self.bslNos.setObjectName(u"bslNos")
        self.bslNos.setMinimumSize(QSize(120, 22))
        self.bslNos.setMaximumSize(QSize(16777215, 22))
        self.bslNos.setFont(font2)
        self.bslNos.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.bslNos.setDecimals(1)
        self.bslNos.setValue(2.000000000000000)

        self.bslAgmtSetLayout.addWidget(self.bslNos, 1, 1, 1, 1)

        self.bslCst = QDoubleSpinBox(self.setBslnBox)
        self.bslCst.setObjectName(u"bslCst")
        self.bslCst.setMinimumSize(QSize(120, 22))
        self.bslCst.setMaximumSize(QSize(16777215, 22))
        self.bslCst.setFont(font2)
        self.bslCst.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.bslCst.setDecimals(1)
        self.bslCst.setValue(1.000000000000000)

        self.bslAgmtSetLayout.addWidget(self.bslCst, 1, 2, 1, 1)

        self.bslLin = QDoubleSpinBox(self.setBslnBox)
        self.bslLin.setObjectName(u"bslLin")
        self.bslLin.setMinimumSize(QSize(120, 22))
        self.bslLin.setMaximumSize(QSize(16777215, 22))
        self.bslLin.setFont(font2)
        self.bslLin.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.bslLin.setDecimals(1)
        self.bslLin.setValue(1.000000000000000)

        self.bslAgmtSetLayout.addWidget(self.bslLin, 1, 3, 1, 1)

        self.bslSin = QDoubleSpinBox(self.setBslnBox)
        self.bslSin.setObjectName(u"bslSin")
        self.bslSin.setMinimumSize(QSize(120, 22))
        self.bslSin.setMaximumSize(QSize(16777215, 22))
        self.bslSin.setFont(font2)
        self.bslSin.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.bslSin.setDecimals(1)
        self.bslSin.setValue(1.000000000000000)

        self.bslAgmtSetLayout.addWidget(self.bslSin, 1, 4, 1, 1)


        self.setBslnLayout.addLayout(self.bslAgmtSetLayout)

        self.setBslnSeparator = QFrame(self.setBslnBox)
        self.setBslnSeparator.setObjectName(u"setBslnSeparator")
        self.setBslnSeparator.setFrameShape(QFrame.Shape.HLine)
        self.setBslnSeparator.setFrameShadow(QFrame.Shadow.Sunken)

        self.setBslnLayout.addWidget(self.setBslnSeparator)

        self.bslAgmtValLayout = QHBoxLayout()
        self.bslAgmtValLayout.setSpacing(18)
        self.bslAgmtValLayout.setObjectName(u"bslAgmtValLayout")
        self.bslAgmtAmpLayout = QVBoxLayout()
        self.bslAgmtAmpLayout.setSpacing(4)
        self.bslAgmtAmpLayout.setObjectName(u"bslAgmtAmpLayout")
        self.bslAgmtAmpLabel = QLabel(self.setBslnBox)
        self.bslAgmtAmpLabel.setObjectName(u"bslAgmtAmpLabel")
        self.bslAgmtAmpLabel.setMinimumSize(QSize(250, 16))
        self.bslAgmtAmpLabel.setMaximumSize(QSize(16777215, 16))
        self.bslAgmtAmpLabel.setFont(font1)

        self.bslAgmtAmpLayout.addWidget(self.bslAgmtAmpLabel)

        self.bslAmpLayout = QHBoxLayout()
        self.bslAmpLayout.setSpacing(12)
        self.bslAmpLayout.setObjectName(u"bslAmpLayout")
        self.bslAmpMinLayout = QHBoxLayout()
        self.bslAmpMinLayout.setSpacing(0)
        self.bslAmpMinLayout.setObjectName(u"bslAmpMinLayout")
        self.bslAmpMinLabel = QLabel(self.setBslnBox)
        self.bslAmpMinLabel.setObjectName(u"bslAmpMinLabel")
        self.bslAmpMinLabel.setFont(font2)

        self.bslAmpMinLayout.addWidget(self.bslAmpMinLabel)

        self.bslAmpMin = QDoubleSpinBox(self.setBslnBox)
        self.bslAmpMin.setObjectName(u"bslAmpMin")
        self.bslAmpMin.setMinimumSize(QSize(115, 22))
        self.bslAmpMin.setMaximumSize(QSize(16777215, 22))
        self.bslAmpMin.setFont(font2)
        self.bslAmpMin.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.bslAmpMin.setMinimum(-100.000000000000000)
        self.bslAmpMin.setMaximum(100.000000000000000)
        self.bslAmpMin.setSingleStep(0.500000000000000)
        self.bslAmpMin.setValue(-20.000000000000000)

        self.bslAmpMinLayout.addWidget(self.bslAmpMin)


        self.bslAmpLayout.addLayout(self.bslAmpMinLayout)

        self.bslAmpMaxLayout = QHBoxLayout()
        self.bslAmpMaxLayout.setSpacing(0)
        self.bslAmpMaxLayout.setObjectName(u"bslAmpMaxLayout")
        self.bslAmpMaxLabel = QLabel(self.setBslnBox)
        self.bslAmpMaxLabel.setObjectName(u"bslAmpMaxLabel")
        self.bslAmpMaxLabel.setFont(font2)

        self.bslAmpMaxLayout.addWidget(self.bslAmpMaxLabel)

        self.bslAmpMax = QDoubleSpinBox(self.setBslnBox)
        self.bslAmpMax.setObjectName(u"bslAmpMax")
        self.bslAmpMax.setMinimumSize(QSize(115, 22))
        self.bslAmpMax.setMaximumSize(QSize(16777215, 22))
        self.bslAmpMax.setFont(font2)
        self.bslAmpMax.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.bslAmpMax.setMinimum(-100.000000000000000)
        self.bslAmpMax.setMaximum(100.000000000000000)
        self.bslAmpMax.setSingleStep(0.500000000000000)
        self.bslAmpMax.setValue(20.000000000000000)

        self.bslAmpMaxLayout.addWidget(self.bslAmpMax)


        self.bslAmpLayout.addLayout(self.bslAmpMaxLayout)


        self.bslAgmtAmpLayout.addLayout(self.bslAmpLayout)


        self.bslAgmtValLayout.addLayout(self.bslAgmtAmpLayout)

        self.bslAgmtValSeparator = QFrame(self.setBslnBox)
        self.bslAgmtValSeparator.setObjectName(u"bslAgmtValSeparator")
        self.bslAgmtValSeparator.setFrameShape(QFrame.Shape.VLine)
        self.bslAgmtValSeparator.setFrameShadow(QFrame.Shadow.Sunken)

        self.bslAgmtValLayout.addWidget(self.bslAgmtValSeparator)

        self.bslAgmtFrqLayout = QVBoxLayout()
        self.bslAgmtFrqLayout.setSpacing(4)
        self.bslAgmtFrqLayout.setObjectName(u"bslAgmtFrqLayout")
        self.bslAgmtFrqLabel = QLabel(self.setBslnBox)
        self.bslAgmtFrqLabel.setObjectName(u"bslAgmtFrqLabel")
        self.bslAgmtFrqLabel.setMinimumSize(QSize(250, 16))
        self.bslAgmtFrqLabel.setMaximumSize(QSize(16777215, 16))
        self.bslAgmtFrqLabel.setFont(font1)

        self.bslAgmtFrqLayout.addWidget(self.bslAgmtFrqLabel)

        self.bslFrqLayout = QHBoxLayout()
        self.bslFrqLayout.setSpacing(12)
        self.bslFrqLayout.setObjectName(u"bslFrqLayout")
        self.bslFrqMinLayout = QHBoxLayout()
        self.bslFrqMinLayout.setSpacing(0)
        self.bslFrqMinLayout.setObjectName(u"bslFrqMinLayout")
        self.bslFrqMinLabel = QLabel(self.setBslnBox)
        self.bslFrqMinLabel.setObjectName(u"bslFrqMinLabel")
        self.bslFrqMinLabel.setFont(font2)

        self.bslFrqMinLayout.addWidget(self.bslFrqMinLabel)

        self.bslFrqMin = QDoubleSpinBox(self.setBslnBox)
        self.bslFrqMin.setObjectName(u"bslFrqMin")
        self.bslFrqMin.setMinimumSize(QSize(115, 22))
        self.bslFrqMin.setMaximumSize(QSize(16777215, 22))
        self.bslFrqMin.setFont(font2)
        self.bslFrqMin.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.bslFrqMin.setMinimum(0.000000000000000)
        self.bslFrqMin.setMaximum(1000.000000000000000)
        self.bslFrqMin.setSingleStep(1.000000000000000)
        self.bslFrqMin.setValue(2.000000000000000)

        self.bslFrqMinLayout.addWidget(self.bslFrqMin)


        self.bslFrqLayout.addLayout(self.bslFrqMinLayout)

        self.bslFrqMaxLayout = QHBoxLayout()
        self.bslFrqMaxLayout.setSpacing(0)
        self.bslFrqMaxLayout.setObjectName(u"bslFrqMaxLayout")
        self.bslFrqMaxLabel = QLabel(self.setBslnBox)
        self.bslFrqMaxLabel.setObjectName(u"bslFrqMaxLabel")
        self.bslFrqMaxLabel.setFont(font2)

        self.bslFrqMaxLayout.addWidget(self.bslFrqMaxLabel)

        self.bslFrqMax = QDoubleSpinBox(self.setBslnBox)
        self.bslFrqMax.setObjectName(u"bslFrqMax")
        self.bslFrqMax.setMinimumSize(QSize(115, 22))
        self.bslFrqMax.setMaximumSize(QSize(16777215, 22))
        self.bslFrqMax.setFont(font2)
        self.bslFrqMax.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.bslFrqMax.setMinimum(0.000000000000000)
        self.bslFrqMax.setMaximum(1000.000000000000000)
        self.bslFrqMax.setSingleStep(0.500000000000000)
        self.bslFrqMax.setValue(50.000000000000000)

        self.bslFrqMaxLayout.addWidget(self.bslFrqMax)


        self.bslFrqLayout.addLayout(self.bslFrqMaxLayout)


        self.bslAgmtFrqLayout.addLayout(self.bslFrqLayout)


        self.bslAgmtValLayout.addLayout(self.bslAgmtFrqLayout)


        self.setBslnLayout.addLayout(self.bslAgmtValLayout)


        self.genSimLayout.addWidget(self.setBslnBox, 7, 0, 1, 3)

        self.mainButtonLayout = QVBoxLayout()
        self.mainButtonLayout.setSpacing(10)
        self.mainButtonLayout.setObjectName(u"mainButtonLayout")
        self.clrSetButton = QPushButton(self.genSimFrame)
        self.clrSetButton.setObjectName(u"clrSetButton")
        self.clrSetButton.setMinimumSize(QSize(445, 45))
        self.clrSetButton.setMaximumSize(QSize(16777215, 45))
        font3 = QFont()
        font3.setPointSize(14)
        font3.setBold(False)
        self.clrSetButton.setFont(font3)

        self.mainButtonLayout.addWidget(self.clrSetButton)

        self.genSimButton = QPushButton(self.genSimFrame)
        self.genSimButton.setObjectName(u"genSimButton")
        self.genSimButton.setMinimumSize(QSize(445, 45))
        self.genSimButton.setMaximumSize(QSize(16777215, 45))
        self.genSimButton.setFont(font)

        self.mainButtonLayout.addWidget(self.genSimButton)


        self.genSimLayout.addLayout(self.mainButtonLayout, 7, 3, 1, 1)

        self.genSimLabel = QLabel(self.genSimFrame)
        self.genSimLabel.setObjectName(u"genSimLabel")
        self.genSimLabel.setMinimumSize(QSize(1110, 28))
        self.genSimLabel.setMaximumSize(QSize(16777215, 28))
        self.genSimLabel.setFont(font)

        self.genSimLayout.addWidget(self.genSimLabel, 0, 0, 1, 4)


        self.argFrameLayout.addWidget(self.genSimFrame)

        self.genStaFrame = QFrame(self.argFrame)
        self.genStaFrame.setObjectName(u"genStaFrame")
        self.genStaFrame.setMinimumSize(QSize(1132, 165))
        self.genStaFrame.setMaximumSize(QSize(1132, 165))
        self.genStaFrame.setFrameShape(QFrame.Shape.Box)
        self.genStaFrame.setFrameShadow(QFrame.Shadow.Sunken)
        self.genStaLayout = QVBoxLayout(self.genStaFrame)
        self.genStaLayout.setObjectName(u"genStaLayout")
        self.genStaLayout.setContentsMargins(-1, 0, -1, -1)
        self.genStaLabel = QLabel(self.genStaFrame)
        self.genStaLabel.setObjectName(u"genStaLabel")
        self.genStaLabel.setMinimumSize(QSize(1110, 28))
        self.genStaLabel.setMaximumSize(QSize(16777215, 28))
        self.genStaLabel.setFont(font)

        self.genStaLayout.addWidget(self.genStaLabel)

        self.genStaLabelSeparator = QFrame(self.genStaFrame)
        self.genStaLabelSeparator.setObjectName(u"genStaLabelSeparator")
        self.genStaLabelSeparator.setMinimumSize(QSize(1110, 0))
        self.genStaLabelSeparator.setFrameShape(QFrame.Shape.HLine)
        self.genStaLabelSeparator.setFrameShadow(QFrame.Shadow.Sunken)

        self.genStaLayout.addWidget(self.genStaLabelSeparator)

        self.statFileBox = QGroupBox(self.genStaFrame)
        self.statFileBox.setObjectName(u"statFileBox")
        self.statFileBox.setMinimumSize(QSize(1110, 60))
        self.statFileBox.setMaximumSize(QSize(16777215, 60))
        self.statFileBox.setFont(font1)
        self.sigBoxLayout_2 = QHBoxLayout(self.statFileBox)
        self.sigBoxLayout_2.setSpacing(10)
        self.sigBoxLayout_2.setObjectName(u"sigBoxLayout_2")
        self.statFilePath = QLineEdit(self.statFileBox)
        self.statFilePath.setObjectName(u"statFilePath")
        self.statFilePath.setMinimumSize(QSize(1000, 22))
        self.statFilePath.setMaximumSize(QSize(16777215, 22))
        self.statFilePath.setFont(font2)

        self.sigBoxLayout_2.addWidget(self.statFilePath)

        self.statFileSelect = QPushButton(self.statFileBox)
        self.statFileSelect.setObjectName(u"statFileSelect")
        self.statFileSelect.setMinimumSize(QSize(80, 24))
        self.statFileSelect.setMaximumSize(QSize(80, 24))
        self.statFileSelect.setFont(font2)

        self.sigBoxLayout_2.addWidget(self.statFileSelect)


        self.genStaLayout.addWidget(self.statFileBox)

        self.genStaButton = QPushButton(self.genStaFrame)
        self.genStaButton.setObjectName(u"genStaButton")
        self.genStaButton.setMinimumSize(QSize(1110, 45))
        self.genStaButton.setMaximumSize(QSize(16777215, 45))
        self.genStaButton.setFont(font)

        self.genStaLayout.addWidget(self.genStaButton)


        self.argFrameLayout.addWidget(self.genStaFrame)


        self.mainLayout.addWidget(self.argFrame)

        ParusGenWindow.setCentralWidget(self.centralWidget)
        self.statBar = QStatusBar(ParusGenWindow)
        self.statBar.setObjectName(u"statBar")
        ParusGenWindow.setStatusBar(self.statBar)

        self.retranslateUi(ParusGenWindow)

        QMetaObject.connectSlotsByName(ParusGenWindow)
    # setupUi

    def retranslateUi(self, ParusGenWindow):
        ParusGenWindow.setWindowTitle(QCoreApplication.translate("ParusGenWindow", u"Parus - Signal Simulation", None))
        self.procConLabel.setText(QCoreApplication.translate("ParusGenWindow", u"System Console", None))
        self.procConClear.setText(QCoreApplication.translate("ParusGenWindow", u"Clear", None))
        self.procConCopy.setText(QCoreApplication.translate("ParusGenWindow", u"Copy", None))
        self.procConScroll.setText(QCoreApplication.translate("ParusGenWindow", u"Auto Scroll", None))
        self.sigBox.setTitle(QCoreApplication.translate("ParusGenWindow", u"Archived Signal Directory", None))
        self.sigPath.setPlaceholderText(QCoreApplication.translate("ParusGenWindow", u"Select folder contains archived signal files (*.arc)", None))
        self.sigSelect.setText(QCoreApplication.translate("ParusGenWindow", u"Open", None))
        self.noiBox.setTitle(QCoreApplication.translate("ParusGenWindow", u"Archived Noise Directory", None))
        self.noiPath.setPlaceholderText(QCoreApplication.translate("ParusGenWindow", u"Select folder contains archived noise files (*.noi)", None))
        self.noiSelect.setText(QCoreApplication.translate("ParusGenWindow", u"Open", None))
        self.outBox.setTitle(QCoreApplication.translate("ParusGenWindow", u"Generated Signal Output Directory", None))
        self.outPath.setPlaceholderText(QCoreApplication.translate("ParusGenWindow", u"Select folder for storing generated signals", None))
        self.outSelect.setText(QCoreApplication.translate("ParusGenWindow", u"Open", None))
        self.setBaseBox.setTitle(QCoreApplication.translate("ParusGenWindow", u"Basic Settings", None))
        self.sampCntLabel.setText(QCoreApplication.translate("ParusGenWindow", u"# Signals to Generate", None))
        self.sampLenLabel.setText(QCoreApplication.translate("ParusGenWindow", u"Length of Each Signal", None))
        self.sampLen.setSuffix(QCoreApplication.translate("ParusGenWindow", u" ms", None))
        self.sampFreqLabel.setText(QCoreApplication.translate("ParusGenWindow", u"Sampling Frequency", None))
        self.sampFreq.setSuffix(QCoreApplication.translate("ParusGenWindow", u" Hz", None))
        self.exEgLabel.setText(QCoreApplication.translate("ParusGenWindow", u"# Extra Samples", None))
#if QT_CONFIG(tooltip)
        self.exEg.setToolTip(QCoreApplication.translate("ParusGenWindow", u"Extra samples for complete validation coverage", None))
#endif // QT_CONFIG(tooltip)
        self.setRateBox.setTitle(QCoreApplication.translate("ParusGenWindow", u"Grouping and Ratio Control", None))
        self.spkGrpMthdLabel.setText(QCoreApplication.translate("ParusGenWindow", u"Spike Grouping", None))
        self.spkGrpMthd.setItemText(0, QCoreApplication.translate("ParusGenWindow", u"No Grouping", None))
        self.spkGrpMthd.setItemText(1, QCoreApplication.translate("ParusGenWindow", u"Cell Type", None))
        self.spkGrpMthd.setItemText(2, QCoreApplication.translate("ParusGenWindow", u"Spike Type", None))

        self.spkGrpRateLabel.setText(QCoreApplication.translate("ParusGenWindow", u"Spike Grouping Ratios", None))
#if QT_CONFIG(tooltip)
        self.spkGrpRate.setToolTip(QCoreApplication.translate("ParusGenWindow", u"<html><head/><body><p>Occurrence ratio of groups</p><p> - The order is associated with the group names alphabetical order</p><p> - Suggested to be the same length of group number</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.spkGrpRate.setPlaceholderText(QCoreApplication.translate("ParusGenWindow", u"Magnitude of each group, separate with space", None))
        self.noiOnlyRateLabel.setText(QCoreApplication.translate("ParusGenWindow", u"Noise Only Ratio", None))
        self.noiOnlyRate.setSuffix(QCoreApplication.translate("ParusGenWindow", u" %", None))
        self.setOccrBox.setTitle(QCoreApplication.translate("ParusGenWindow", u"Spike Occurrence", None))
        self.minSpkFreqLabel.setText(QCoreApplication.translate("ParusGenWindow", u"Min Firing Frequency", None))
        self.minSpkFreq.setSuffix(QCoreApplication.translate("ParusGenWindow", u" Hz", None))
        self.maxSpkFreqLabel.setText(QCoreApplication.translate("ParusGenWindow", u"Max Firing Frequency", None))
        self.maxSpkFreq.setSuffix(QCoreApplication.translate("ParusGenWindow", u" Hz", None))
        self.chnCellCntLabel.setText(QCoreApplication.translate("ParusGenWindow", u"Max Cells/Channel", None))
        self.setMultBox.setTitle(QCoreApplication.translate("ParusGenWindow", u"Sample Multiplication", None))
        self.sigMultFacLabel.setText(QCoreApplication.translate("ParusGenWindow", u"Signal Amplitude Multiplication Factor", None))
        self.sigMultMinLabel.setText(QCoreApplication.translate("ParusGenWindow", u"Min", None))
        self.sigMultMin.setSuffix(QCoreApplication.translate("ParusGenWindow", u" x", None))
        self.sigMultMaxLabel.setText(QCoreApplication.translate("ParusGenWindow", u"Max", None))
        self.sigMultMax.setSuffix(QCoreApplication.translate("ParusGenWindow", u" x", None))
        self.noiMultFacLabel.setText(QCoreApplication.translate("ParusGenWindow", u"Noise Level Multiplication Factor", None))
        self.noiMultMinLabel.setText(QCoreApplication.translate("ParusGenWindow", u"Min", None))
        self.noiMultMin.setSuffix(QCoreApplication.translate("ParusGenWindow", u" x", None))
        self.noiMultMaxLabel.setText(QCoreApplication.translate("ParusGenWindow", u"Max", None))
        self.noiMultMax.setSuffix(QCoreApplication.translate("ParusGenWindow", u" x", None))
        self.setBslnBox.setTitle(QCoreApplication.translate("ParusGenWindow", u"Baseline Augmentation", None))
        self.bslAgmtMthdLabel.setText(QCoreApplication.translate("ParusGenWindow", u"Method", None))
        self.bslNosLabel.setText(QCoreApplication.translate("ParusGenWindow", u"No Shifting", None))
        self.bslCstLabel.setText(QCoreApplication.translate("ParusGenWindow", u"Constant", None))
        self.bslLinLabel.setText(QCoreApplication.translate("ParusGenWindow", u"Linear", None))
        self.bslSinLabel.setText(QCoreApplication.translate("ParusGenWindow", u"Sinusoid", None))
        self.bslAgmtRateLabel.setText(QCoreApplication.translate("ParusGenWindow", u"Magnitude", None))
        self.bslNos.setSuffix("")
        self.bslCst.setSuffix("")
        self.bslLin.setSuffix("")
        self.bslSin.setSuffix("")
        self.bslAgmtAmpLabel.setText(QCoreApplication.translate("ParusGenWindow", u"Shifting Amplitude (for Constant/Linear/Sinusiod)", None))
        self.bslAmpMinLabel.setText(QCoreApplication.translate("ParusGenWindow", u"Min", None))
        self.bslAmpMin.setSuffix(QCoreApplication.translate("ParusGenWindow", u" unit", None))
        self.bslAmpMaxLabel.setText(QCoreApplication.translate("ParusGenWindow", u"Max", None))
        self.bslAmpMax.setSuffix(QCoreApplication.translate("ParusGenWindow", u" unit", None))
        self.bslAgmtFrqLabel.setText(QCoreApplication.translate("ParusGenWindow", u"Shifting Frequency (for Sinusoid)", None))
        self.bslFrqMinLabel.setText(QCoreApplication.translate("ParusGenWindow", u"Min", None))
        self.bslFrqMin.setSuffix(QCoreApplication.translate("ParusGenWindow", u" Hz", None))
        self.bslFrqMaxLabel.setText(QCoreApplication.translate("ParusGenWindow", u"Max", None))
        self.bslFrqMax.setSuffix(QCoreApplication.translate("ParusGenWindow", u" Hz", None))
        self.clrSetButton.setText(QCoreApplication.translate("ParusGenWindow", u"Clear Settings", None))
        self.genSimButton.setText(QCoreApplication.translate("ParusGenWindow", u"Start Generation", None))
        self.genSimLabel.setText(QCoreApplication.translate("ParusGenWindow", u"Simulated Signal Generation", None))
        self.genStaLabel.setText(QCoreApplication.translate("ParusGenWindow", u"View Generation Statistics", None))
        self.statFileBox.setTitle(QCoreApplication.translate("ParusGenWindow", u"Generation Statistics File Path", None))
        self.statFilePath.setPlaceholderText(QCoreApplication.translate("ParusGenWindow", u"Select simulated signal generation statistics file (*.cjh)", None))
        self.statFileSelect.setText(QCoreApplication.translate("ParusGenWindow", u"Open", None))
        self.genStaButton.setText(QCoreApplication.translate("ParusGenWindow", u"View Statistics", None))
    # retranslateUi

