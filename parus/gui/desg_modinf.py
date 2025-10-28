# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'desg_modinf.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QAbstractItemView, QCheckBox, QComboBox, QFrame, QGridLayout, QGroupBox, QHBoxLayout,
                               QLabel, QLineEdit, QPushButton, QSizePolicy, QSpacerItem, QSpinBox, QStatusBar,
                               QTableWidget, QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget)


class Ui_ParusInfWindow(object):
    def setupUi(self, ParusInfWindow):
        if not ParusInfWindow.objectName():
            ParusInfWindow.setObjectName(u"ParusInfWindow")
        ParusInfWindow.resize(1168, 916)
        self.centralWidget = QWidget(ParusInfWindow)
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

        self.infFrame = QFrame(self.centralWidget)
        self.infFrame.setObjectName(u"infFrame")
        self.infFrame.setMinimumSize(QSize(1150, 560))
        self.infFrame.setFrameShape(QFrame.Shape.Box)
        self.infFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.infFrameLayout = QVBoxLayout(self.infFrame)
        self.infFrameLayout.setObjectName(u"infFrameLayout")
        self.infFrameLayout.setContentsMargins(-1, 0, -1, 5)
        self.infConLabel = QLabel(self.infFrame)
        self.infConLabel.setObjectName(u"infConLabel")
        self.infConLabel.setMinimumSize(QSize(1000, 28))
        self.infConLabel.setMaximumSize(QSize(16777215, 28))
        self.infConLabel.setFont(font)

        self.infFrameLayout.addWidget(self.infConLabel)

        self.inputGroup = QGroupBox(self.infFrame)
        self.inputGroup.setObjectName(u"inputGroup")
        self.inputGroup.setMinimumSize(QSize(1000, 350))
        font2 = QFont()
        font2.setPointSize(12)
        font2.setBold(True)
        self.inputGroup.setFont(font2)
        self.inputLayout = QVBoxLayout(self.inputGroup)
        self.inputLayout.setObjectName(u"inputLayout")
        self.inputTable = QTableWidget(self.inputGroup)
        if (self.inputTable.columnCount() < 3):
            self.inputTable.setColumnCount(3)
        font3 = QFont()
        font3.setPointSize(9)
        font3.setBold(True)
        __qtablewidgetitem = QTableWidgetItem()
        __qtablewidgetitem.setFont(font3);
        self.inputTable.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        __qtablewidgetitem1.setFont(font3);
        self.inputTable.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        __qtablewidgetitem2.setFont(font3);
        self.inputTable.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        self.inputTable.setObjectName(u"inputTable")
        self.inputTable.setMinimumSize(QSize(600, 200))
        font4 = QFont()
        font4.setPointSize(9)
        font4.setBold(False)
        self.inputTable.setFont(font4)
        self.inputTable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.inputTable.setAlternatingRowColors(True)
        self.inputTable.horizontalHeader().setStretchLastSection(True)

        self.inputLayout.addWidget(self.inputTable)

        self.selLayout = QHBoxLayout()
        self.selLayout.setSpacing(10)
        self.selLayout.setObjectName(u"selLayout")
        self.addFileButton = QPushButton(self.inputGroup)
        self.addFileButton.setObjectName(u"addFileButton")
        self.addFileButton.setMinimumSize(QSize(150, 25))
        self.addFileButton.setMaximumSize(QSize(150, 25))
        font5 = QFont()
        font5.setPointSize(10)
        font5.setBold(True)
        self.addFileButton.setFont(font5)

        self.selLayout.addWidget(self.addFileButton)

        self.addPathButton = QPushButton(self.inputGroup)
        self.addPathButton.setObjectName(u"addPathButton")
        self.addPathButton.setMinimumSize(QSize(150, 25))
        self.addPathButton.setMaximumSize(QSize(150, 25))
        self.addPathButton.setFont(font5)

        self.selLayout.addWidget(self.addPathButton)

        self.ctrlSelSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.selLayout.addItem(self.ctrlSelSpacer)

        self.selAllButton = QPushButton(self.inputGroup)
        self.selAllButton.setObjectName(u"selAllButton")
        self.selAllButton.setMinimumSize(QSize(120, 25))
        self.selAllButton.setMaximumSize(QSize(120, 25))
        font6 = QFont()
        font6.setPointSize(10)
        font6.setBold(False)
        self.selAllButton.setFont(font6)

        self.selLayout.addWidget(self.selAllButton)

        self.selNonButton = QPushButton(self.inputGroup)
        self.selNonButton.setObjectName(u"selNonButton")
        self.selNonButton.setMinimumSize(QSize(120, 25))
        self.selNonButton.setMaximumSize(QSize(120, 25))
        self.selNonButton.setFont(font6)

        self.selLayout.addWidget(self.selNonButton)

        self.selInvButton = QPushButton(self.inputGroup)
        self.selInvButton.setObjectName(u"selInvButton")
        self.selInvButton.setMinimumSize(QSize(120, 25))
        self.selInvButton.setMaximumSize(QSize(120, 25))
        self.selInvButton.setFont(font6)

        self.selLayout.addWidget(self.selInvButton)


        self.inputLayout.addLayout(self.selLayout)


        self.infFrameLayout.addWidget(self.inputGroup)

        self.ckptGroup = QGroupBox(self.infFrame)
        self.ckptGroup.setObjectName(u"ckptGroup")
        self.ckptGroup.setMinimumSize(QSize(1000, 70))
        self.ckptGroup.setMaximumSize(QSize(16777215, 70))
        self.ckptGroup.setFont(font2)
        self.ckptLayout = QHBoxLayout(self.ckptGroup)
        self.ckptLayout.setSpacing(20)
        self.ckptLayout.setObjectName(u"ckptLayout")
        self.ckptLine = QLineEdit(self.ckptGroup)
        self.ckptLine.setObjectName(u"ckptLine")
        self.ckptLine.setMinimumSize(QSize(350, 25))
        self.ckptLine.setMaximumSize(QSize(16777215, 25))
        self.ckptLine.setFont(font6)

        self.ckptLayout.addWidget(self.ckptLine)

        self.ckptButton = QPushButton(self.ckptGroup)
        self.ckptButton.setObjectName(u"ckptButton")
        self.ckptButton.setMinimumSize(QSize(150, 25))
        self.ckptButton.setMaximumSize(QSize(150, 25))
        self.ckptButton.setFont(font5)

        self.ckptLayout.addWidget(self.ckptButton)


        self.infFrameLayout.addWidget(self.ckptGroup)

        self.optGroup = QGroupBox(self.infFrame)
        self.optGroup.setObjectName(u"optGroup")
        self.optGroup.setMinimumSize(QSize(1000, 70))
        self.optGroup.setMaximumSize(QSize(16777215, 70))
        self.optGroup.setFont(font2)
        self.optGrpLayout = QHBoxLayout(self.optGroup)
        self.optGrpLayout.setObjectName(u"optGrpLayout")
        self.ovlpLayout = QHBoxLayout()
        self.ovlpLayout.setSpacing(0)
        self.ovlpLayout.setObjectName(u"ovlpLayout")
        self.ovlpLabel = QLabel(self.optGroup)
        self.ovlpLabel.setObjectName(u"ovlpLabel")
        self.ovlpLabel.setMinimumSize(QSize(105, 25))
        self.ovlpLabel.setMaximumSize(QSize(105, 25))
        self.ovlpLabel.setFont(font6)

        self.ovlpLayout.addWidget(self.ovlpLabel)

        self.ovlpSpinbox = QSpinBox(self.optGroup)
        self.ovlpSpinbox.setObjectName(u"ovlpSpinbox")
        self.ovlpSpinbox.setMinimumSize(QSize(80, 25))
        self.ovlpSpinbox.setMaximumSize(QSize(80, 25))
        self.ovlpSpinbox.setFont(font4)
        self.ovlpSpinbox.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.ovlpSpinbox.setMaximum(1000)
        self.ovlpSpinbox.setValue(10)

        self.ovlpLayout.addWidget(self.ovlpSpinbox)


        self.optGrpLayout.addLayout(self.ovlpLayout)

        self.optSpacerL = QSpacerItem(100, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.optGrpLayout.addItem(self.optSpacerL)

        self.tmemCheckbox = QCheckBox(self.optGroup)
        self.tmemCheckbox.setObjectName(u"tmemCheckbox")
        self.tmemCheckbox.setMinimumSize(QSize(115, 25))
        self.tmemCheckbox.setFont(font4)

        self.optGrpLayout.addWidget(self.tmemCheckbox)

        self.optSpacerM = QSpacerItem(100, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.optGrpLayout.addItem(self.optSpacerM)

        self.btszLayout = QHBoxLayout()
        self.btszLayout.setSpacing(0)
        self.btszLayout.setObjectName(u"btszLayout")
        self.btszLabel = QLabel(self.optGroup)
        self.btszLabel.setObjectName(u"btszLabel")
        self.btszLabel.setMinimumSize(QSize(65, 25))
        self.btszLabel.setMaximumSize(QSize(65, 25))
        self.btszLabel.setFont(font6)

        self.btszLayout.addWidget(self.btszLabel)

        self.btszSpinbox = QSpinBox(self.optGroup)
        self.btszSpinbox.setObjectName(u"btszSpinbox")
        self.btszSpinbox.setMinimumSize(QSize(100, 25))
        self.btszSpinbox.setMaximumSize(QSize(100, 25))
        self.btszSpinbox.setFont(font4)
        self.btszSpinbox.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.btszSpinbox.setMinimum(1)
        self.btszSpinbox.setMaximum(10000)
        self.btszSpinbox.setValue(2048)

        self.btszLayout.addWidget(self.btszSpinbox)


        self.optGrpLayout.addLayout(self.btszLayout)

        self.optSpacerR = QSpacerItem(100, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.optGrpLayout.addItem(self.optSpacerR)

        self.clvlLayout = QHBoxLayout()
        self.clvlLayout.setSpacing(0)
        self.clvlLayout.setObjectName(u"clvlLayout")
        self.clvlLabel = QLabel(self.optGroup)
        self.clvlLabel.setObjectName(u"clvlLabel")
        self.clvlLabel.setMinimumSize(QSize(120, 25))
        self.clvlLabel.setMaximumSize(QSize(120, 25))
        self.clvlLabel.setFont(font6)

        self.clvlLayout.addWidget(self.clvlLabel)

        self.clvlCombo = QComboBox(self.optGroup)
        self.clvlCombo.addItem("")
        self.clvlCombo.addItem("")
        self.clvlCombo.addItem("")
        self.clvlCombo.addItem("")
        self.clvlCombo.addItem("")
        self.clvlCombo.addItem("")
        self.clvlCombo.addItem("")
        self.clvlCombo.addItem("")
        self.clvlCombo.addItem("")
        self.clvlCombo.addItem("")
        self.clvlCombo.setObjectName(u"clvlCombo")
        self.clvlCombo.setMinimumSize(QSize(60, 25))
        self.clvlCombo.setMaximumSize(QSize(60, 25))
        self.clvlCombo.setFont(font4)

        self.clvlLayout.addWidget(self.clvlCombo)


        self.optGrpLayout.addLayout(self.clvlLayout)


        self.infFrameLayout.addWidget(self.optGroup)


        self.centralLayout.addWidget(self.infFrame)

        self.procButton = QPushButton(self.centralWidget)
        self.procButton.setObjectName(u"procButton")
        self.procButton.setMinimumSize(QSize(1150, 45))
        self.procButton.setMaximumSize(QSize(16777215, 45))
        self.procButton.setFont(font)

        self.centralLayout.addWidget(self.procButton)

        ParusInfWindow.setCentralWidget(self.centralWidget)
        self.statBar = QStatusBar(ParusInfWindow)
        self.statBar.setObjectName(u"statBar")
        ParusInfWindow.setStatusBar(self.statBar)

        self.retranslateUi(ParusInfWindow)

        self.clvlCombo.setCurrentIndex(4)


        QMetaObject.connectSlotsByName(ParusInfWindow)
    # setupUi

    def retranslateUi(self, ParusInfWindow):
        ParusInfWindow.setWindowTitle(QCoreApplication.translate("ParusInfWindow", u"Parus - Data Inference", None))
        self.procConLabel.setText(QCoreApplication.translate("ParusInfWindow", u"System Console", None))
        self.procConClear.setText(QCoreApplication.translate("ParusInfWindow", u"Clear", None))
        self.procConCopy.setText(QCoreApplication.translate("ParusInfWindow", u"Copy", None))
        self.procConScroll.setText(QCoreApplication.translate("ParusInfWindow", u"Auto Scroll", None))
        self.infConLabel.setText(QCoreApplication.translate("ParusInfWindow", u"Inference Settings", None))
        self.inputGroup.setTitle(QCoreApplication.translate("ParusInfWindow", u"Data File/Directory Selection", None))
        ___qtablewidgetitem = self.inputTable.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("ParusInfWindow", u"  Select  ", None));
        ___qtablewidgetitem1 = self.inputTable.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("ParusInfWindow", u"Type", None));
        ___qtablewidgetitem2 = self.inputTable.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("ParusInfWindow", u"Path", None));
        self.addFileButton.setText(QCoreApplication.translate("ParusInfWindow", u"Add File(s)", None))
        self.addPathButton.setText(QCoreApplication.translate("ParusInfWindow", u"Add Directory", None))
        self.selAllButton.setText(QCoreApplication.translate("ParusInfWindow", u"Select All", None))
        self.selNonButton.setText(QCoreApplication.translate("ParusInfWindow", u"Deselect All", None))
        self.selInvButton.setText(QCoreApplication.translate("ParusInfWindow", u"Invert Selection", None))
        self.ckptGroup.setTitle(QCoreApplication.translate("ParusInfWindow", u"Model Trained Weights", None))
        self.ckptLine.setPlaceholderText(QCoreApplication.translate("ParusInfWindow", u"Trained weight (*.ckpt) of model", None))
        self.ckptButton.setText(QCoreApplication.translate("ParusInfWindow", u"Select File", None))
        self.optGroup.setTitle(QCoreApplication.translate("ParusInfWindow", u"Process Options", None))
