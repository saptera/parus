# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'desg_resver.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDoubleSpinBox, QFrame, QHBoxLayout, QLabel, QLineEdit,
                               QPushButton, QScrollBar, QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)


class Ui_ParusResWindow(object):
    def setupUi(self, ParusResWindow):
        if not ParusResWindow.objectName():
            ParusResWindow.setObjectName(u"ParusResWindow")
        ParusResWindow.resize(1018, 745)
        self.centralWidget = QWidget(ParusResWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.centralLayout = QVBoxLayout(self.centralWidget)
        self.centralLayout.setObjectName(u"centralLayout")
        self.signalFrame = QFrame(self.centralWidget)
        self.signalFrame.setObjectName(u"signalFrame")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.signalFrame.sizePolicy().hasHeightForWidth())
        self.signalFrame.setSizePolicy(sizePolicy)
        self.signalFrame.setMinimumSize(QSize(1000, 600))
        self.signalFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.signalFrame.setFrameShadow(QFrame.Shadow.Sunken)
        self.signalLayout = QVBoxLayout(self.signalFrame)
        self.signalLayout.setSpacing(2)
        self.signalLayout.setObjectName(u"signalLayout")
        self.signalLayout.setContentsMargins(4, 4, 4, 4)

        self.centralLayout.addWidget(self.signalFrame)

        self.pltctrlLayout = QHBoxLayout()
        self.pltctrlLayout.setObjectName(u"pltctrlLayout")
        self.fileLayout = QVBoxLayout()
        self.fileLayout.setSpacing(5)
        self.fileLayout.setObjectName(u"fileLayout")
        self.fileLabel = QLabel(self.centralWidget)
        self.fileLabel.setObjectName(u"fileLabel")

        self.fileLayout.addWidget(self.fileLabel)

        self.fileLine = QLineEdit(self.centralWidget)
        self.fileLine.setObjectName(u"fileLine")
        self.fileLine.setMinimumSize(QSize(200, 20))
        self.fileLine.setMaximumSize(QSize(16777215, 20))
        self.fileLine.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.fileLine.setReadOnly(True)

        self.fileLayout.addWidget(self.fileLine)


        self.pltctrlLayout.addLayout(self.fileLayout)

        self.pltCtrlSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.pltctrlLayout.addItem(self.pltCtrlSpacer)

        self.xrangeLayout = QVBoxLayout()
        self.xrangeLayout.setSpacing(5)
        self.xrangeLayout.setObjectName(u"xrangeLayout")
        self.xrangeLabel = QLabel(self.centralWidget)
        self.xrangeLabel.setObjectName(u"xrangeLabel")

        self.xrangeLayout.addWidget(self.xrangeLabel)

        self.xrangeSpinBox = QDoubleSpinBox(self.centralWidget)
        self.xrangeSpinBox.setObjectName(u"xrangeSpinBox")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.xrangeSpinBox.sizePolicy().hasHeightForWidth())
        self.xrangeSpinBox.setSizePolicy(sizePolicy1)
        self.xrangeSpinBox.setMinimumSize(QSize(100, 20))
        self.xrangeSpinBox.setMaximumSize(QSize(100, 20))
        self.xrangeSpinBox.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.xrangeSpinBox.setMinimum(0.500000000000000)
        self.xrangeSpinBox.setMaximum(10000.000000000000000)
        self.xrangeSpinBox.setValue(100.000000000000000)

        self.xrangeLayout.addWidget(self.xrangeSpinBox)


        self.pltctrlLayout.addLayout(self.xrangeLayout)

        self.yminLayout = QVBoxLayout()
        self.yminLayout.setSpacing(5)
        self.yminLayout.setObjectName(u"yminLayout")
        self.yminLabel = QLabel(self.centralWidget)
        self.yminLabel.setObjectName(u"yminLabel")

        self.yminLayout.addWidget(self.yminLabel)

        self.yminSpinBox = QDoubleSpinBox(self.centralWidget)
        self.yminSpinBox.setObjectName(u"yminSpinBox")
        sizePolicy1.setHeightForWidth(self.yminSpinBox.sizePolicy().hasHeightForWidth())
        self.yminSpinBox.setSizePolicy(sizePolicy1)
        self.yminSpinBox.setMinimumSize(QSize(100, 20))
        self.yminSpinBox.setMaximumSize(QSize(100, 20))
        self.yminSpinBox.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.yminSpinBox.setMinimum(-100000.000000000000000)
        self.yminSpinBox.setMaximum(0.000000000000000)
        self.yminSpinBox.setSingleStep(10.000000000000000)
        self.yminSpinBox.setValue(-500.000000000000000)

        self.yminLayout.addWidget(self.yminSpinBox)


        self.pltctrlLayout.addLayout(self.yminLayout)

        self.ymaxLayout = QVBoxLayout()
        self.ymaxLayout.setSpacing(5)
        self.ymaxLayout.setObjectName(u"ymaxLayout")
        self.ymaxLabel = QLabel(self.centralWidget)
        self.ymaxLabel.setObjectName(u"ymaxLabel")

        self.ymaxLayout.addWidget(self.ymaxLabel)

        self.ymaxSpinBox = QDoubleSpinBox(self.centralWidget)
        self.ymaxSpinBox.setObjectName(u"ymaxSpinBox")
        sizePolicy1.setHeightForWidth(self.ymaxSpinBox.sizePolicy().hasHeightForWidth())
        self.ymaxSpinBox.setSizePolicy(sizePolicy1)
        self.ymaxSpinBox.setMinimumSize(QSize(100, 20))
        self.ymaxSpinBox.setMaximumSize(QSize(100, 20))
        self.ymaxSpinBox.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.ymaxSpinBox.setMinimum(0.000000000000000)
        self.ymaxSpinBox.setMaximum(100000.000000000000000)
        self.ymaxSpinBox.setSingleStep(10.000000000000000)
        self.ymaxSpinBox.setValue(500.000000000000000)

        self.ymaxLayout.addWidget(self.ymaxSpinBox)


        self.pltctrlLayout.addLayout(self.ymaxLayout)

        self.actanoLayout = QVBoxLayout()
        self.actanoLayout.setSpacing(3)
        self.actanoLayout.setObjectName(u"actanoLayout")
        self.actanoLabel = QLabel(self.centralWidget)
        self.actanoLabel.setObjectName(u"actanoLabel")

        self.actanoLayout.addWidget(self.actanoLabel)

        self.actanoComboBox = QComboBox(self.centralWidget)
        self.actanoComboBox.addItem("")
        self.actanoComboBox.setObjectName(u"actanoComboBox")
        self.actanoComboBox.setMinimumSize(QSize(120, 22))
        self.actanoComboBox.setMaximumSize(QSize(120, 22))

        self.actanoLayout.addWidget(self.actanoComboBox)


        self.pltctrlLayout.addLayout(self.actanoLayout)

        self.lnkAnoBox = QCheckBox(self.centralWidget)
        self.lnkAnoBox.setObjectName(u"lnkAnoBox")
        sizePolicy1.setHeightForWidth(self.lnkAnoBox.sizePolicy().hasHeightForWidth())
        self.lnkAnoBox.setSizePolicy(sizePolicy1)
        self.lnkAnoBox.setMinimumSize(QSize(130, 30))
        self.lnkAnoBox.setMaximumSize(QSize(130, 30))
        font = QFont()
        font.setPointSize(10)
        font.setBold(False)
        self.lnkAnoBox.setFont(font)
        self.lnkAnoBox.setCheckable(True)
        self.lnkAnoBox.setChecked(True)

        self.pltctrlLayout.addWidget(self.lnkAnoBox)

        self.wfmselButton = QPushButton(self.centralWidget)
        self.wfmselButton.setObjectName(u"wfmselButton")
        self.wfmselButton.setMinimumSize(QSize(120, 30))
        self.wfmselButton.setMaximumSize(QSize(120, 30))
        font1 = QFont()
        font1.setPointSize(10)
        self.wfmselButton.setFont(font1)

        self.pltctrlLayout.addWidget(self.wfmselButton)


        self.centralLayout.addLayout(self.pltctrlLayout)

        self.navctrlLayout = QHBoxLayout()
        self.navctrlLayout.setSpacing(16)
        self.navctrlLayout.setObjectName(u"navctrlLayout")
        self.signalScrollBar = QScrollBar(self.centralWidget)
        self.signalScrollBar.setObjectName(u"signalScrollBar")
        self.signalScrollBar.setMinimumSize(QSize(0, 30))
        self.signalScrollBar.setMaximumSize(QSize(16777215, 30))
        self.signalScrollBar.setStyleSheet(u"QScrollBar:horizontal {\n"
"    border: 1px solid grey;\n"
"    background: #D3D3D3;\n"
"    height: 20px;\n"
"    margin: 0px 20px 0px 20px;\n"
"}\n"
"QScrollBar::handle:horizontal {\n"
"    background: #0078D7;\n"
"    min-width: 10px;\n"
"}\n"
"QScrollBar::handle:horizontal:hover {\n"
"    background: #73A5C6;\n"
"}\n"
"QScrollBar::handle:horizontal:pressed {\n"
"    background: #4169E1;\n"
"}\n"
"QScrollBar::handle:horizontal:disabled{\n"
"    background: #C0C0C0;\n"
"}\n"
"QScrollBar::add-line:horizontal {\n"
"    width: 20px;\n"
"    subcontrol-position: right;\n"
"    subcontrol-origin: margin;\n"
"}\n"
"QScrollBar::sub-line:horizontal {\n"
"    width: 20px;\n"
"    subcontrol-position: left;\n"
"    subcontrol-origin: margin;\n"
"}")
        self.signalScrollBar.setOrientation(Qt.Orientation.Horizontal)

        self.navctrlLayout.addWidget(self.signalScrollBar)

        self.toolbarBox = QCheckBox(self.centralWidget)
        self.toolbarBox.setObjectName(u"toolbarBox")
        sizePolicy1.setHeightForWidth(self.toolbarBox.sizePolicy().hasHeightForWidth())
        self.toolbarBox.setSizePolicy(sizePolicy1)
        self.toolbarBox.setMinimumSize(QSize(75, 30))
        self.toolbarBox.setMaximumSize(QSize(75, 30))
        font2 = QFont()
        font2.setPointSize(10)
        font2.setBold(True)
        self.toolbarBox.setFont(font2)

        self.navctrlLayout.addWidget(self.toolbarBox)


        self.centralLayout.addLayout(self.navctrlLayout)

        self.corExLayout = QHBoxLayout()
        self.corExLayout.setObjectName(u"corExLayout")
        self.cxDiscardButton = QPushButton(self.centralWidget)
        self.cxDiscardButton.setObjectName(u"cxDiscardButton")
        self.cxDiscardButton.setMinimumSize(QSize(120, 30))
        self.cxDiscardButton.setMaximumSize(QSize(120, 30))
        self.cxDiscardButton.setFont(font2)

        self.corExLayout.addWidget(self.cxDiscardButton)

        self.cxModeSpacerA = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.corExLayout.addItem(self.cxModeSpacerA)

        self.cxSaveButton = QPushButton(self.centralWidget)
        self.cxSaveButton.setObjectName(u"cxSaveButton")
        self.cxSaveButton.setMinimumSize(QSize(120, 30))
        self.cxSaveButton.setMaximumSize(QSize(120, 30))
        self.cxSaveButton.setFont(font2)

        self.corExLayout.addWidget(self.cxSaveButton)


        self.centralLayout.addLayout(self.corExLayout)

        ParusResWindow.setCentralWidget(self.centralWidget)
        QWidget.setTabOrder(self.actanoComboBox, self.xrangeSpinBox)
        QWidget.setTabOrder(self.xrangeSpinBox, self.yminSpinBox)
        QWidget.setTabOrder(self.yminSpinBox, self.ymaxSpinBox)
        QWidget.setTabOrder(self.ymaxSpinBox, self.lnkAnoBox)
        QWidget.setTabOrder(self.lnkAnoBox, self.wfmselButton)
        QWidget.setTabOrder(self.wfmselButton, self.toolbarBox)
        QWidget.setTabOrder(self.toolbarBox, self.cxDiscardButton)
        QWidget.setTabOrder(self.cxDiscardButton, self.cxSaveButton)

        self.retranslateUi(ParusResWindow)

        QMetaObject.connectSlotsByName(ParusResWindow)
    # setupUi

    def retranslateUi(self, ParusResWindow):
        ParusResWindow.setWindowTitle(QCoreApplication.translate("ParusResWindow", u"Parus - Signal Viewer", None))
        self.fileLabel.setText(QCoreApplication.translate("ParusResWindow", u"File", None))
