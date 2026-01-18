# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'desg_spksrt.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QAbstractItemView, QComboBox, QDoubleSpinBox, QFrame, QGroupBox, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QScrollBar, QSizePolicy, QSlider, QSpacerItem, QSpinBox,
                               QStatusBar, QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)


class Ui_ParusSrtWindow(object):
    def setupUi(self, ParusSrtWindow):
        if not ParusSrtWindow.objectName():
            ParusSrtWindow.setObjectName(u"ParusSrtWindow")
        ParusSrtWindow.resize(1476, 977)
        self.centralWidget = QWidget(ParusSrtWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.centralLayout = QVBoxLayout(self.centralWidget)
        self.centralLayout.setObjectName(u"centralLayout")
        self.upperLayout = QHBoxLayout()
        self.upperLayout.setObjectName(u"upperLayout")
        self.ctrlLayout = QVBoxLayout()
        self.ctrlLayout.setObjectName(u"ctrlLayout")
        self.inputGroup = QGroupBox(self.centralWidget)
        self.inputGroup.setObjectName(u"inputGroup")
        self.inputGroup.setMinimumSize(QSize(800, 225))
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.inputGroup.setFont(font)
        self.inputLayout = QVBoxLayout(self.inputGroup)
        self.inputLayout.setObjectName(u"inputLayout")
        self.inputTable = QTableWidget(self.inputGroup)
        if (self.inputTable.columnCount() < 3):
            self.inputTable.setColumnCount(3)
        font1 = QFont()
        font1.setPointSize(9)
        font1.setBold(True)
        __qtablewidgetitem = QTableWidgetItem()
        __qtablewidgetitem.setFont(font1);
        self.inputTable.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        __qtablewidgetitem1.setFont(font1);
        self.inputTable.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        __qtablewidgetitem2.setFont(font1);
        self.inputTable.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        self.inputTable.setObjectName(u"inputTable")
        self.inputTable.setMinimumSize(QSize(600, 120))
        font2 = QFont()
        font2.setPointSize(9)
        font2.setBold(False)
        self.inputTable.setFont(font2)
        self.inputTable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.inputTable.setAlternatingRowColors(True)
        self.inputTable.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.inputTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.inputTable.horizontalHeader().setStretchLastSection(True)

        self.inputLayout.addWidget(self.inputTable)

        self.selLayout = QHBoxLayout()
        self.selLayout.setSpacing(10)
        self.selLayout.setObjectName(u"selLayout")
        self.addFileButton = QPushButton(self.inputGroup)
        self.addFileButton.setObjectName(u"addFileButton")
        self.addFileButton.setMinimumSize(QSize(150, 25))
        self.addFileButton.setMaximumSize(QSize(150, 25))
        font3 = QFont()
        font3.setPointSize(10)
        font3.setBold(True)
        self.addFileButton.setFont(font3)

        self.selLayout.addWidget(self.addFileButton)

        self.addPathButton = QPushButton(self.inputGroup)
        self.addPathButton.setObjectName(u"addPathButton")
        self.addPathButton.setMinimumSize(QSize(150, 25))
        self.addPathButton.setMaximumSize(QSize(150, 25))
        self.addPathButton.setFont(font3)

        self.selLayout.addWidget(self.addPathButton)

        self.ctrlSelSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.selLayout.addItem(self.ctrlSelSpacer)

        self.selAllButton = QPushButton(self.inputGroup)
        self.selAllButton.setObjectName(u"selAllButton")
        self.selAllButton.setMinimumSize(QSize(120, 25))
        self.selAllButton.setMaximumSize(QSize(120, 25))
        font4 = QFont()
        font4.setPointSize(10)
        font4.setBold(False)
        self.selAllButton.setFont(font4)

        self.selLayout.addWidget(self.selAllButton)

        self.selNonButton = QPushButton(self.inputGroup)
        self.selNonButton.setObjectName(u"selNonButton")
        self.selNonButton.setMinimumSize(QSize(120, 25))
        self.selNonButton.setMaximumSize(QSize(120, 25))
        self.selNonButton.setFont(font4)

        self.selLayout.addWidget(self.selNonButton)

        self.selInvButton = QPushButton(self.inputGroup)
        self.selInvButton.setObjectName(u"selInvButton")
        self.selInvButton.setMinimumSize(QSize(120, 25))
        self.selInvButton.setMaximumSize(QSize(120, 25))
        self.selInvButton.setFont(font4)

        self.selLayout.addWidget(self.selInvButton)


        self.inputLayout.addLayout(self.selLayout)


        self.ctrlLayout.addWidget(self.inputGroup)

        self.clusterGroup = QGroupBox(self.centralWidget)
        self.clusterGroup.setObjectName(u"clusterGroup")
        self.clusterGroup.setMinimumSize(QSize(800, 430))
        self.clusterGroup.setFont(font)
        self.clusterLayout = QVBoxLayout(self.clusterGroup)
        self.clusterLayout.setObjectName(u"clusterLayout")
        self.clsArgLayout = QHBoxLayout()
        self.clsArgLayout.setSpacing(12)
        self.clsArgLayout.setObjectName(u"clsArgLayout")
        self.argStatus = QLineEdit(self.clusterGroup)
        self.argStatus.setObjectName(u"argStatus")
        self.argStatus.setMinimumSize(QSize(25, 25))
        self.argStatus.setMaximumSize(QSize(25, 25))
        self.argStatus.setFont(font1)
        self.argStatus.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.argStatus.setStyleSheet(u"QLineEdit {background:#bcbd22; color:#000000}")
        self.argStatus.setFrame(False)
        self.argStatus.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.argStatus.setReadOnly(True)

        self.clsArgLayout.addWidget(self.argStatus)

        self.spkWfmLayout = QVBoxLayout()
        self.spkWfmLayout.setSpacing(4)
        self.spkWfmLayout.setObjectName(u"spkWfmLayout")
        self.spkWfmLabel = QLabel(self.clusterGroup)
        self.spkWfmLabel.setObjectName(u"spkWfmLabel")
        self.spkWfmLabel.setMinimumSize(QSize(70, 16))
        self.spkWfmLabel.setMaximumSize(QSize(16777215, 16))
        self.spkWfmLabel.setFont(font1)

        self.spkWfmLayout.addWidget(self.spkWfmLabel)

        self.spkWfmBox = QComboBox(self.clusterGroup)
        self.spkWfmBox.setObjectName(u"spkWfmBox")
        self.spkWfmBox.setMinimumSize(QSize(70, 25))
        self.spkWfmBox.setMaximumSize(QSize(70, 25))
        self.spkWfmBox.setFont(font2)

        self.spkWfmLayout.addWidget(self.spkWfmBox)


        self.clsArgLayout.addLayout(self.spkWfmLayout)

        self.clsMethLayout = QVBoxLayout()
        self.clsMethLayout.setSpacing(4)
        self.clsMethLayout.setObjectName(u"clsMethLayout")
        self.clsMethLabel = QLabel(self.clusterGroup)
        self.clsMethLabel.setObjectName(u"clsMethLabel")
        self.clsMethLabel.setMinimumSize(QSize(130, 16))
        self.clsMethLabel.setMaximumSize(QSize(16777215, 16))
        self.clsMethLabel.setFont(font1)

        self.clsMethLayout.addWidget(self.clsMethLabel)

        self.clsMethBox = QComboBox(self.clusterGroup)
        self.clsMethBox.addItem("")
        self.clsMethBox.addItem("")
        self.clsMethBox.addItem("")
        self.clsMethBox.setObjectName(u"clsMethBox")
        self.clsMethBox.setMinimumSize(QSize(135, 25))
        self.clsMethBox.setMaximumSize(QSize(16777215, 25))
        self.clsMethBox.setFont(font2)

        self.clsMethLayout.addWidget(self.clsMethBox)


        self.clsArgLayout.addLayout(self.clsMethLayout)

        self.detThLayout = QVBoxLayout()
        self.detThLayout.setSpacing(4)
        self.detThLayout.setObjectName(u"detThLayout")
        self.detThLabel = QLabel(self.clusterGroup)
        self.detThLabel.setObjectName(u"detThLabel")
        self.detThLabel.setMinimumSize(QSize(100, 16))
        self.detThLabel.setMaximumSize(QSize(16777215, 16))
        self.detThLabel.setFont(font1)

        self.detThLayout.addWidget(self.detThLabel)

        self.detThSpinbox = QSpinBox(self.clusterGroup)
        self.detThSpinbox.setObjectName(u"detThSpinbox")
        self.detThSpinbox.setMinimumSize(QSize(100, 25))
        self.detThSpinbox.setMaximumSize(QSize(100, 25))
        self.detThSpinbox.setFont(font2)
        self.detThSpinbox.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.detThSpinbox.setMinimum(-65536)
        self.detThSpinbox.setMaximum(65535)
        self.detThSpinbox.setValue(-50)

        self.detThLayout.addWidget(self.detThSpinbox)


        self.clsArgLayout.addLayout(self.detThLayout)

        self.kValLayout = QVBoxLayout()
        self.kValLayout.setSpacing(4)
        self.kValLayout.setObjectName(u"kValLayout")
        self.kValLabel = QLabel(self.clusterGroup)
        self.kValLabel.setObjectName(u"kValLabel")
        self.kValLabel.setMinimumSize(QSize(0, 16))
        self.kValLabel.setMaximumSize(QSize(16777215, 16))
        self.kValLabel.setFont(font1)

        self.kValLayout.addWidget(self.kValLabel)

        self.kDatLayout = QHBoxLayout()
        self.kDatLayout.setObjectName(u"kDatLayout")
        self.kValSlider = QSlider(self.clusterGroup)
        self.kValSlider.setObjectName(u"kValSlider")
        self.kValSlider.setMinimumSize(QSize(75, 20))
        self.kValSlider.setMaximumSize(QSize(16777215, 20))
        self.kValSlider.setMaximum(100)
        self.kValSlider.setValue(80)
        self.kValSlider.setOrientation(Qt.Orientation.Horizontal)

        self.kDatLayout.addWidget(self.kValSlider)

        self.kValSpinbox = QDoubleSpinBox(self.clusterGroup)
        self.kValSpinbox.setObjectName(u"kValSpinbox")
        self.kValSpinbox.setMinimumSize(QSize(60, 25))
        self.kValSpinbox.setMaximumSize(QSize(60, 25))
        self.kValSpinbox.setFont(font2)
        self.kValSpinbox.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.kValSpinbox.setMaximum(1.000000000000000)
        self.kValSpinbox.setSingleStep(0.010000000000000)
        self.kValSpinbox.setValue(0.800000000000000)

        self.kDatLayout.addWidget(self.kValSpinbox)


        self.kValLayout.addLayout(self.kDatLayout)


        self.clsArgLayout.addLayout(self.kValLayout)

        self.clsArgSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.clsArgLayout.addItem(self.clsArgSpacer)

        self.sampAntLayout = QVBoxLayout()
        self.sampAntLayout.setSpacing(4)
        self.sampAntLayout.setObjectName(u"sampAntLayout")
        self.sampAntLabel = QLabel(self.clusterGroup)
        self.sampAntLabel.setObjectName(u"sampAntLabel")
        self.sampAntLabel.setMinimumSize(QSize(0, 16))
        self.sampAntLabel.setMaximumSize(QSize(16777215, 16))
        self.sampAntLabel.setFont(font1)

        self.sampAntLayout.addWidget(self.sampAntLabel)

        self.sampAntSpinbox = QSpinBox(self.clusterGroup)
        self.sampAntSpinbox.setObjectName(u"sampAntSpinbox")
        self.sampAntSpinbox.setMinimumSize(QSize(60, 25))
        self.sampAntSpinbox.setMaximumSize(QSize(60, 25))
        self.sampAntSpinbox.setFont(font2)
        self.sampAntSpinbox.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.sampAntSpinbox.setMinimum(1)
        self.sampAntSpinbox.setMaximum(1000)
        self.sampAntSpinbox.setValue(5)

        self.sampAntLayout.addWidget(self.sampAntSpinbox)


        self.clsArgLayout.addLayout(self.sampAntLayout)

        self.sampPstLayout = QVBoxLayout()
        self.sampPstLayout.setSpacing(4)
        self.sampPstLayout.setObjectName(u"sampPstLayout")
        self.sampPstLabel = QLabel(self.clusterGroup)
        self.sampPstLabel.setObjectName(u"sampPstLabel")
        self.sampPstLabel.setMinimumSize(QSize(0, 16))
        self.sampPstLabel.setMaximumSize(QSize(16777215, 16))
        self.sampPstLabel.setFont(font1)

        self.sampPstLayout.addWidget(self.sampPstLabel)

        self.sampPstSpinbox = QSpinBox(self.clusterGroup)
        self.sampPstSpinbox.setObjectName(u"sampPstSpinbox")
        self.sampPstSpinbox.setMinimumSize(QSize(60, 25))
        self.sampPstSpinbox.setMaximumSize(QSize(60, 25))
        self.sampPstSpinbox.setFont(font2)
        self.sampPstSpinbox.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.sampPstSpinbox.setMinimum(1)
        self.sampPstSpinbox.setMaximum(1000)
        self.sampPstSpinbox.setValue(5)

        self.sampPstLayout.addWidget(self.sampPstSpinbox)


        self.clsArgLayout.addLayout(self.sampPstLayout)

        self.betaLayout = QVBoxLayout()
        self.betaLayout.setSpacing(4)
        self.betaLayout.setObjectName(u"betaLayout")
        self.betaLabel = QLabel(self.clusterGroup)
        self.betaLabel.setObjectName(u"betaLabel")
        self.betaLabel.setMinimumSize(QSize(0, 16))
        self.betaLabel.setMaximumSize(QSize(16777215, 16))
        self.betaLabel.setFont(font1)

        self.betaLayout.addWidget(self.betaLabel)

        self.betaSpinbox = QDoubleSpinBox(self.clusterGroup)
        self.betaSpinbox.setObjectName(u"betaSpinbox")
        self.betaSpinbox.setMinimumSize(QSize(60, 25))
        self.betaSpinbox.setMaximumSize(QSize(60, 25))
        self.betaSpinbox.setFont(font2)
        self.betaSpinbox.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.betaSpinbox.setMaximum(2.000000000000000)
        self.betaSpinbox.setValue(0.500000000000000)

        self.betaLayout.addWidget(self.betaSpinbox)


        self.clsArgLayout.addLayout(self.betaLayout)


        self.clusterLayout.addLayout(self.clsArgLayout)

        self.prbGrpLayout = QHBoxLayout()
        self.prbGrpLayout.setSpacing(12)
        self.prbGrpLayout.setObjectName(u"prbGrpLayout")
        self.prbGroup = QGroupBox(self.clusterGroup)
        self.prbGroup.setObjectName(u"prbGroup")
        self.prbGroup.setMinimumSize(QSize(500, 50))
        self.prbGroup.setMaximumSize(QSize(16777215, 50))
        self.prbGroup.setFont(font1)
        self.prbLayout = QHBoxLayout(self.prbGroup)
        self.prbLayout.setObjectName(u"prbLayout")
        self.prbLayout.setContentsMargins(2, 0, 2, 2)
        self.prbLine = QLineEdit(self.prbGroup)
        self.prbLine.setObjectName(u"prbLine")
        self.prbLine.setMinimumSize(QSize(300, 25))
        self.prbLine.setMaximumSize(QSize(16777215, 25))
        self.prbLine.setFont(font2)

        self.prbLayout.addWidget(self.prbLine)

        self.prbButton = QPushButton(self.prbGroup)
        self.prbButton.setObjectName(u"prbButton")
        self.prbButton.setMinimumSize(QSize(75, 25))
        self.prbButton.setMaximumSize(QSize(75, 25))
        self.prbButton.setFont(font1)

        self.prbLayout.addWidget(self.prbButton)

        self.prbViewButton = QPushButton(self.prbGroup)
        self.prbViewButton.setObjectName(u"prbViewButton")
        self.prbViewButton.setMinimumSize(QSize(75, 25))
        self.prbViewButton.setMaximumSize(QSize(75, 25))
        self.prbViewButton.setFont(font1)

        self.prbLayout.addWidget(self.prbViewButton)


        self.prbGrpLayout.addWidget(self.prbGroup)

        self.chsThLayout = QVBoxLayout()
        self.chsThLayout.setSpacing(4)
        self.chsThLayout.setObjectName(u"chsThLayout")
        self.chsThLabel = QLabel(self.clusterGroup)
        self.chsThLabel.setObjectName(u"chsThLabel")
        self.chsThLabel.setMinimumSize(QSize(100, 16))
        self.chsThLabel.setMaximumSize(QSize(16777215, 16))
        self.chsThLabel.setFont(font1)

        self.chsThLayout.addWidget(self.chsThLabel)

        self.chsThSpinbox = QSpinBox(self.clusterGroup)
        self.chsThSpinbox.setObjectName(u"chsThSpinbox")
        self.chsThSpinbox.setMinimumSize(QSize(100, 25))
        self.chsThSpinbox.setMaximumSize(QSize(100, 25))
        self.chsThSpinbox.setFont(font2)
        self.chsThSpinbox.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.chsThSpinbox.setMinimum(0)
        self.chsThSpinbox.setMaximum(65535)
        self.chsThSpinbox.setValue(60)

        self.chsThLayout.addWidget(self.chsThSpinbox)


        self.prbGrpLayout.addLayout(self.chsThLayout)

        self.chkRngLayout = QVBoxLayout()
        self.chkRngLayout.setSpacing(4)
        self.chkRngLayout.setObjectName(u"chkRngLayout")
        self.chkRngLabel = QLabel(self.clusterGroup)
        self.chkRngLabel.setObjectName(u"chkRngLabel")
        self.chkRngLabel.setMinimumSize(QSize(0, 16))
        self.chkRngLabel.setMaximumSize(QSize(16777215, 16))
        self.chkRngLabel.setFont(font1)

        self.chkRngLayout.addWidget(self.chkRngLabel)

        self.chkRngSpinbox = QSpinBox(self.clusterGroup)
        self.chkRngSpinbox.setObjectName(u"chkRngSpinbox")
        self.chkRngSpinbox.setMinimumSize(QSize(60, 25))
        self.chkRngSpinbox.setMaximumSize(QSize(60, 25))
        self.chkRngSpinbox.setFont(font2)
        self.chkRngSpinbox.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.chkRngSpinbox.setMinimum(1)
        self.chkRngSpinbox.setMaximum(20)
        self.chkRngSpinbox.setValue(5)

        self.chkRngLayout.addWidget(self.chkRngSpinbox)


        self.prbGrpLayout.addLayout(self.chkRngLayout)

        self.chkPctLayout = QVBoxLayout()
        self.chkPctLayout.setSpacing(4)
        self.chkPctLayout.setObjectName(u"chkPctLayout")
        self.chkPctLabel = QLabel(self.clusterGroup)
        self.chkPctLabel.setObjectName(u"chkPctLabel")
        self.chkPctLabel.setMinimumSize(QSize(0, 16))
        self.chkPctLabel.setMaximumSize(QSize(16777215, 16))
        self.chkPctLabel.setFont(font1)

        self.chkPctLayout.addWidget(self.chkPctLabel)

        self.chkPctSpinbox = QDoubleSpinBox(self.clusterGroup)
        self.chkPctSpinbox.setObjectName(u"chkPctSpinbox")
        self.chkPctSpinbox.setMinimumSize(QSize(60, 25))
        self.chkPctSpinbox.setMaximumSize(QSize(60, 25))
        self.chkPctSpinbox.setFont(font2)
        self.chkPctSpinbox.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.chkPctSpinbox.setMaximum(1.000000000000000)
        self.chkPctSpinbox.setValue(0.800000000000000)

        self.chkPctLayout.addWidget(self.chkPctSpinbox)


        self.prbGrpLayout.addLayout(self.chkPctLayout)


        self.clusterLayout.addLayout(self.prbGrpLayout)

        self.vldCtrlLayout = QHBoxLayout()
        self.vldCtrlLayout.setSpacing(12)
        self.vldCtrlLayout.setObjectName(u"vldCtrlLayout")
        self.actChnLayout = QHBoxLayout()
        self.actChnLayout.setSpacing(2)
        self.actChnLayout.setObjectName(u"actChnLayout")
        self.actChnLabel = QLabel(self.clusterGroup)
        self.actChnLabel.setObjectName(u"actChnLabel")
        self.actChnLabel.setMinimumSize(QSize(50, 25))
        self.actChnLabel.setMaximumSize(QSize(50, 25))
        self.actChnLabel.setFont(font1)

        self.actChnLayout.addWidget(self.actChnLabel)

        self.actChnBox = QComboBox(self.clusterGroup)
        self.actChnBox.setObjectName(u"actChnBox")
        self.actChnBox.setMinimumSize(QSize(80, 25))
        self.actChnBox.setMaximumSize(QSize(16777215, 25))
        self.actChnBox.setFont(font2)

        self.actChnLayout.addWidget(self.actChnBox)


        self.vldCtrlLayout.addLayout(self.actChnLayout)

        self.vldCtrlSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.vldCtrlLayout.addItem(self.vldCtrlSpacer)

        self.minCutLayout = QHBoxLayout()
        self.minCutLayout.setSpacing(2)
        self.minCutLayout.setObjectName(u"minCutLayout")
        self.minCutLabel = QLabel(self.clusterGroup)
        self.minCutLabel.setObjectName(u"minCutLabel")
        self.minCutLabel.setMinimumSize(QSize(50, 25))
        self.minCutLabel.setMaximumSize(QSize(50, 25))
        self.minCutLabel.setFont(font1)

        self.minCutLayout.addWidget(self.minCutLabel)

        self.minCutSpinbox = QSpinBox(self.clusterGroup)
        self.minCutSpinbox.setObjectName(u"minCutSpinbox")
        self.minCutSpinbox.setMinimumSize(QSize(60, 25))
        self.minCutSpinbox.setMaximumSize(QSize(60, 25))
        self.minCutSpinbox.setFont(font2)
        self.minCutSpinbox.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.minCutSpinbox.setMinimum(1)
        self.minCutSpinbox.setMaximum(100000)
        self.minCutSpinbox.setValue(50)

        self.minCutLayout.addWidget(self.minCutSpinbox)


        self.vldCtrlLayout.addLayout(self.minCutLayout)

        self.spkMrgButton = QPushButton(self.clusterGroup)
        self.spkMrgButton.setObjectName(u"spkMrgButton")
        self.spkMrgButton.setMinimumSize(QSize(200, 30))
        self.spkMrgButton.setMaximumSize(QSize(200, 30))
        self.spkMrgButton.setFont(font3)
        self.spkMrgButton.setStyleSheet(u"QPushButton {color: deepskyblue;}\n"
"QPushButton:disabled {color: dimgray;}")

        self.vldCtrlLayout.addWidget(self.spkMrgButton)


        self.clusterLayout.addLayout(self.vldCtrlLayout)

        self.spkCidTable = QTableWidget(self.clusterGroup)
        if (self.spkCidTable.columnCount() < 12):
            self.spkCidTable.setColumnCount(12)
        __qtablewidgetitem3 = QTableWidgetItem()
        __qtablewidgetitem3.setFont(font1);
        self.spkCidTable.setHorizontalHeaderItem(0, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        __qtablewidgetitem4.setFont(font1);
        self.spkCidTable.setHorizontalHeaderItem(1, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        __qtablewidgetitem5.setFont(font1);
        self.spkCidTable.setHorizontalHeaderItem(2, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        __qtablewidgetitem6.setFont(font1);
        self.spkCidTable.setHorizontalHeaderItem(3, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        __qtablewidgetitem7.setFont(font1);
        self.spkCidTable.setHorizontalHeaderItem(4, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        __qtablewidgetitem8.setFont(font1);
        self.spkCidTable.setHorizontalHeaderItem(5, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        __qtablewidgetitem9.setFont(font1);
        self.spkCidTable.setHorizontalHeaderItem(6, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        __qtablewidgetitem10.setFont(font1);
        self.spkCidTable.setHorizontalHeaderItem(7, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        __qtablewidgetitem11.setFont(font1);
        self.spkCidTable.setHorizontalHeaderItem(8, __qtablewidgetitem11)
        __qtablewidgetitem12 = QTableWidgetItem()
        __qtablewidgetitem12.setFont(font1);
        self.spkCidTable.setHorizontalHeaderItem(9, __qtablewidgetitem12)
        __qtablewidgetitem13 = QTableWidgetItem()
        __qtablewidgetitem13.setFont(font1);
        self.spkCidTable.setHorizontalHeaderItem(10, __qtablewidgetitem13)
        __qtablewidgetitem14 = QTableWidgetItem()
        __qtablewidgetitem14.setFont(font1);
        self.spkCidTable.setHorizontalHeaderItem(11, __qtablewidgetitem14)
        self.spkCidTable.setObjectName(u"spkCidTable")
        self.spkCidTable.setMinimumSize(QSize(0, 200))
        self.spkCidTable.setFont(font2)
        self.spkCidTable.setAlternatingRowColors(True)
        self.spkCidTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.spkCidTable.horizontalHeader().setDefaultSectionSize(60)
        self.spkCidTable.horizontalHeader().setStretchLastSection(True)

        self.clusterLayout.addWidget(self.spkCidTable)

        self.fileProcLayout = QHBoxLayout()
        self.fileProcLayout.setSpacing(12)
        self.fileProcLayout.setObjectName(u"fileProcLayout")
        self.actFileLayout = QHBoxLayout()
        self.actFileLayout.setSpacing(2)
        self.actFileLayout.setObjectName(u"actFileLayout")
        self.actFileLabel = QLabel(self.clusterGroup)
        self.actFileLabel.setObjectName(u"actFileLabel")
        self.actFileLabel.setMinimumSize(QSize(50, 25))
        self.actFileLabel.setMaximumSize(QSize(50, 25))
        self.actFileLabel.setFont(font1)

        self.actFileLayout.addWidget(self.actFileLabel)

        self.actFileBox = QComboBox(self.clusterGroup)
        self.actFileBox.addItem("")
        self.actFileBox.setObjectName(u"actFileBox")
        self.actFileBox.setMinimumSize(QSize(80, 25))
        self.actFileBox.setMaximumSize(QSize(16777215, 25))
        self.actFileBox.setFont(font2)

        self.actFileLayout.addWidget(self.actFileBox)


        self.fileProcLayout.addLayout(self.actFileLayout)

        self.actProcButton = QPushButton(self.clusterGroup)
        self.actProcButton.setObjectName(u"actProcButton")
        self.actProcButton.setMinimumSize(QSize(150, 30))
        self.actProcButton.setMaximumSize(QSize(150, 30))
        self.actProcButton.setFont(font3)

        self.fileProcLayout.addWidget(self.actProcButton)

        self.actSaveButton = QPushButton(self.clusterGroup)
        self.actSaveButton.setObjectName(u"actSaveButton")
        self.actSaveButton.setMinimumSize(QSize(150, 30))
        self.actSaveButton.setMaximumSize(QSize(150, 30))
        self.actSaveButton.setFont(font3)

        self.fileProcLayout.addWidget(self.actSaveButton)

        self.fileProcSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.fileProcLayout.addItem(self.fileProcSpacer)

        self.allPrsvButton = QPushButton(self.clusterGroup)
        self.allPrsvButton.setObjectName(u"allPrsvButton")
        self.allPrsvButton.setMinimumSize(QSize(225, 30))
        self.allPrsvButton.setMaximumSize(QSize(225, 30))
        self.allPrsvButton.setFont(font3)

        self.fileProcLayout.addWidget(self.allPrsvButton)


        self.clusterLayout.addLayout(self.fileProcLayout)


        self.ctrlLayout.addWidget(self.clusterGroup)

        self.ctrlLayout.setStretch(1, 1)

        self.upperLayout.addLayout(self.ctrlLayout)

        self.clsGrpLayout = QVBoxLayout()
        self.clsGrpLayout.setObjectName(u"clsGrpLayout")
        self.avgCorLayout = QVBoxLayout()
        self.avgCorLayout.setSpacing(2)
        self.avgCorLayout.setObjectName(u"avgCorLayout")
        self.avgCorLabel = QLabel(self.centralWidget)
        self.avgCorLabel.setObjectName(u"avgCorLabel")
        self.avgCorLabel.setFont(font3)
        self.avgCorLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.avgCorLayout.addWidget(self.avgCorLabel)

        self.avgCorTab = QTabWidget(self.centralWidget)
        self.avgCorTab.setObjectName(u"avgCorTab")

        self.avgCorLayout.addWidget(self.avgCorTab)


        self.clsGrpLayout.addLayout(self.avgCorLayout)

        self.grpFeatFrame = QFrame(self.centralWidget)
        self.grpFeatFrame.setObjectName(u"grpFeatFrame")
        self.grpFeatFrame.setMinimumSize(QSize(320, 300))
        self.grpFeatFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.grpFeatFrame.setFrameShadow(QFrame.Shadow.Sunken)
        self.grpFeatLayout = QVBoxLayout(self.grpFeatFrame)
        self.grpFeatLayout.setSpacing(0)
        self.grpFeatLayout.setObjectName(u"grpFeatLayout")
        self.grpFeatLayout.setContentsMargins(0, 0, 0, 0)

        self.clsGrpLayout.addWidget(self.grpFeatFrame)

        self.clsGrpLayout.setStretch(0, 1)
        self.clsGrpLayout.setStretch(1, 1)

        self.upperLayout.addLayout(self.clsGrpLayout)

        self.spkFeatFrame = QFrame(self.centralWidget)
        self.spkFeatFrame.setObjectName(u"spkFeatFrame")
        self.spkFeatFrame.setMinimumSize(QSize(320, 600))
        self.spkFeatFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.spkFeatFrame.setFrameShadow(QFrame.Shadow.Sunken)
        self.spkFeatLayout = QVBoxLayout(self.spkFeatFrame)
        self.spkFeatLayout.setSpacing(0)
        self.spkFeatLayout.setObjectName(u"spkFeatLayout")
        self.spkFeatLayout.setContentsMargins(0, 0, 0, 0)

        self.upperLayout.addWidget(self.spkFeatFrame)

        self.upperLayout.setStretch(1, 1)
        self.upperLayout.setStretch(2, 1)

        self.centralLayout.addLayout(self.upperLayout)

        self.spkAmpLayout = QVBoxLayout()
        self.spkAmpLayout.setSpacing(0)
        self.spkAmpLayout.setObjectName(u"spkAmpLayout")
        self.chnFeatFrame = QFrame(self.centralWidget)
        self.chnFeatFrame.setObjectName(u"chnFeatFrame")
        self.chnFeatFrame.setMinimumSize(QSize(1200, 240))
        self.chnFeatFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.chnFeatFrame.setFrameShadow(QFrame.Shadow.Sunken)
        self.chnFeatLayout = QVBoxLayout(self.chnFeatFrame)
        self.chnFeatLayout.setSpacing(0)
        self.chnFeatLayout.setObjectName(u"chnFeatLayout")
        self.chnFeatLayout.setContentsMargins(0, 0, 0, 0)

        self.spkAmpLayout.addWidget(self.chnFeatFrame)

        self.sigCtrlLayout = QHBoxLayout()
        self.sigCtrlLayout.setSpacing(27)
        self.sigCtrlLayout.setObjectName(u"sigCtrlLayout")
        self.signalScrollBar = QScrollBar(self.centralWidget)
        self.signalScrollBar.setObjectName(u"signalScrollBar")
        self.signalScrollBar.setMinimumSize(QSize(1200, 15))
        self.signalScrollBar.setMaximumSize(QSize(16777215, 15))
        self.signalScrollBar.setOrientation(Qt.Orientation.Horizontal)

        self.sigCtrlLayout.addWidget(self.signalScrollBar)

        self.sigTypButton = QPushButton(self.centralWidget)
        self.sigTypButton.setObjectName(u"sigTypButton")
        self.sigTypButton.setMinimumSize(QSize(75, 23))
        self.sigTypButton.setMaximumSize(QSize(75, 23))
        font5 = QFont()
        font5.setPointSize(8)
        self.sigTypButton.setFont(font5)

        self.sigCtrlLayout.addWidget(self.sigTypButton)


        self.spkAmpLayout.addLayout(self.sigCtrlLayout)


        self.centralLayout.addLayout(self.spkAmpLayout)

        ParusSrtWindow.setCentralWidget(self.centralWidget)
        self.statBar = QStatusBar(ParusSrtWindow)
        self.statBar.setObjectName(u"statBar")
        ParusSrtWindow.setStatusBar(self.statBar)

        self.retranslateUi(ParusSrtWindow)

        self.avgCorTab.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(ParusSrtWindow)
    # setupUi

    def retranslateUi(self, ParusSrtWindow):
        ParusSrtWindow.setWindowTitle(QCoreApplication.translate("ParusSrtWindow", u"Parus - Spike Sorting", None))
        self.inputGroup.setTitle(QCoreApplication.translate("ParusSrtWindow", u"Data File Selection", None))
        ___qtablewidgetitem = self.inputTable.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("ParusSrtWindow", u"  Select  ", None));
        ___qtablewidgetitem1 = self.inputTable.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("ParusSrtWindow", u"Type", None));
        ___qtablewidgetitem2 = self.inputTable.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("ParusSrtWindow", u"Path", None));
        self.addFileButton.setText(QCoreApplication.translate("ParusSrtWindow", u"Add File(s)", None))
        self.addPathButton.setText(QCoreApplication.translate("ParusSrtWindow", u"Add Directory", None))
        self.selAllButton.setText(QCoreApplication.translate("ParusSrtWindow", u"Select All", None))
        self.selNonButton.setText(QCoreApplication.translate("ParusSrtWindow", u"Deselect All", None))
        self.selInvButton.setText(QCoreApplication.translate("ParusSrtWindow", u"Invert Selection", None))
        self.clusterGroup.setTitle(QCoreApplication.translate("ParusSrtWindow", u"Clustering Control", None))
#if QT_CONFIG(tooltip)
        self.argStatus.setToolTip(QCoreApplication.translate("ParusSrtWindow", u"Clustering arguments definition status\n"
"Current: [Using Defaults]", None))
#endif // QT_CONFIG(tooltip)
        self.argStatus.setText(QCoreApplication.translate("ParusSrtWindow", u"U", None))
        self.spkWfmLabel.setText(QCoreApplication.translate("ParusSrtWindow", u"Waveform", None))
#if QT_CONFIG(tooltip)
        self.spkWfmBox.setToolTip(QCoreApplication.translate("ParusSrtWindow", u"Settings for this waveform\n"
"Each waveform can have unique settings", None))
#endif // QT_CONFIG(tooltip)
        self.clsMethLabel.setText(QCoreApplication.translate("ParusSrtWindow", u"Clustering Method", None))
        self.clsMethBox.setItemText(0, QCoreApplication.translate("ParusSrtWindow", u"Cosine-Amplitude", None))
        self.clsMethBox.setItemText(1, QCoreApplication.translate("ParusSrtWindow", u"Cosine-AmplitudeW", None))
        self.clsMethBox.setItemText(2, QCoreApplication.translate("ParusSrtWindow", u"Cross-Correlation", None))

#if QT_CONFIG(tooltip)
        self.clsMethBox.setToolTip(QCoreApplication.translate("ParusSrtWindow", u"[Cosine-Amplitude] Composite similarity of cosine and amplitude\n"
"[Cosine-AmplitudeW] Composite similarity of cosine and Gaussian weighted amplitude\n"
"[Cross-Correlation] Pearson correlation coefficient score", None))
#endif // QT_CONFIG(tooltip)
        self.detThLabel.setText(QCoreApplication.translate("ParusSrtWindow", u"Spike Threshold", None))
#if QT_CONFIG(tooltip)
        self.detThSpinbox.setToolTip(QCoreApplication.translate("ParusSrtWindow", u"Overlapping size between each sample step\n"
"Increase value will capture features better at a cost of longer process time", None))
#endif // QT_CONFIG(tooltip)
        self.detThSpinbox.setSuffix(QCoreApplication.translate("ParusSrtWindow", u" mV", None))
        self.kValLabel.setText(QCoreApplication.translate("ParusSrtWindow", u"K Value", None))
#if QT_CONFIG(tooltip)
        self.kValSlider.setToolTip(QCoreApplication.translate("ParusSrtWindow", u"Similarity score threshold between 0 to 1\n"
"Higher value resulting more conservative results", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.kValSpinbox.setToolTip(QCoreApplication.translate("ParusSrtWindow", u"Similarity score threshold between 0 to 1\n"
"Higher value resulting more conservative results", None))
#endif // QT_CONFIG(tooltip)
        self.sampAntLabel.setText(QCoreApplication.translate("ParusSrtWindow", u"Anterior", None))
#if QT_CONFIG(tooltip)
        self.sampAntSpinbox.setToolTip(QCoreApplication.translate("ParusSrtWindow", u"Number of samples before spike peak", None))
#endif // QT_CONFIG(tooltip)
        self.sampAntSpinbox.setSuffix(QCoreApplication.translate("ParusSrtWindow", u" pt", None))
        self.sampPstLabel.setText(QCoreApplication.translate("ParusSrtWindow", u"Posterior", None))
#if QT_CONFIG(tooltip)
        self.sampPstSpinbox.setToolTip(QCoreApplication.translate("ParusSrtWindow", u"Number of samples after spike peak", None))
#endif // QT_CONFIG(tooltip)
        self.sampPstSpinbox.setSuffix(QCoreApplication.translate("ParusSrtWindow", u" pt", None))
        self.betaLabel.setText(QCoreApplication.translate("ParusSrtWindow", u"Beta", None))
#if QT_CONFIG(tooltip)
        self.betaSpinbox.setToolTip(QCoreApplication.translate("ParusSrtWindow", u"Exponential weight for amplitude component", None))
#endif // QT_CONFIG(tooltip)
        self.prbGroup.setTitle(QCoreApplication.translate("ParusSrtWindow", u"Probe Geometry", None))
        self.prbLine.setPlaceholderText(QCoreApplication.translate("ParusSrtWindow", u"Probe geometry file (*.prb)", None))
        self.prbButton.setText(QCoreApplication.translate("ParusSrtWindow", u"Select", None))
        self.prbViewButton.setText(QCoreApplication.translate("ParusSrtWindow", u"View", None))
        self.chsThLabel.setText(QCoreApplication.translate("ParusSrtWindow", u"Max Distance", None))
#if QT_CONFIG(tooltip)
        self.chsThSpinbox.setToolTip(QCoreApplication.translate("ParusSrtWindow", u"Maximum distance between channels to record the same cell", None))
#endif // QT_CONFIG(tooltip)
        self.chsThSpinbox.setSuffix(QCoreApplication.translate("ParusSrtWindow", u" \u03bcm", None))
        self.chkRngLabel.setText(QCoreApplication.translate("ParusSrtWindow", u"Range", None))
#if QT_CONFIG(tooltip)
        self.chkRngSpinbox.setToolTip(QCoreApplication.translate("ParusSrtWindow", u"Allowed range for checking overlapping", None))
#endif // QT_CONFIG(tooltip)
        self.chkRngSpinbox.setSuffix(QCoreApplication.translate("ParusSrtWindow", u" pt", None))
        self.chkPctLabel.setText(QCoreApplication.translate("ParusSrtWindow", u"Ratio", None))
#if QT_CONFIG(tooltip)
        self.chkPctSpinbox.setToolTip(QCoreApplication.translate("ParusSrtWindow", u"Threshold rate of overlapping", None))
#endif // QT_CONFIG(tooltip)
        self.actChnLabel.setText(QCoreApplication.translate("ParusSrtWindow", u"Channel:", None))
        self.minCutLabel.setText(QCoreApplication.translate("ParusSrtWindow", u"Min Cut", None))
#if QT_CONFIG(tooltip)
        self.minCutSpinbox.setToolTip(QCoreApplication.translate("ParusSrtWindow", u"Minimum spike event in cluster required to save by default", None))
#endif // QT_CONFIG(tooltip)
        self.spkMrgButton.setText(QCoreApplication.translate("ParusSrtWindow", u"Merge Selected Cells", None))
        ___qtablewidgetitem3 = self.spkCidTable.horizontalHeaderItem(0)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("ParusSrtWindow", u"[S]", None));
#if QT_CONFIG(tooltip)
        ___qtablewidgetitem3.setToolTip(QCoreApplication.translate("ParusSrtWindow", u"Check this column to save cluster", None));
#endif // QT_CONFIG(tooltip)
        ___qtablewidgetitem4 = self.spkCidTable.horizontalHeaderItem(1)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("ParusSrtWindow", u"Cell", None));
        ___qtablewidgetitem5 = self.spkCidTable.horizontalHeaderItem(2)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("ParusSrtWindow", u"Count", None));
        ___qtablewidgetitem6 = self.spkCidTable.horizontalHeaderItem(3)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("ParusSrtWindow", u"[M]", None));
#if QT_CONFIG(tooltip)
        ___qtablewidgetitem6.setToolTip(QCoreApplication.translate("ParusSrtWindow", u"Check this column to merge clusters", None));
#endif // QT_CONFIG(tooltip)
        ___qtablewidgetitem7 = self.spkCidTable.horizontalHeaderItem(4)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("ParusSrtWindow", u"Amp", None));
        ___qtablewidgetitem8 = self.spkCidTable.horizontalHeaderItem(5)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("ParusSrtWindow", u"Frq", None));
        ___qtablewidgetitem9 = self.spkCidTable.horizontalHeaderItem(6)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("ParusSrtWindow", u"ISI", None));
        ___qtablewidgetitem10 = self.spkCidTable.horizontalHeaderItem(7)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("ParusSrtWindow", u"CV", None));
        ___qtablewidgetitem11 = self.spkCidTable.horizontalHeaderItem(8)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("ParusSrtWindow", u"CV2", None));
        ___qtablewidgetitem12 = self.spkCidTable.horizontalHeaderItem(9)
        ___qtablewidgetitem12.setText(QCoreApplication.translate("ParusSrtWindow", u"[C]", None));
