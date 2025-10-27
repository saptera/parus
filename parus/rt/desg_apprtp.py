# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'desg_apprtp.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QButtonGroup, QComboBox, QDoubleSpinBox, QFrame, QGroupBox, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QRadioButton, QSizePolicy, QSpacerItem, QSpinBox, QStatusBar,
                               QToolButton, QVBoxLayout, QWidget)


class Ui_ParusRtpWindow(object):
    def setupUi(self, ParusRtpWindow):
        if not ParusRtpWindow.objectName():
            ParusRtpWindow.setObjectName(u"ParusRtpWindow")
        ParusRtpWindow.resize(1200, 960)
        ParusRtpWindow.setMinimumSize(QSize(1200, 960))
        self.centralWidget = QWidget(ParusRtpWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.centralLayout = QHBoxLayout(self.centralWidget)
        self.centralLayout.setObjectName(u"centralLayout")
        self.ctrlLayout = QVBoxLayout()
        self.ctrlLayout.setObjectName(u"ctrlLayout")
        self.logoFrame = QFrame(self.centralWidget)
        self.logoFrame.setObjectName(u"logoFrame")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.logoFrame.sizePolicy().hasHeightForWidth())
        self.logoFrame.setSizePolicy(sizePolicy)
        self.logoFrame.setMinimumSize(QSize(230, 230))
        self.logoFrame.setMaximumSize(QSize(230, 230))
        self.logoFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.logoFrame.setFrameShadow(QFrame.Shadow.Plain)
        self.logoLayout = QVBoxLayout(self.logoFrame)
        self.logoLayout.setObjectName(u"logoLayout")

        self.ctrlLayout.addWidget(self.logoFrame)

        self.ctrlUpSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.ctrlLayout.addItem(self.ctrlUpSpacer)

        self.svrGroup = QGroupBox(self.centralWidget)
        self.svrGroup.setObjectName(u"svrGroup")
        self.svrGroup.setMinimumSize(QSize(125, 165))
        self.svrGroup.setMaximumSize(QSize(16777215, 165))
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.svrGroup.setFont(font)
        self.svrGroupLayout = QVBoxLayout(self.svrGroup)
        self.svrGroupLayout.setObjectName(u"svrGroupLayout")
        self.svrGroupLayout.setContentsMargins(6, 0, 6, 3)
        self.ipLayout = QVBoxLayout()
        self.ipLayout.setSpacing(0)
        self.ipLayout.setObjectName(u"ipLayout")
        self.ipLabel = QLabel(self.svrGroup)
        self.ipLabel.setObjectName(u"ipLabel")
        self.ipLabel.setMinimumSize(QSize(100, 16))
        self.ipLabel.setMaximumSize(QSize(16777215, 16))
        font1 = QFont()
        font1.setPointSize(9)
        font1.setBold(True)
        self.ipLabel.setFont(font1)

        self.ipLayout.addWidget(self.ipLabel)

        self.ipLine = QLineEdit(self.svrGroup)
        self.ipLine.setObjectName(u"ipLine")
        self.ipLine.setMinimumSize(QSize(100, 25))
        self.ipLine.setMaximumSize(QSize(16777215, 25))
        font2 = QFont()
        font2.setPointSize(9)
        font2.setBold(False)
        self.ipLine.setFont(font2)

        self.ipLayout.addWidget(self.ipLine)


        self.svrGroupLayout.addLayout(self.ipLayout)

        self.svrPortLayout = QHBoxLayout()
        self.svrPortLayout.setObjectName(u"svrPortLayout")
        self.portCmdLayout = QVBoxLayout()
        self.portCmdLayout.setSpacing(0)
        self.portCmdLayout.setObjectName(u"portCmdLayout")
        self.portCmdLabel = QLabel(self.svrGroup)
        self.portCmdLabel.setObjectName(u"portCmdLabel")
        self.portCmdLabel.setMinimumSize(QSize(100, 16))
        self.portCmdLabel.setMaximumSize(QSize(16777215, 16))
        self.portCmdLabel.setFont(font1)

        self.portCmdLayout.addWidget(self.portCmdLabel)

        self.portCmdSpinbox = QSpinBox(self.svrGroup)
        self.portCmdSpinbox.setObjectName(u"portCmdSpinbox")
        self.portCmdSpinbox.setMinimumSize(QSize(100, 25))
        self.portCmdSpinbox.setMaximumSize(QSize(16777215, 25))
        self.portCmdSpinbox.setFont(font2)
        self.portCmdSpinbox.setMaximum(65535)
        self.portCmdSpinbox.setValue(5000)

        self.portCmdLayout.addWidget(self.portCmdSpinbox)


        self.svrPortLayout.addLayout(self.portCmdLayout)

        self.portWfmLayout = QVBoxLayout()
        self.portWfmLayout.setSpacing(0)
        self.portWfmLayout.setObjectName(u"portWfmLayout")
        self.portWfmLabel = QLabel(self.svrGroup)
        self.portWfmLabel.setObjectName(u"portWfmLabel")
        self.portWfmLabel.setMinimumSize(QSize(100, 16))
        self.portWfmLabel.setMaximumSize(QSize(16777215, 16))
        self.portWfmLabel.setFont(font1)

        self.portWfmLayout.addWidget(self.portWfmLabel)

        self.portWfmSpinbox = QSpinBox(self.svrGroup)
        self.portWfmSpinbox.setObjectName(u"portWfmSpinbox")
        self.portWfmSpinbox.setMinimumSize(QSize(100, 25))
        self.portWfmSpinbox.setMaximumSize(QSize(16777215, 25))
        self.portWfmSpinbox.setFont(font2)
        self.portWfmSpinbox.setMaximum(65535)
        self.portWfmSpinbox.setValue(5001)

        self.portWfmLayout.addWidget(self.portWfmSpinbox)


        self.svrPortLayout.addLayout(self.portWfmLayout)


        self.svrGroupLayout.addLayout(self.svrPortLayout)

        self.svrConnectButton = QPushButton(self.svrGroup)
        self.svrConnectButton.setObjectName(u"svrConnectButton")
        self.svrConnectButton.setMinimumSize(QSize(100, 30))
        self.svrConnectButton.setMaximumSize(QSize(16777215, 30))

        self.svrGroupLayout.addWidget(self.svrConnectButton)


        self.ctrlLayout.addWidget(self.svrGroup)

        self.wfmGroup = QGroupBox(self.centralWidget)
        self.wfmGroup.setObjectName(u"wfmGroup")
        self.wfmGroup.setMinimumSize(QSize(125, 115))
        self.wfmGroup.setMaximumSize(QSize(16777215, 115))
        self.wfmGroup.setFont(font)
        self.wfmGroupLayout = QVBoxLayout(self.wfmGroup)
        self.wfmGroupLayout.setObjectName(u"wfmGroupLayout")
        self.wfmGroupLayout.setContentsMargins(6, 0, 6, 3)
        self.chStrLayout = QHBoxLayout()
        self.chStrLayout.setObjectName(u"chStrLayout")
        self.spiLayout = QVBoxLayout()
        self.spiLayout.setSpacing(0)
        self.spiLayout.setObjectName(u"spiLayout")
        self.spiLabel = QLabel(self.wfmGroup)
        self.spiLabel.setObjectName(u"spiLabel")
        self.spiLabel.setMinimumSize(QSize(100, 16))
        self.spiLabel.setMaximumSize(QSize(16777215, 16))
        self.spiLabel.setFont(font1)

        self.spiLayout.addWidget(self.spiLabel)

        self.spiCombo = QComboBox(self.wfmGroup)
        self.spiCombo.addItem("")
        self.spiCombo.addItem("")
        self.spiCombo.addItem("")
        self.spiCombo.addItem("")
        self.spiCombo.setObjectName(u"spiCombo")
        self.spiCombo.setMinimumSize(QSize(100, 25))
        self.spiCombo.setMaximumSize(QSize(16777215, 25))
        self.spiCombo.setFont(font2)

        self.spiLayout.addWidget(self.spiCombo)


        self.chStrLayout.addLayout(self.spiLayout)

        self.chLayout = QVBoxLayout()
        self.chLayout.setSpacing(0)
        self.chLayout.setObjectName(u"chLayout")
        self.chLabel = QLabel(self.wfmGroup)
        self.chLabel.setObjectName(u"chLabel")
        self.chLabel.setMinimumSize(QSize(100, 16))
        self.chLabel.setMaximumSize(QSize(16777215, 16))
        self.chLabel.setFont(font1)

        self.chLayout.addWidget(self.chLabel)

        self.chSpinbox = QSpinBox(self.wfmGroup)
        self.chSpinbox.setObjectName(u"chSpinbox")
        self.chSpinbox.setMinimumSize(QSize(100, 25))
        self.chSpinbox.setMaximumSize(QSize(16777215, 25))
        self.chSpinbox.setFont(font2)
        self.chSpinbox.setMaximum(127)
        self.chSpinbox.setValue(0)

        self.chLayout.addWidget(self.chSpinbox)


        self.chStrLayout.addLayout(self.chLayout)


        self.wfmGroupLayout.addLayout(self.chStrLayout)

        self.wfmSelectButton = QPushButton(self.wfmGroup)
        self.wfmSelectButton.setObjectName(u"wfmSelectButton")
        self.wfmSelectButton.setMinimumSize(QSize(100, 30))
        self.wfmSelectButton.setMaximumSize(QSize(16777215, 30))

        self.wfmGroupLayout.addWidget(self.wfmSelectButton)


        self.ctrlLayout.addWidget(self.wfmGroup)

        self.ctrlMiSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.ctrlLayout.addItem(self.ctrlMiSpacer)

        self.modGroup = QGroupBox(self.centralWidget)
        self.modGroup.setObjectName(u"modGroup")
        self.modGroup.setMinimumSize(QSize(125, 115))
        self.modGroup.setMaximumSize(QSize(16777215, 115))
        self.modGroup.setFont(font)
        self.modGroupLayout = QVBoxLayout(self.modGroup)
        self.modGroupLayout.setObjectName(u"modGroupLayout")
        self.modGroupLayout.setContentsMargins(6, 0, 6, 3)
        self.modelLayout = QVBoxLayout()
        self.modelLayout.setSpacing(0)
        self.modelLayout.setObjectName(u"modelLayout")
        self.modelLabel = QLabel(self.modGroup)
        self.modelLabel.setObjectName(u"modelLabel")
        self.modelLabel.setMinimumSize(QSize(100, 16))
        self.modelLabel.setMaximumSize(QSize(16777215, 16))
        self.modelLabel.setFont(font1)

        self.modelLayout.addWidget(self.modelLabel)

        self.ckptLayout = QHBoxLayout()
        self.ckptLayout.setObjectName(u"ckptLayout")
        self.modelPath = QLineEdit(self.modGroup)
        self.modelPath.setObjectName(u"modelPath")
        self.modelPath.setMinimumSize(QSize(100, 25))
        self.modelPath.setMaximumSize(QSize(16777215, 25))
        self.modelPath.setFont(font2)

        self.ckptLayout.addWidget(self.modelPath)

        self.modelSelect = QToolButton(self.modGroup)
        self.modelSelect.setObjectName(u"modelSelect")
        self.modelSelect.setMinimumSize(QSize(22, 22))
        self.modelSelect.setMaximumSize(QSize(22, 22))
        self.modelSelect.setFont(font1)

        self.ckptLayout.addWidget(self.modelSelect)


        self.modelLayout.addLayout(self.ckptLayout)


        self.modGroupLayout.addLayout(self.modelLayout)

        self.modLoadButton = QPushButton(self.modGroup)
        self.modLoadButton.setObjectName(u"modLoadButton")
        self.modLoadButton.setMinimumSize(QSize(100, 30))
        self.modLoadButton.setMaximumSize(QSize(16777215, 30))

        self.modGroupLayout.addWidget(self.modLoadButton)


        self.ctrlLayout.addWidget(self.modGroup)

        self.srtGroup = QGroupBox(self.centralWidget)
        self.srtGroup.setObjectName(u"srtGroup")
        self.srtGroup.setMinimumSize(QSize(125, 215))
        self.srtGroup.setMaximumSize(QSize(16777215, 215))
        self.srtGroup.setFont(font)
        self.srtGroupLayout = QVBoxLayout(self.srtGroup)
        self.srtGroupLayout.setObjectName(u"srtGroupLayout")
        self.srtGroupLayout.setContentsMargins(6, 0, 6, 3)
        self.srtWfmLayout = QVBoxLayout()
        self.srtWfmLayout.setSpacing(0)
        self.srtWfmLayout.setObjectName(u"srtWfmLayout")
        self.srtWfmLabel = QLabel(self.srtGroup)
        self.srtWfmLabel.setObjectName(u"srtWfmLabel")
        self.srtWfmLabel.setMinimumSize(QSize(100, 16))
        self.srtWfmLabel.setMaximumSize(QSize(16777215, 16))
        self.srtWfmLabel.setFont(font1)

        self.srtWfmLayout.addWidget(self.srtWfmLabel)

        self.srtWfmCombo = QComboBox(self.srtGroup)
        self.srtWfmCombo.setObjectName(u"srtWfmCombo")
        self.srtWfmCombo.setMinimumSize(QSize(100, 25))
        self.srtWfmCombo.setMaximumSize(QSize(16777215, 25))
        self.srtWfmCombo.setFont(font2)

        self.srtWfmLayout.addWidget(self.srtWfmCombo)


        self.srtGroupLayout.addLayout(self.srtWfmLayout)

        self.srtSmpLayout = QHBoxLayout()
        self.srtSmpLayout.setObjectName(u"srtSmpLayout")
        self.smpAntLayout = QVBoxLayout()
        self.smpAntLayout.setSpacing(0)
        self.smpAntLayout.setObjectName(u"smpAntLayout")
        self.smpAntLabel = QLabel(self.srtGroup)
        self.smpAntLabel.setObjectName(u"smpAntLabel")
        self.smpAntLabel.setMinimumSize(QSize(100, 16))
        self.smpAntLabel.setMaximumSize(QSize(16777215, 16))
        self.smpAntLabel.setFont(font1)

        self.smpAntLayout.addWidget(self.smpAntLabel)

        self.smpAntSpinbox = QSpinBox(self.srtGroup)
        self.smpAntSpinbox.setObjectName(u"smpAntSpinbox")
        self.smpAntSpinbox.setMinimumSize(QSize(100, 25))
        self.smpAntSpinbox.setMaximumSize(QSize(16777215, 25))
        self.smpAntSpinbox.setFont(font2)
        self.smpAntSpinbox.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.smpAntSpinbox.setMinimum(1)
        self.smpAntSpinbox.setMaximum(100)
        self.smpAntSpinbox.setValue(5)

        self.smpAntLayout.addWidget(self.smpAntSpinbox)


        self.srtSmpLayout.addLayout(self.smpAntLayout)

        self.smpPstLayout = QVBoxLayout()
        self.smpPstLayout.setSpacing(0)
        self.smpPstLayout.setObjectName(u"smpPstLayout")
        self.smpPstLabel = QLabel(self.srtGroup)
        self.smpPstLabel.setObjectName(u"smpPstLabel")
        self.smpPstLabel.setMinimumSize(QSize(100, 16))
        self.smpPstLabel.setMaximumSize(QSize(16777215, 16))
        self.smpPstLabel.setFont(font1)

        self.smpPstLayout.addWidget(self.smpPstLabel)

        self.smpPstSpinbox = QSpinBox(self.srtGroup)
        self.smpPstSpinbox.setObjectName(u"smpPstSpinbox")
        self.smpPstSpinbox.setMinimumSize(QSize(100, 25))
        self.smpPstSpinbox.setMaximumSize(QSize(16777215, 25))
        self.smpPstSpinbox.setFont(font2)
        self.smpPstSpinbox.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.smpPstSpinbox.setMinimum(1)
        self.smpPstSpinbox.setMaximum(100)
        self.smpPstSpinbox.setValue(5)

        self.smpPstLayout.addWidget(self.smpPstSpinbox)


        self.srtSmpLayout.addLayout(self.smpPstLayout)


        self.srtGroupLayout.addLayout(self.srtSmpLayout)

        self.srtSpkLayout = QHBoxLayout()
        self.srtSpkLayout.setObjectName(u"srtSpkLayout")
        self.spkThsLayout = QVBoxLayout()
        self.spkThsLayout.setSpacing(0)
        self.spkThsLayout.setObjectName(u"spkThsLayout")
        self.spkThsAntLabel = QLabel(self.srtGroup)
        self.spkThsAntLabel.setObjectName(u"spkThsAntLabel")
        self.spkThsAntLabel.setMinimumSize(QSize(100, 16))
        self.spkThsAntLabel.setMaximumSize(QSize(16777215, 16))
        self.spkThsAntLabel.setFont(font1)

        self.spkThsLayout.addWidget(self.spkThsAntLabel)

        self.spkThsSpinbox = QDoubleSpinBox(self.srtGroup)
        self.spkThsSpinbox.setObjectName(u"spkThsSpinbox")
        self.spkThsSpinbox.setMinimumSize(QSize(100, 25))
        self.spkThsSpinbox.setMaximumSize(QSize(16777215, 25))
        self.spkThsSpinbox.setFont(font2)
        self.spkThsSpinbox.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.spkThsSpinbox.setMinimum(-65535.000000000000000)
        self.spkThsSpinbox.setMaximum(0.000000000000000)
        self.spkThsSpinbox.setValue(-200.000000000000000)

        self.spkThsLayout.addWidget(self.spkThsSpinbox)


        self.srtSpkLayout.addLayout(self.spkThsLayout)

        self.spkKvlLayout = QVBoxLayout()
        self.spkKvlLayout.setSpacing(0)
        self.spkKvlLayout.setObjectName(u"spkKvlLayout")
        self.spkKvlLabel = QLabel(self.srtGroup)
        self.spkKvlLabel.setObjectName(u"spkKvlLabel")
        self.spkKvlLabel.setMinimumSize(QSize(100, 16))
        self.spkKvlLabel.setMaximumSize(QSize(16777215, 16))
        self.spkKvlLabel.setFont(font1)

        self.spkKvlLayout.addWidget(self.spkKvlLabel)

        self.spkKvlSpinbox = QDoubleSpinBox(self.srtGroup)
        self.spkKvlSpinbox.setObjectName(u"spkKvlSpinbox")
        self.spkKvlSpinbox.setMinimumSize(QSize(100, 25))
        self.spkKvlSpinbox.setMaximumSize(QSize(16777215, 25))
        self.spkKvlSpinbox.setFont(font2)
        self.spkKvlSpinbox.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.spkKvlSpinbox.setMaximum(1.000000000000000)
        self.spkKvlSpinbox.setSingleStep(0.100000000000000)
        self.spkKvlSpinbox.setValue(0.600000000000000)

        self.spkKvlLayout.addWidget(self.spkKvlSpinbox)


        self.srtSpkLayout.addLayout(self.spkKvlLayout)


        self.srtGroupLayout.addLayout(self.srtSpkLayout)

        self.srtAttachButton = QPushButton(self.srtGroup)
        self.srtAttachButton.setObjectName(u"srtAttachButton")
        self.srtAttachButton.setMinimumSize(QSize(100, 30))
        self.srtAttachButton.setMaximumSize(QSize(16777215, 30))

        self.srtGroupLayout.addWidget(self.srtAttachButton)


        self.ctrlLayout.addWidget(self.srtGroup)

        self.ctrlLoSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.ctrlLayout.addItem(self.ctrlLoSpacer)

        self.initProcButton = QPushButton(self.centralWidget)
        self.initProcButton.setObjectName(u"initProcButton")
        self.initProcButton.setMinimumSize(QSize(100, 30))
        self.initProcButton.setMaximumSize(QSize(16777215, 30))
        font3 = QFont()
        font3.setPointSize(12)
        font3.setBold(True)
        self.initProcButton.setFont(font3)

        self.ctrlLayout.addWidget(self.initProcButton)


        self.centralLayout.addLayout(self.ctrlLayout)

        self.pltLayout = QVBoxLayout()
        self.pltLayout.setObjectName(u"pltLayout")
        self.rawFrame = QFrame(self.centralWidget)
        self.rawFrame.setObjectName(u"rawFrame")
        self.rawFrame.setMinimumSize(QSize(800, 300))
        self.rawFrame.setFrameShape(QFrame.Shape.Box)
        self.rawFrame.setFrameShadow(QFrame.Shadow.Sunken)
        self.rawFrameLayout = QVBoxLayout(self.rawFrame)
        self.rawFrameLayout.setSpacing(0)
        self.rawFrameLayout.setObjectName(u"rawFrameLayout")
        self.rawFrameLayout.setContentsMargins(0, 0, 0, 0)

        self.pltLayout.addWidget(self.rawFrame)

        self.spkFrame = QFrame(self.centralWidget)
        self.spkFrame.setObjectName(u"spkFrame")
        self.spkFrame.setMinimumSize(QSize(800, 300))
        self.spkFrame.setFrameShape(QFrame.Shape.Box)
        self.spkFrame.setFrameShadow(QFrame.Shadow.Sunken)
        self.spkFrameLayout = QVBoxLayout(self.spkFrame)
        self.spkFrameLayout.setSpacing(0)
        self.spkFrameLayout.setObjectName(u"spkFrameLayout")
        self.spkFrameLayout.setContentsMargins(0, 0, 0, 0)

        self.pltLayout.addWidget(self.spkFrame)

        self.pltCtrlLayout = QHBoxLayout()
        self.pltCtrlLayout.setObjectName(u"pltCtrlLayout")
        self.pltLSpacer = QSpacerItem(80, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.pltCtrlLayout.addItem(self.pltLSpacer)

        self.yMinLayout = QVBoxLayout()
        self.yMinLayout.setSpacing(0)
        self.yMinLayout.setObjectName(u"yMinLayout")
        self.yMinLabel = QLabel(self.centralWidget)
        self.yMinLabel.setObjectName(u"yMinLabel")
        self.yMinLabel.setMinimumSize(QSize(100, 16))
        self.yMinLabel.setMaximumSize(QSize(16777215, 16))
        self.yMinLabel.setFont(font1)

        self.yMinLayout.addWidget(self.yMinLabel)

        self.yMinSpinbox = QDoubleSpinBox(self.centralWidget)
        self.yMinSpinbox.setObjectName(u"yMinSpinbox")
        self.yMinSpinbox.setMinimumSize(QSize(100, 25))
        self.yMinSpinbox.setMaximumSize(QSize(16777215, 25))
        self.yMinSpinbox.setFont(font2)
        self.yMinSpinbox.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.yMinSpinbox.setMinimum(-1000000.000000000000000)
        self.yMinSpinbox.setMaximum(0.000000000000000)
        self.yMinSpinbox.setValue(-1000.000000000000000)

        self.yMinLayout.addWidget(self.yMinSpinbox)


        self.pltCtrlLayout.addLayout(self.yMinLayout)

        self.yMaxLayout = QVBoxLayout()
        self.yMaxLayout.setSpacing(0)
        self.yMaxLayout.setObjectName(u"yMaxLayout")
        self.yMaxLabel = QLabel(self.centralWidget)
        self.yMaxLabel.setObjectName(u"yMaxLabel")
        self.yMaxLabel.setMinimumSize(QSize(100, 16))
        self.yMaxLabel.setMaximumSize(QSize(16777215, 16))
        self.yMaxLabel.setFont(font1)

        self.yMaxLayout.addWidget(self.yMaxLabel)

        self.yMaxSpinbox = QDoubleSpinBox(self.centralWidget)
        self.yMaxSpinbox.setObjectName(u"yMaxSpinbox")
        self.yMaxSpinbox.setMinimumSize(QSize(100, 25))
        self.yMaxSpinbox.setMaximumSize(QSize(16777215, 25))
        self.yMaxSpinbox.setFont(font2)
        self.yMaxSpinbox.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.yMaxSpinbox.setMinimum(0.000000000000000)
        self.yMaxSpinbox.setMaximum(1000000.000000000000000)
        self.yMaxSpinbox.setValue(500.000000000000000)

        self.yMaxLayout.addWidget(self.yMaxSpinbox)


        self.pltCtrlLayout.addLayout(self.yMaxLayout)

        self.ampButtonLayout = QVBoxLayout()
        self.ampButtonLayout.setSpacing(0)
        self.ampButtonLayout.setObjectName(u"ampButtonLayout")
        self.autoAmpButton = QRadioButton(self.centralWidget)
        self.ampButtonGroup = QButtonGroup(ParusRtpWindow)
        self.ampButtonGroup.setObjectName(u"ampButtonGroup")
        self.ampButtonGroup.addButton(self.autoAmpButton)
        self.autoAmpButton.setObjectName(u"autoAmpButton")
        self.autoAmpButton.setMinimumSize(QSize(110, 20))
        self.autoAmpButton.setMaximumSize(QSize(110, 20))
        self.autoAmpButton.setChecked(True)

        self.ampButtonLayout.addWidget(self.autoAmpButton)

        self.setAmpButton = QRadioButton(self.centralWidget)
        self.ampButtonGroup.addButton(self.setAmpButton)
        self.setAmpButton.setObjectName(u"setAmpButton")
        self.setAmpButton.setMinimumSize(QSize(110, 20))
        self.setAmpButton.setMaximumSize(QSize(110, 20))

        self.ampButtonLayout.addWidget(self.setAmpButton)


        self.pltCtrlLayout.addLayout(self.ampButtonLayout)

        self.pltRSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.pltCtrlLayout.addItem(self.pltRSpacer)

        self.xRngLayout = QVBoxLayout()
        self.xRngLayout.setSpacing(0)
        self.xRngLayout.setObjectName(u"xRngLayout")
        self.xRngLabel = QLabel(self.centralWidget)
        self.xRngLabel.setObjectName(u"xRngLabel")
        self.xRngLabel.setMinimumSize(QSize(100, 16))
        self.xRngLabel.setMaximumSize(QSize(16777215, 16))
        self.xRngLabel.setFont(font1)

        self.xRngLayout.addWidget(self.xRngLabel)

        self.xRngSpinbox = QDoubleSpinBox(self.centralWidget)
        self.xRngSpinbox.setObjectName(u"xRngSpinbox")
        self.xRngSpinbox.setMinimumSize(QSize(100, 25))
        self.xRngSpinbox.setMaximumSize(QSize(16777215, 25))
        self.xRngSpinbox.setFont(font2)
        self.xRngSpinbox.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.xRngSpinbox.setMinimum(100.000000000000000)
        self.xRngSpinbox.setMaximum(10000.000000000000000)
        self.xRngSpinbox.setValue(2000.000000000000000)

        self.xRngLayout.addWidget(self.xRngSpinbox)


        self.pltCtrlLayout.addLayout(self.xRngLayout)

        self.setRngButton = QPushButton(self.centralWidget)
        self.setRngButton.setObjectName(u"setRngButton")
        self.setRngButton.setMinimumSize(QSize(100, 30))
        self.setRngButton.setMaximumSize(QSize(16777215, 30))
        self.setRngButton.setFont(font)

        self.pltCtrlLayout.addWidget(self.setRngButton)

        self.pltCtrlLayout.setStretch(0, 1)

        self.pltLayout.addLayout(self.pltCtrlLayout)

        self.pltLayout.setStretch(0, 1)
        self.pltLayout.setStretch(1, 1)

        self.centralLayout.addLayout(self.pltLayout)

        self.centralLayout.setStretch(1, 1)
        ParusRtpWindow.setCentralWidget(self.centralWidget)
        self.statBar = QStatusBar(ParusRtpWindow)
        self.statBar.setObjectName(u"statBar")
        ParusRtpWindow.setStatusBar(self.statBar)

        self.retranslateUi(ParusRtpWindow)

        QMetaObject.connectSlotsByName(ParusRtpWindow)
    # setupUi

    def retranslateUi(self, ParusRtpWindow):
        ParusRtpWindow.setWindowTitle(QCoreApplication.translate("ParusRtpWindow", u"Parus - Realtime Spike Sorting", None))
        self.svrGroup.setTitle(QCoreApplication.translate("ParusRtpWindow", u"TCP Server", None))
        self.ipLabel.setText(QCoreApplication.translate("ParusRtpWindow", u"Server IP", None))
        self.ipLine.setPlaceholderText(QCoreApplication.translate("ParusRtpWindow", u"localhost", None))
        self.portCmdLabel.setText(QCoreApplication.translate("ParusRtpWindow", u"Command Port", None))
        self.portWfmLabel.setText(QCoreApplication.translate("ParusRtpWindow", u"Waveform Port", None))
        self.svrConnectButton.setText(QCoreApplication.translate("ParusRtpWindow", u"Connect", None))
        self.wfmGroup.setTitle(QCoreApplication.translate("ParusRtpWindow", u"Active Waveform", None))
        self.spiLabel.setText(QCoreApplication.translate("ParusRtpWindow", u"SPI Port", None))
        self.spiCombo.setItemText(0, QCoreApplication.translate("ParusRtpWindow", u"A", None))
        self.spiCombo.setItemText(1, QCoreApplication.translate("ParusRtpWindow", u"B", None))
        self.spiCombo.setItemText(2, QCoreApplication.translate("ParusRtpWindow", u"C", None))
        self.spiCombo.setItemText(3, QCoreApplication.translate("ParusRtpWindow", u"D", None))

        self.chLabel.setText(QCoreApplication.translate("ParusRtpWindow", u"Channel Number", None))
#if QT_CONFIG(tooltip)
        self.wfmSelectButton.setToolTip(QCoreApplication.translate("ParusRtpWindow", u"Connect to server first to enable channel selection", None))
#endif // QT_CONFIG(tooltip)
        self.wfmSelectButton.setText(QCoreApplication.translate("ParusRtpWindow", u"Select", None))
        self.modGroup.setTitle(QCoreApplication.translate("ParusRtpWindow", u"Model Definition", None))
        self.modelLabel.setText(QCoreApplication.translate("ParusRtpWindow", u"Model", None))
        self.modelPath.setPlaceholderText(QCoreApplication.translate("ParusRtpWindow", u"model (*.ckpt)", None))
        self.modelSelect.setText(QCoreApplication.translate("ParusRtpWindow", u"...", None))
        self.modLoadButton.setText(QCoreApplication.translate("ParusRtpWindow", u"Load", None))
        self.srtGroup.setTitle(QCoreApplication.translate("ParusRtpWindow", u"Spike Sorter", None))
        self.srtWfmLabel.setText(QCoreApplication.translate("ParusRtpWindow", u"Spike Waveform", None))
        self.smpAntLabel.setText(QCoreApplication.translate("ParusRtpWindow", u"Anterior Sample", None))
        self.smpAntSpinbox.setSuffix(QCoreApplication.translate("ParusRtpWindow", u" pt", None))
        self.smpPstLabel.setText(QCoreApplication.translate("ParusRtpWindow", u"Posterior Sample", None))
        self.smpPstSpinbox.setSuffix(QCoreApplication.translate("ParusRtpWindow", u" pt", None))
        self.spkThsAntLabel.setText(QCoreApplication.translate("ParusRtpWindow", u"Threshold", None))
        self.spkThsSpinbox.setSuffix(QCoreApplication.translate("ParusRtpWindow", u" \u03bcV", None))
        self.spkKvlLabel.setText(QCoreApplication.translate("ParusRtpWindow", u"K Value", None))
#if QT_CONFIG(tooltip)
        self.srtAttachButton.setToolTip(QCoreApplication.translate("ParusRtpWindow", u"Start data process to attach spike sorter", None))
#endif // QT_CONFIG(tooltip)
        self.srtAttachButton.setText(QCoreApplication.translate("ParusRtpWindow", u"Attach", None))
#if QT_CONFIG(tooltip)
        self.initProcButton.setToolTip(QCoreApplication.translate("ParusRtpWindow", u"Data streaming required for data process\n"
"Model need to be loaded for data process", None))
#endif // QT_CONFIG(tooltip)
        self.initProcButton.setText(QCoreApplication.translate("ParusRtpWindow", u"Process", None))
        self.yMinLabel.setText(QCoreApplication.translate("ParusRtpWindow", u"Min Amplitude", None))
        self.yMinSpinbox.setSuffix(QCoreApplication.translate("ParusRtpWindow", u" \u03bcV", None))
        self.yMaxLabel.setText(QCoreApplication.translate("ParusRtpWindow", u"Max Amplitude", None))
        self.yMaxSpinbox.setSuffix(QCoreApplication.translate("ParusRtpWindow", u" \u03bcV", None))
        self.autoAmpButton.setText(QCoreApplication.translate("ParusRtpWindow", u"Auto Amplitude", None))
        self.setAmpButton.setText(QCoreApplication.translate("ParusRtpWindow", u"Set Amplitude", None))
        self.xRngLabel.setText(QCoreApplication.translate("ParusRtpWindow", u"Time Range", None))
        self.xRngSpinbox.setSuffix(QCoreApplication.translate("ParusRtpWindow", u" ms", None))
        self.setRngButton.setText(QCoreApplication.translate("ParusRtpWindow", u"Set Time", None))
    # retranslateUi