#if QT_CONFIG(tooltip)
        self.fileLine.setToolTip(QCoreApplication.translate("ParusResWindow", u"File name of current plot", None))
#endif // QT_CONFIG(tooltip)
        self.xrangeLabel.setText(QCoreApplication.translate("ParusResWindow", u"Time Range", None))
#if QT_CONFIG(tooltip)
        self.xrangeSpinBox.setToolTip(QCoreApplication.translate("ParusResWindow", u"Set the time range of the plot", None))
#endif // QT_CONFIG(tooltip)
        self.xrangeSpinBox.setSuffix(QCoreApplication.translate("ParusResWindow", u" ms", None))
        self.yminLabel.setText(QCoreApplication.translate("ParusResWindow", u"Min Voltage", None))
#if QT_CONFIG(tooltip)
        self.yminSpinBox.setToolTip(QCoreApplication.translate("ParusResWindow", u"Set the relative scale of Y axes", None))
#endif // QT_CONFIG(tooltip)
        self.yminSpinBox.setSuffix(QCoreApplication.translate("ParusResWindow", u" mV", None))
        self.ymaxLabel.setText(QCoreApplication.translate("ParusResWindow", u"Max Voltage", None))
#if QT_CONFIG(tooltip)
        self.ymaxSpinBox.setToolTip(QCoreApplication.translate("ParusResWindow", u"Set the relative scale of Y axes", None))