#if QT_CONFIG(tooltip)
        ___qtablewidgetitem12.setToolTip(QCoreApplication.translate("ParusSrtWindow", u"Check this column to compare clusters (MAX = 2)", None));
#endif // QT_CONFIG(tooltip)
        ___qtablewidgetitem13 = self.spkCidTable.horizontalHeaderItem(10)
        ___qtablewidgetitem13.setText(QCoreApplication.translate("ParusSrtWindow", u"Colour", None));
        ___qtablewidgetitem14 = self.spkCidTable.horizontalHeaderItem(11)
        ___qtablewidgetitem14.setText(QCoreApplication.translate("ParusSrtWindow", u"Channel", None));
        self.actFileLabel.setText(QCoreApplication.translate("ParusSrtWindow", u"Act File:", None))
        self.actFileBox.setItemText(0, QCoreApplication.translate("ParusSrtWindow", u"NONE", None))

        self.actProcButton.setText(QCoreApplication.translate("ParusSrtWindow", u"Process Active File", None))
        self.actSaveButton.setText(QCoreApplication.translate("ParusSrtWindow", u"Save to Active File", None))
        self.allPrsvButton.setText(QCoreApplication.translate("ParusSrtWindow", u"Process && Save All Selected Files", None))
        self.avgCorLabel.setText(QCoreApplication.translate("ParusSrtWindow", u"Cluster Correlation Matrix", None))
        self.sigTypButton.setText(QCoreApplication.translate("ParusSrtWindow", u"Spike", None))
    # retranslateUi

