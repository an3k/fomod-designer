# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'resources/templates/window_about.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(340, 355)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QtCore.QSize(340, 355))
        Dialog.setMaximumSize(QtCore.QSize(340, 355))
        Dialog.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(22)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.version = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.version.sizePolicy().hasHeightForWidth())
        self.version.setSizePolicy(sizePolicy)
        self.version.setScaledContents(False)
        self.version.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.version.setObjectName("version")
        self.verticalLayout.addWidget(self.version)
        self.copyright = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.copyright.sizePolicy().hasHeightForWidth())
        self.copyright.setSizePolicy(sizePolicy)
        self.copyright.setAlignment(QtCore.Qt.AlignCenter)
        self.copyright.setObjectName("copyright")
        self.verticalLayout.addWidget(self.copyright)
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.label_4 = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(5)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setTextFormat(QtCore.Qt.AutoText)
        self.label_4.setScaledContents(False)
        self.label_4.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignVCenter)
        self.label_4.setWordWrap(True)
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)
        self.button = QtWidgets.QPushButton(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button.sizePolicy().hasHeightForWidth())
        self.button.setSizePolicy(sizePolicy)
        self.button.setDefault(False)
        self.button.setObjectName("button")
        self.verticalLayout.addWidget(self.button, 0, QtCore.Qt.AlignHCenter)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "About"))
        self.label.setText(_translate("Dialog", "FOMOD Designer"))
        self.version.setText(_translate("Dialog", "Version: 0.0.0.0"))
        self.copyright.setText(_translate("Dialog", "Copyright 2016 Daniel Nunes"))
        self.label_2.setText(_translate("Dialog", "<html><head/><body><p>Special Thanks to <a href=\"http://forum.step-project.com/user/3928-hishutup/\"><span style=\" text-decoration: underline; color:#0000ff;\">Hishutup</span></a>.</p></body></html>"))
        self.label_4.setText(_translate("Dialog", "<html><head/><body><p>Licensed under the <a href=\"http://www.apache.org/licenses/LICENSE-2.0\"><span style=\" text-decoration: underline; color:#0000ff;\">Apache License</span></a>, Version 2.0 (the &quot;License&quot;); you may not use this file except in compliance with the <a href=\"http://www.apache.org/licenses/LICENSE-2.0\"><span style=\" text-decoration: underline; color:#0000ff;\">License</span></a>. Unless required by applicable law or agreed to in writing, software distributed under the <a href=\"http://www.apache.org/licenses/LICENSE-2.0\"><span style=\" text-decoration: underline; color:#0000ff;\">License</span></a> is distributed on an &quot;AS IS&quot; BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.See the <a href=\"http://www.apache.org/licenses/LICENSE-2.0\"><span style=\" text-decoration: underline; color:#0000ff;\">License</span></a> for the specific language governing permissions and limitations under the <a href=\"http://www.apache.org/licenses/LICENSE-2.0\"><span style=\" text-decoration: underline; color:#0000ff;\">License</span></a>.</p></body></html>"))
        self.button.setText(_translate("Dialog", "Exit"))