#endif // QT_CONFIG(tooltip)
        self.ymaxSpinBox.setSuffix(QCoreApplication.translate("ParusResWindow", u" mV", None))
        self.actanoLabel.setText(QCoreApplication.translate("ParusResWindow", u"Active Annotation", None))
        self.actanoComboBox.setItemText(0, QCoreApplication.translate("ParusResWindow", u"NONE", None))

        self.lnkAnoBox.setText(QCoreApplication.translate("ParusResWindow", u"Linked Annotation", None))
#if QT_CONFIG(tooltip)
        self.wfmselButton.setToolTip(QCoreApplication.translate("ParusResWindow", u"Select displaying channel(s)", None))
#endif // QT_CONFIG(tooltip)
        self.wfmselButton.setText(QCoreApplication.translate("ParusResWindow", u"Select Waveforms", None))
        self.toolbarBox.setText(QCoreApplication.translate("ParusResWindow", u"Toolbar", None))
#if QT_CONFIG(tooltip)
        self.cxDiscardButton.setToolTip(QCoreApplication.translate("ParusResWindow", u"Select displaying channel(s)", None))
#endif // QT_CONFIG(tooltip)
        self.cxDiscardButton.setText(QCoreApplication.translate("ParusResWindow", u"Discard && Exit", None))
#if QT_CONFIG(tooltip)
        self.cxSaveButton.setToolTip(QCoreApplication.translate("ParusResWindow", u"Select displaying channel(s)", None))
#endif // QT_CONFIG(tooltip)
        self.cxSaveButton.setText(QCoreApplication.translate("ParusResWindow", u"Save", None))
    # retranslateUi

