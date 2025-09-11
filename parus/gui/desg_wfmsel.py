# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'desg_wfmsel.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize
from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QWidget


class Ui_WfmSelWindow(object):
    def setupUi(self, WfmSelWindow):
        if not WfmSelWindow.objectName():
            WfmSelWindow.setObjectName(u"WfmSelWindow")
        WfmSelWindow.resize(300, 112)
        WfmSelWindow.setMinimumSize(QSize(300, 0))
        WfmSelWindow.setMaximumSize(QSize(400, 16777215))
        self.centralWidget = QWidget(WfmSelWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.centralLayout = QVBoxLayout(self.centralWidget)
        self.centralLayout.setSpacing(10)
        self.centralLayout.setObjectName(u"centralLayout")
        self.centralLayout.setContentsMargins(15, 15, 15, 15)
        self.chRawBox = QGroupBox(self.centralWidget)
        self.chRawBox.setObjectName(u"chRawBox")
        self.chRawLayout = QVBoxLayout(self.chRawBox)
        self.chRawLayout.setObjectName(u"chRawLayout")

        self.centralLayout.addWidget(self.chRawBox)

        self.chSpkBox = QGroupBox(self.centralWidget)
        self.chSpkBox.setObjectName(u"chSpkBox")
        self.chSpkLayout = QVBoxLayout(self.chSpkBox)
        self.chSpkLayout.setObjectName(u"chSpkLayout")

        self.centralLayout.addWidget(self.chSpkBox)

        WfmSelWindow.setCentralWidget(self.centralWidget)

        self.retranslateUi(WfmSelWindow)

        QMetaObject.connectSlotsByName(WfmSelWindow)
    # setupUi

    def retranslateUi(self, WfmSelWindow):
        WfmSelWindow.setWindowTitle(QCoreApplication.translate("WfmSelWindow", u"Select Waveforms", None))
#if QT_CONFIG(tooltip)
        self.chRawBox.setToolTip(QCoreApplication.translate("WfmSelWindow", u"Event channel list", None))
#endif // QT_CONFIG(tooltip)
        self.chRawBox.setTitle(QCoreApplication.translate("WfmSelWindow", u"Raw Signal Channels", None))
#if QT_CONFIG(tooltip)
        self.chSpkBox.setToolTip(QCoreApplication.translate("WfmSelWindow", u"Signal channel list", None))
#endif // QT_CONFIG(tooltip)
        self.chSpkBox.setTitle(QCoreApplication.translate("WfmSelWindow", u"Spike Signal Channels", None))
    # retranslateUi

