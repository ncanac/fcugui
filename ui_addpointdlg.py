# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'addpointdlg.ui'
#
# Created: Wed Apr 21 16:15:06 2010
#      by: PyQt4 UI code generator 4.5.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_AddPointDlg(object):
    def setupUi(self, AddPointDlg):
        AddPointDlg.setObjectName("AddPointDlg")
        AddPointDlg.resize(347, 122)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AddPointDlg.sizePolicy().hasHeightForWidth())
        AddPointDlg.setSizePolicy(sizePolicy)
        self.horizontalLayout = QtGui.QHBoxLayout(AddPointDlg)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.wavelengthLabel = QtGui.QLabel(AddPointDlg)
        self.wavelengthLabel.setObjectName("wavelengthLabel")
        self.gridLayout.addWidget(self.wavelengthLabel, 0, 0, 1, 1)
        self.wavelengthSpinBox = QtGui.QSpinBox(AddPointDlg)
        self.wavelengthSpinBox.setMinimum(350)
        self.wavelengthSpinBox.setMaximum(650)
        self.wavelengthSpinBox.setObjectName("wavelengthSpinBox")
        self.gridLayout.addWidget(self.wavelengthSpinBox, 0, 1, 1, 1)
        self.amplitudeLabel = QtGui.QLabel(AddPointDlg)
        self.amplitudeLabel.setObjectName("amplitudeLabel")
        self.gridLayout.addWidget(self.amplitudeLabel, 1, 0, 1, 1)
        self.amplitudeSpinBox = QtGui.QDoubleSpinBox(AddPointDlg)
        self.amplitudeSpinBox.setMaximum(3.0)
        self.amplitudeSpinBox.setSingleStep(0.01)
        self.amplitudeSpinBox.setObjectName("amplitudeSpinBox")
        self.gridLayout.addWidget(self.amplitudeSpinBox, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.line = QtGui.QFrame(AddPointDlg)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout.addWidget(self.line)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.buttonBox = QtGui.QDialogButtonBox(AddPointDlg)
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_3.addWidget(self.buttonBox)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem1)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.wavelengthLabel.setBuddy(self.wavelengthSpinBox)
        self.amplitudeLabel.setBuddy(self.amplitudeSpinBox)

        self.retranslateUi(AddPointDlg)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), AddPointDlg.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), AddPointDlg.reject)
        QtCore.QMetaObject.connectSlotsByName(AddPointDlg)
        AddPointDlg.setTabOrder(self.wavelengthSpinBox, self.amplitudeSpinBox)
        AddPointDlg.setTabOrder(self.amplitudeSpinBox, self.buttonBox)

    def retranslateUi(self, AddPointDlg):
        AddPointDlg.setWindowTitle(QtGui.QApplication.translate("AddPointDlg", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.wavelengthLabel.setText(QtGui.QApplication.translate("AddPointDlg", "&Wavelength", None, QtGui.QApplication.UnicodeUTF8))
        self.amplitudeLabel.setText(QtGui.QApplication.translate("AddPointDlg", "&Amplitude", None, QtGui.QApplication.UnicodeUTF8))

