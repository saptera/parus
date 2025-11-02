# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'desg_modtrn.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QComboBox, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                               QSizePolicy, QSpacerItem, QSpinBox, QStatusBar, QTextEdit, QVBoxLayout, QWidget)


class Ui_ParusTrnWindow(object):
    def setupUi(self, ParusTrnWindow):
        if not ParusTrnWindow.objectName():
            ParusTrnWindow.setObjectName(u"ParusTrnWindow")
        ParusTrnWindow.resize(1168, 951)
        self.centralWidget = QWidget(ParusTrnWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.centralLayout = QVBoxLayout(self.centralWidget)
        self.centralLayout.setObjectName(u"centralLayout")
        self.conFrame = QFrame(self.centralWidget)
        self.conFrame.setObjectName(u"conFrame")
        self.conFrame.setMinimumSize(QSize(1150, 260))
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


        self.centralLayout.addWidget(self.conFrame)

        self.trnFrame = QFrame(self.centralWidget)
        self.trnFrame.setObjectName(u"trnFrame")
        self.trnFrame.setMinimumSize(QSize(1150, 470))
        self.trnFrame.setMaximumSize(QSize(16777215, 470))
        self.trnFrame.setFrameShape(QFrame.Shape.Box)
        self.trnFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.trnFrameLayout = QVBoxLayout(self.trnFrame)
        self.trnFrameLayout.setObjectName(u"trnFrameLayout")
        self.trnFrameLayout.setContentsMargins(-1, 0, -1, 5)
        self.trnConLabel = QLabel(self.trnFrame)
        self.trnConLabel.setObjectName(u"trnConLabel")
        self.trnConLabel.setMinimumSize(QSize(1000, 28))
        self.trnConLabel.setMaximumSize(QSize(16777215, 28))
        self.trnConLabel.setFont(font)

        self.trnFrameLayout.addWidget(self.trnConLabel)

        self.simBox = QGroupBox(self.trnFrame)
        self.simBox.setObjectName(u"simBox")
        self.simBox.setMinimumSize(QSize(1110, 70))
        self.simBox.setMaximumSize(QSize(16777215, 70))
        font2 = QFont()
        font2.setPointSize(12)
        font2.setBold(True)
        self.simBox.setFont(font2)
        self.simBoxLayout = QHBoxLayout(self.simBox)
        self.simBoxLayout.setSpacing(10)
        self.simBoxLayout.setObjectName(u"simBoxLayout")
        self.simPath = QLineEdit(self.simBox)
        self.simPath.setObjectName(u"simPath")
        self.simPath.setMinimumSize(QSize(1000, 22))
        self.simPath.setMaximumSize(QSize(16777215, 22))
        font3 = QFont()
        font3.setPointSize(9)
        font3.setBold(False)
        self.simPath.setFont(font3)

        self.simBoxLayout.addWidget(self.simPath)

        self.simSelect = QPushButton(self.simBox)
        self.simSelect.setObjectName(u"simSelect")
        self.simSelect.setMinimumSize(QSize(80, 24))
        self.simSelect.setMaximumSize(QSize(80, 24))
        self.simSelect.setFont(font3)

        self.simBoxLayout.addWidget(self.simSelect)


        self.trnFrameLayout.addWidget(self.simBox)

        self.outBox = QGroupBox(self.trnFrame)
        self.outBox.setObjectName(u"outBox")
        self.outBox.setMinimumSize(QSize(1110, 70))
        self.outBox.setMaximumSize(QSize(16777215, 70))
        self.outBox.setFont(font2)
        self.outBoxLayout = QHBoxLayout(self.outBox)
        self.outBoxLayout.setSpacing(10)
        self.outBoxLayout.setObjectName(u"outBoxLayout")
        self.outPath = QLineEdit(self.outBox)
        self.outPath.setObjectName(u"outPath")
        self.outPath.setMinimumSize(QSize(1000, 22))
        self.outPath.setMaximumSize(QSize(16777215, 22))
        self.outPath.setFont(font3)

        self.outBoxLayout.addWidget(self.outPath)

        self.outSelect = QPushButton(self.outBox)
        self.outSelect.setObjectName(u"outSelect")
        self.outSelect.setMinimumSize(QSize(80, 24))
        self.outSelect.setMaximumSize(QSize(80, 24))
        self.outSelect.setFont(font3)

        self.outBoxLayout.addWidget(self.outSelect)


        self.trnFrameLayout.addWidget(self.outBox)

        self.dsetGroup = QGroupBox(self.trnFrame)
        self.dsetGroup.setObjectName(u"dsetGroup")
        self.dsetGroup.setMinimumSize(QSize(1000, 70))
        self.dsetGroup.setMaximumSize(QSize(16777215, 70))
        self.dsetGroup.setFont(font2)
        self.dsetGrpLayout = QHBoxLayout(self.dsetGroup)
        self.dsetGrpLayout.setObjectName(u"dsetGrpLayout")
        self.trnSampLayout = QHBoxLayout()
        self.trnSampLayout.setSpacing(0)
        self.trnSampLayout.setObjectName(u"trnSampLayout")
        self.trnSampLabel = QLabel(self.dsetGroup)
        self.trnSampLabel.setObjectName(u"trnSampLabel")
        self.trnSampLabel.setMinimumSize(QSize(105, 25))
        self.trnSampLabel.setMaximumSize(QSize(105, 25))
        font4 = QFont()
        font4.setPointSize(10)
        font4.setBold(False)
        self.trnSampLabel.setFont(font4)

        self.trnSampLayout.addWidget(self.trnSampLabel)

        self.trnSampSpinbox = QSpinBox(self.dsetGroup)
        self.trnSampSpinbox.setObjectName(u"trnSampSpinbox")
        self.trnSampSpinbox.setMinimumSize(QSize(80, 25))
        self.trnSampSpinbox.setMaximumSize(QSize(80, 25))
        self.trnSampSpinbox.setFont(font3)
        self.trnSampSpinbox.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.trnSampSpinbox.setMinimum(1000)
        self.trnSampSpinbox.setMaximum(999999999)
        self.trnSampSpinbox.setValue(500000)

        self.trnSampLayout.addWidget(self.trnSampSpinbox)


        self.dsetGrpLayout.addLayout(self.trnSampLayout)

        self.destSpacerL = QSpacerItem(100, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.dsetGrpLayout.addItem(self.destSpacerL)

        self.vldSampLayout = QHBoxLayout()
        self.vldSampLayout.setSpacing(0)
        self.vldSampLayout.setObjectName(u"vldSampLayout")
        self.vldSampLabel = QLabel(self.dsetGroup)
        self.vldSampLabel.setObjectName(u"vldSampLabel")
        self.vldSampLabel.setMinimumSize(QSize(115, 25))
        self.vldSampLabel.setMaximumSize(QSize(115, 25))
        self.vldSampLabel.setFont(font4)

        self.vldSampLayout.addWidget(self.vldSampLabel)

        self.vldSampSpinbox = QSpinBox(self.dsetGroup)
        self.vldSampSpinbox.setObjectName(u"vldSampSpinbox")
        self.vldSampSpinbox.setMinimumSize(QSize(80, 25))
        self.vldSampSpinbox.setMaximumSize(QSize(80, 25))
        self.vldSampSpinbox.setFont(font3)
        self.vldSampSpinbox.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.vldSampSpinbox.setMinimum(100)
        self.vldSampSpinbox.setMaximum(999999999)
        self.vldSampSpinbox.setValue(1000)

        self.vldSampLayout.addWidget(self.vldSampSpinbox)


        self.dsetGrpLayout.addLayout(self.vldSampLayout)

        self.dsetSpacerM = QSpacerItem(100, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.dsetGrpLayout.addItem(self.dsetSpacerM)

        self.tstSampLayout = QHBoxLayout()
        self.tstSampLayout.setSpacing(0)
        self.tstSampLayout.setObjectName(u"tstSampLayout")
        self.tstSampLabel = QLabel(self.dsetGroup)
        self.tstSampLabel.setObjectName(u"tstSampLabel")
        self.tstSampLabel.setMinimumSize(QSize(100, 25))
        self.tstSampLabel.setMaximumSize(QSize(100, 25))
        self.tstSampLabel.setFont(font4)

        self.tstSampLayout.addWidget(self.tstSampLabel)

        self.tstSampSpinbox = QSpinBox(self.dsetGroup)
        self.tstSampSpinbox.setObjectName(u"tstSampSpinbox")
        self.tstSampSpinbox.setMinimumSize(QSize(80, 25))
        self.tstSampSpinbox.setMaximumSize(QSize(80, 25))
        self.tstSampSpinbox.setFont(font3)
        self.tstSampSpinbox.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.tstSampSpinbox.setMinimum(100)
        self.tstSampSpinbox.setMaximum(999999999)
        self.tstSampSpinbox.setValue(1000)

        self.tstSampLayout.addWidget(self.tstSampSpinbox)


        self.dsetGrpLayout.addLayout(self.tstSampLayout)

        self.dsetSpacerR = QSpacerItem(100, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.dsetGrpLayout.addItem(self.dsetSpacerR)

        self.seqLenLayout = QHBoxLayout()
        self.seqLenLayout.setSpacing(0)
        self.seqLenLayout.setObjectName(u"seqLenLayout")
        self.seqLenLabel = QLabel(self.dsetGroup)
        self.seqLenLabel.setObjectName(u"seqLenLabel")
        self.seqLenLabel.setMinimumSize(QSize(105, 25))
        self.seqLenLabel.setMaximumSize(QSize(105, 25))
        self.seqLenLabel.setFont(font4)

        self.seqLenLayout.addWidget(self.seqLenLabel)

        self.seqLenSpinbox = QSpinBox(self.dsetGroup)
        self.seqLenSpinbox.setObjectName(u"seqLenSpinbox")
        self.seqLenSpinbox.setMinimumSize(QSize(80, 25))
        self.seqLenSpinbox.setMaximumSize(QSize(80, 25))
        self.seqLenSpinbox.setFont(font3)
        self.seqLenSpinbox.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.seqLenSpinbox.setMinimum(100)
        self.seqLenSpinbox.setMaximum(10000)
        self.seqLenSpinbox.setValue(300)

        self.seqLenLayout.addWidget(self.seqLenSpinbox)


        self.dsetGrpLayout.addLayout(self.seqLenLayout)


        self.trnFrameLayout.addWidget(self.dsetGroup)

        self.trnGroup = QGroupBox(self.trnFrame)
        self.trnGroup.setObjectName(u"trnGroup")
        self.trnGroup.setMinimumSize(QSize(1000, 70))
        self.trnGroup.setMaximumSize(QSize(16777215, 70))
        self.trnGroup.setFont(font2)
        self.trnGrpLayout = QHBoxLayout(self.trnGroup)
        self.trnGrpLayout.setObjectName(u"trnGrpLayout")
        self.modNameLayout = QHBoxLayout()
        self.modNameLayout.setSpacing(0)
        self.modNameLayout.setObjectName(u"modNameLayout")
        self.modNameLabel = QLabel(self.trnGroup)
        self.modNameLabel.setObjectName(u"modNameLabel")
        self.modNameLabel.setMinimumSize(QSize(90, 25))
        self.modNameLabel.setMaximumSize(QSize(90, 25))
        self.modNameLabel.setFont(font4)

        self.modNameLayout.addWidget(self.modNameLabel)

        self.modNameLine = QLineEdit(self.trnGroup)
        self.modNameLine.setObjectName(u"modNameLine")
        self.modNameLine.setMinimumSize(QSize(150, 25))
        self.modNameLine.setMaximumSize(QSize(16777215, 25))
        self.modNameLine.setFont(font3)

        self.modNameLayout.addWidget(self.modNameLine)


        self.trnGrpLayout.addLayout(self.modNameLayout)

        self.trnSpacerL = QSpacerItem(100, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.trnGrpLayout.addItem(self.trnSpacerL)

        self.nEpLayout = QHBoxLayout()
        self.nEpLayout.setSpacing(0)
        self.nEpLayout.setObjectName(u"nEpLayout")
        self.nEpLabel = QLabel(self.trnGroup)
        self.nEpLabel.setObjectName(u"nEpLabel")
        self.nEpLabel.setMinimumSize(QSize(60, 25))
        self.nEpLabel.setMaximumSize(QSize(60, 25))
        self.nEpLabel.setFont(font4)

        self.nEpLayout.addWidget(self.nEpLabel)

        self.nEpSpinbox = QSpinBox(self.trnGroup)
        self.nEpSpinbox.setObjectName(u"nEpSpinbox")
        self.nEpSpinbox.setMinimumSize(QSize(80, 25))
        self.nEpSpinbox.setMaximumSize(QSize(80, 25))
        self.nEpSpinbox.setFont(font3)
        self.nEpSpinbox.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.nEpSpinbox.setMinimum(1)
        self.nEpSpinbox.setMaximum(1000)
        self.nEpSpinbox.setValue(5)

        self.nEpLayout.addWidget(self.nEpSpinbox)


        self.trnGrpLayout.addLayout(self.nEpLayout)

        self.trnSpacerM = QSpacerItem(100, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.trnGrpLayout.addItem(self.trnSpacerM)

        self.stpEvalLayout = QHBoxLayout()
        self.stpEvalLayout.setSpacing(0)
        self.stpEvalLayout.setObjectName(u"stpEvalLayout")
        self.stpEvalLabel = QLabel(self.trnGroup)
        self.stpEvalLabel.setObjectName(u"stpEvalLabel")
        self.stpEvalLabel.setMinimumSize(QSize(135, 25))
        self.stpEvalLabel.setMaximumSize(QSize(135, 25))
        self.stpEvalLabel.setFont(font4)

        self.stpEvalLayout.addWidget(self.stpEvalLabel)

        self.stpEvalSpinbox = QSpinBox(self.trnGroup)
        self.stpEvalSpinbox.setObjectName(u"stpEvalSpinbox")
        self.stpEvalSpinbox.setMinimumSize(QSize(80, 25))
        self.stpEvalSpinbox.setMaximumSize(QSize(80, 25))
        self.stpEvalSpinbox.setFont(font3)
        self.stpEvalSpinbox.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.stpEvalSpinbox.setMinimum(100)
        self.stpEvalSpinbox.setMaximum(999999999)
        self.stpEvalSpinbox.setValue(1000)

        self.stpEvalLayout.addWidget(self.stpEvalSpinbox)


        self.trnGrpLayout.addLayout(self.stpEvalLayout)

        self.trnSpacerR = QSpacerItem(100, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.trnGrpLayout.addItem(self.trnSpacerR)

        self.indEvalLayout = QHBoxLayout()
        self.indEvalLayout.setSpacing(0)
        self.indEvalLayout.setObjectName(u"indEvalLayout")
        self.indEvalLabel = QLabel(self.trnGroup)
        self.indEvalLabel.setObjectName(u"indEvalLabel")
        self.indEvalLabel.setMinimumSize(QSize(125, 25))
        self.indEvalLabel.setMaximumSize(QSize(125, 25))
        self.indEvalLabel.setFont(font4)

        self.indEvalLayout.addWidget(self.indEvalLabel)

        self.indEvalCombo = QComboBox(self.trnGroup)
        self.indEvalCombo.addItem("")
        self.indEvalCombo.addItem("")
        self.indEvalCombo.addItem("")
        self.indEvalCombo.setObjectName(u"indEvalCombo")
        self.indEvalCombo.setMinimumSize(QSize(100, 25))
        self.indEvalCombo.setMaximumSize(QSize(100, 25))
        self.indEvalCombo.setFont(font3)

        self.indEvalLayout.addWidget(self.indEvalCombo)


        self.trnGrpLayout.addLayout(self.indEvalLayout)


        self.trnFrameLayout.addWidget(self.trnGroup)

        self.exGroup = QGroupBox(self.trnFrame)
        self.exGroup.setObjectName(u"exGroup")
        self.exGroup.setMinimumSize(QSize(1000, 70))
        self.exGroup.setMaximumSize(QSize(16777215, 70))
        self.exGroup.setFont(font2)
        self.exGrpLayout = QHBoxLayout(self.exGroup)
        self.exGrpLayout.setObjectName(u"exGrpLayout")
        self.exOptLine = QLineEdit(self.exGroup)
        self.exOptLine.setObjectName(u"exOptLine")
        self.exOptLine.setMinimumSize(QSize(400, 25))
        self.exOptLine.setMaximumSize(QSize(16777215, 25))
        self.exOptLine.setFont(font3)

        self.exGrpLayout.addWidget(self.exOptLine)


        self.trnFrameLayout.addWidget(self.exGroup)

        self.trnProcButton = QPushButton(self.trnFrame)
        self.trnProcButton.setObjectName(u"trnProcButton")
        self.trnProcButton.setMinimumSize(QSize(1000, 45))
        self.trnProcButton.setMaximumSize(QSize(16777215, 45))
        self.trnProcButton.setFont(font)

        self.trnFrameLayout.addWidget(self.trnProcButton)


        self.centralLayout.addWidget(self.trnFrame)

        self.tstFrame = QFrame(self.centralWidget)
        self.tstFrame.setObjectName(u"tstFrame")
        self.tstFrame.setMinimumSize(QSize(1132, 170))
        self.tstFrame.setMaximumSize(QSize(16777215, 170))
        self.tstFrame.setFrameShape(QFrame.Shape.Box)
        self.tstFrame.setFrameShadow(QFrame.Shadow.Sunken)
        self.tstFrameLayout = QVBoxLayout(self.tstFrame)
        self.tstFrameLayout.setObjectName(u"tstFrameLayout")
        self.tstFrameLayout.setContentsMargins(-1, 0, -1, -1)
        self.tstConLabel = QLabel(self.tstFrame)
        self.tstConLabel.setObjectName(u"tstConLabel")
        self.tstConLabel.setMinimumSize(QSize(1000, 28))
        self.tstConLabel.setMaximumSize(QSize(16777215, 28))
        self.tstConLabel.setFont(font)

        self.tstFrameLayout.addWidget(self.tstConLabel)

        self.tstFileBox = QGroupBox(self.tstFrame)
        self.tstFileBox.setObjectName(u"tstFileBox")
        self.tstFileBox.setMinimumSize(QSize(1000, 70))
        self.tstFileBox.setMaximumSize(QSize(16777215, 70))
        self.tstFileBox.setFont(font2)
        self.tstFileLayout = QHBoxLayout(self.tstFileBox)
        self.tstFileLayout.setSpacing(10)
        self.tstFileLayout.setObjectName(u"tstFileLayout")
        self.tstTypeBox = QComboBox(self.tstFileBox)
        self.tstTypeBox.addItem("")
        self.tstTypeBox.addItem("")
        self.tstTypeBox.setObjectName(u"tstTypeBox")
        self.tstTypeBox.setMinimumSize(QSize(80, 24))
        self.tstTypeBox.setMaximumSize(QSize(80, 24))
        self.tstTypeBox.setFont(font3)

        self.tstFileLayout.addWidget(self.tstTypeBox)

        self.tstPathLine = QLineEdit(self.tstFileBox)
        self.tstPathLine.setObjectName(u"tstPathLine")
        self.tstPathLine.setMinimumSize(QSize(900, 22))
        self.tstPathLine.setMaximumSize(QSize(16777215, 22))
        self.tstPathLine.setFont(font3)

        self.tstFileLayout.addWidget(self.tstPathLine)

        self.tstPathSelect = QPushButton(self.tstFileBox)
        self.tstPathSelect.setObjectName(u"tstPathSelect")
        self.tstPathSelect.setMinimumSize(QSize(80, 24))
        self.tstPathSelect.setMaximumSize(QSize(80, 24))
        self.tstPathSelect.setFont(font3)

        self.tstFileLayout.addWidget(self.tstPathSelect)


        self.tstFrameLayout.addWidget(self.tstFileBox)

        self.tstViewButton = QPushButton(self.tstFrame)
        self.tstViewButton.setObjectName(u"tstViewButton")
        self.tstViewButton.setMinimumSize(QSize(1000, 45))
        self.tstViewButton.setMaximumSize(QSize(16777215, 45))
        self.tstViewButton.setFont(font)

        self.tstFrameLayout.addWidget(self.tstViewButton)


        self.centralLayout.addWidget(self.tstFrame)

        ParusTrnWindow.setCentralWidget(self.centralWidget)
        self.statBar = QStatusBar(ParusTrnWindow)
        self.statBar.setObjectName(u"statBar")
        ParusTrnWindow.setStatusBar(self.statBar)

        self.retranslateUi(ParusTrnWindow)

        self.indEvalCombo.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(ParusTrnWindow)
    # setupUi

    def retranslateUi(self, ParusTrnWindow):
        ParusTrnWindow.setWindowTitle(QCoreApplication.translate("ParusTrnWindow", u"Parus - Model Training", None))
        self.procConLabel.setText(QCoreApplication.translate("ParusTrnWindow", u"System Console", None))
        self.procConClear.setText(QCoreApplication.translate("ParusTrnWindow", u"Clear", None))
        self.procConCopy.setText(QCoreApplication.translate("ParusTrnWindow", u"Copy", None))
        self.procConScroll.setText(QCoreApplication.translate("ParusTrnWindow", u"Auto Scroll", None))
        self.trnConLabel.setText(QCoreApplication.translate("ParusTrnWindow", u"Training Settings", None))
        self.simBox.setTitle(QCoreApplication.translate("ParusTrnWindow", u"Simulated Datasets Directory", None))
        self.simPath.setPlaceholderText(QCoreApplication.translate("ParusTrnWindow", u"Select folder contains 3 sets of simulated datasets (*.sim)", None))
        self.simSelect.setText(QCoreApplication.translate("ParusTrnWindow", u"Open", None))
#if QT_CONFIG(tooltip)
        self.outBox.setToolTip(QCoreApplication.translate("ParusTrnWindow", u"Generated dataset type", None))
#endif // QT_CONFIG(tooltip)
        self.outBox.setTitle(QCoreApplication.translate("ParusTrnWindow", u"Model Output Directory", None))
        self.outPath.setPlaceholderText(QCoreApplication.translate("ParusTrnWindow", u"Select folder for storing model training results", None))
        self.outSelect.setText(QCoreApplication.translate("ParusTrnWindow", u"Open", None))
        self.dsetGroup.setTitle(QCoreApplication.translate("ParusTrnWindow", u"Dataset Input Options", None))
        self.trnSampLabel.setText(QCoreApplication.translate("ParusTrnWindow", u"Training Samples", None))
        self.vldSampLabel.setText(QCoreApplication.translate("ParusTrnWindow", u"Validation Samples", None))
        self.tstSampLabel.setText(QCoreApplication.translate("ParusTrnWindow", u"Testing Samples", None))
        self.seqLenLabel.setText(QCoreApplication.translate("ParusTrnWindow", u"Sequence Length", None))
        self.trnGroup.setTitle(QCoreApplication.translate("ParusTrnWindow", u"Model Training Options", None))
        self.modNameLabel.setText(QCoreApplication.translate("ParusTrnWindow", u"Model Name", None))
        self.modNameLine.setPlaceholderText(QCoreApplication.translate("ParusTrnWindow", u"parus", None))
#if QT_CONFIG(tooltip)
        self.nEpLabel.setToolTip(QCoreApplication.translate("ParusTrnWindow", u"Total number of epoches for training", None))
#endif // QT_CONFIG(tooltip)
        self.nEpLabel.setText(QCoreApplication.translate("ParusTrnWindow", u"# Epochs", None))
#if QT_CONFIG(tooltip)
        self.nEpSpinbox.setToolTip(QCoreApplication.translate("ParusTrnWindow", u"Total number of epoches for training", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.stpEvalLabel.setToolTip(QCoreApplication.translate("ParusTrnWindow", u"Number of training steps between each model validation", None))
#endif // QT_CONFIG(tooltip)
        self.stpEvalLabel.setText(QCoreApplication.translate("ParusTrnWindow", u"# Steps per Evaluation", None))
#if QT_CONFIG(tooltip)
        self.stpEvalSpinbox.setToolTip(QCoreApplication.translate("ParusTrnWindow", u"Number of training steps between each model validation", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.indEvalLabel.setToolTip(QCoreApplication.translate("ParusTrnWindow", u"Number of training steps between each model validation", None))
#endif // QT_CONFIG(tooltip)
        self.indEvalLabel.setText(QCoreApplication.translate("ParusTrnWindow", u"Evaluation Indication", None))
        self.indEvalCombo.setItemText(0, QCoreApplication.translate("ParusTrnWindow", u"NONE", None))
        self.indEvalCombo.setItemText(1, QCoreApplication.translate("ParusTrnWindow", u"Display", None))
        self.indEvalCombo.setItemText(2, QCoreApplication.translate("ParusTrnWindow", u"Save Image", None))

        self.exGroup.setTitle(QCoreApplication.translate("ParusTrnWindow", u"Extra Options", None))
        self.exOptLine.setPlaceholderText(QCoreApplication.translate("ParusTrnWindow", u"Model training extra options, for advanced users only. Please refer to model training script manual for possible options.", None))
        self.trnProcButton.setText(QCoreApplication.translate("ParusTrnWindow", u"Initiate Model Training", None))
        self.tstConLabel.setText(QCoreApplication.translate("ParusTrnWindow", u"Model Testing Results", None))
        self.tstFileBox.setTitle(QCoreApplication.translate("ParusTrnWindow", u"Testing Results Selection", None))
        self.tstTypeBox.setItemText(0, QCoreApplication.translate("ParusTrnWindow", u"Optimum", None))
        self.tstTypeBox.setItemText(1, QCoreApplication.translate("ParusTrnWindow", u"Final", None))

#if QT_CONFIG(tooltip)
        self.tstTypeBox.setToolTip(QCoreApplication.translate("ParusTrnWindow", u"Select testing results model source", None))
#endif // QT_CONFIG(tooltip)
        self.tstPathLine.setPlaceholderText(QCoreApplication.translate("ParusTrnWindow", u"Select testing results folder", None))
        self.tstPathSelect.setText(QCoreApplication.translate("ParusTrnWindow", u"Open", None))
        self.tstViewButton.setText(QCoreApplication.translate("ParusTrnWindow", u"View Testing Results", None))
    # retranslateUi