#if QT_CONFIG(tooltip)
        self.ovlpLabel.setToolTip(QCoreApplication.translate("ParusInfWindow", u"Overlapping size between each sample step\n"
"Increase value will capture features better at a cost of longer process time", None))
#endif // QT_CONFIG(tooltip)
        self.ovlpLabel.setText(QCoreApplication.translate("ParusInfWindow", u"Overlap Samples", None))
#if QT_CONFIG(tooltip)
        self.ovlpSpinbox.setToolTip(QCoreApplication.translate("ParusInfWindow", u"Overlapping size between each sample step\n"
"Increase value will capture features better at a cost of longer process time", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.tmemCheckbox.setToolTip(QCoreApplication.translate("ParusInfWindow", u"Load whole file to system memory\n"
"Enable this to accelerate process at risk of RAM overflow", None))
#endif // QT_CONFIG(tooltip)
        self.tmemCheckbox.setText(QCoreApplication.translate("ParusInfWindow", u"Load to Memory", None))
#if QT_CONFIG(tooltip)
        self.btszLabel.setToolTip(QCoreApplication.translate("ParusInfWindow", u"Processing batch size\n"
"Greater value will make process faster at a cost of larger VRAM usage", None))
#endif // QT_CONFIG(tooltip)
        self.btszLabel.setText(QCoreApplication.translate("ParusInfWindow", u"Batch Size", None))
#if QT_CONFIG(tooltip)
        self.btszSpinbox.setToolTip(QCoreApplication.translate("ParusInfWindow", u"Processing batch size\n"
"Greater value will make process faster at a cost of larger VRAM usage", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.clvlLabel.setToolTip(QCoreApplication.translate("ParusInfWindow", u"Output file compression level\n"
"Higher level make smaller file at a cost of longer compression time", None))
#endif // QT_CONFIG(tooltip)
        self.clvlLabel.setText(QCoreApplication.translate("ParusInfWindow", u"Compression Level", None))
        self.clvlCombo.setItemText(0, QCoreApplication.translate("ParusInfWindow", u"0", None))
        self.clvlCombo.setItemText(1, QCoreApplication.translate("ParusInfWindow", u"1", None))
        self.clvlCombo.setItemText(2, QCoreApplication.translate("ParusInfWindow", u"2", None))
        self.clvlCombo.setItemText(3, QCoreApplication.translate("ParusInfWindow", u"3", None))
        self.clvlCombo.setItemText(4, QCoreApplication.translate("ParusInfWindow", u"4", None))
        self.clvlCombo.setItemText(5, QCoreApplication.translate("ParusInfWindow", u"5", None))
        self.clvlCombo.setItemText(6, QCoreApplication.translate("ParusInfWindow", u"6", None))
        self.clvlCombo.setItemText(7, QCoreApplication.translate("ParusInfWindow", u"7", None))
        self.clvlCombo.setItemText(8, QCoreApplication.translate("ParusInfWindow", u"8", None))
        self.clvlCombo.setItemText(9, QCoreApplication.translate("ParusInfWindow", u"9", None))

#if QT_CONFIG(tooltip)
        self.clvlCombo.setToolTip(QCoreApplication.translate("ParusInfWindow", u"Output file compression level\n"
"Higher level make smaller file at a cost of longer compression time", None))
#endif // QT_CONFIG(tooltip)
        self.procButton.setText(QCoreApplication.translate("ParusInfWindow", u"Initiate Data Inference", None))
    # retranslateUi

