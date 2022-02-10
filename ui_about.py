# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'about.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        AboutDialog.setObjectName("AboutDialog")
        AboutDialog.setWindowModality(QtCore.Qt.NonModal)
        AboutDialog.resize(350, 285)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AboutDialog.sizePolicy().hasHeightForWidth())
        AboutDialog.setSizePolicy(sizePolicy)
        AboutDialog.setMinimumSize(QtCore.QSize(350, 285))
        AboutDialog.setMaximumSize(QtCore.QSize(350, 285))
        font = QtGui.QFont()
        font.setFamily("DejaVu Sans")
        font.setPointSize(10)
        AboutDialog.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/flasher.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        AboutDialog.setWindowIcon(icon)
        AboutDialog.setModal(False)
        self.verticalLayout = QtWidgets.QVBoxLayout(AboutDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.lab_version = QtWidgets.QLabel(AboutDialog)
        self.lab_version.setAlignment(QtCore.Qt.AlignCenter)
        self.lab_version.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.lab_version.setObjectName("lab_version")
        self.verticalLayout.addWidget(self.lab_version)
        self.lab_version_2 = QtWidgets.QLabel(AboutDialog)
        self.lab_version_2.setAlignment(QtCore.Qt.AlignCenter)
        self.lab_version_2.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.lab_version_2.setObjectName("lab_version_2")
        self.verticalLayout.addWidget(self.lab_version_2)
        self.label_3 = QtWidgets.QLabel(AboutDialog)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.buttonBox = QtWidgets.QDialogButtonBox(AboutDialog)
        self.buttonBox.setMaximumSize(QtCore.QSize(16777215, 23))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(AboutDialog)
        self.buttonBox.clicked['QAbstractButton*'].connect(AboutDialog.close)
        QtCore.QMetaObject.connectSlotsByName(AboutDialog)

    def retranslateUi(self, AboutDialog):
        _translate = QtCore.QCoreApplication.translate
        AboutDialog.setWindowTitle(_translate("AboutDialog", "About"))
        self.lab_version.setText(_translate("AboutDialog", "<html><head/><body><p><span style=\" font-size:16pt; font-weight:600;\">K1921VKx Flasher vx.x</span></p><p><img src=\":/icons/flasher.png\"/></p></body></html>"))
        self.lab_version_2.setText(_translate("AboutDialog", "<html><head/><body><p align=\"center\">Утилита взаимодействия с UART загрузчиками </p><p align=\"center\">микроконтроллеров серии К1921ВКх</p></body></html>"))
        self.label_3.setText(_translate("AboutDialog", "АО \"НИИЭТ\", 2019"))

import ui_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    AboutDialog = QtWidgets.QDialog()
    ui = Ui_AboutDialog()
    ui.setupUi(AboutDialog)
    AboutDialog.show()
    sys.exit(app.exec_())

