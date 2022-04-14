# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'config1921.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Config1921(object):
    def setupUi(self, Config1921):
        Config1921.setObjectName("Config1921")
        Config1921.resize(547, 138)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Config1921)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tconfig_frm_cfg = QtWidgets.QFrame(Config1921)
        self.tconfig_frm_cfg.setEnabled(False)
        self.tconfig_frm_cfg.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tconfig_frm_cfg.setFrameShadow(QtWidgets.QFrame.Raised)
        self.tconfig_frm_cfg.setObjectName("tconfig_frm_cfg")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.tconfig_frm_cfg)
        self.verticalLayout.setObjectName("verticalLayout")
        self.lbl_warn0 = QtWidgets.QLabel(self.tconfig_frm_cfg)
        self.lbl_warn0.setTextFormat(QtCore.Qt.RichText)
        self.lbl_warn0.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_warn0.setObjectName("lbl_warn0")
        self.verticalLayout.addWidget(self.lbl_warn0)
        self.verticalLayout_2.addWidget(self.tconfig_frm_cfg)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)

        self.retranslateUi(Config1921)
        QtCore.QMetaObject.connectSlotsByName(Config1921)

    def retranslateUi(self, Config1921):
        _translate = QtCore.QCoreApplication.translate
        Config1921.setWindowTitle(_translate("Config1921", "Form"))
        self.lbl_warn0.setText(_translate("Config1921", "<html><head/><body><p><span style=\" color:#ef2929;\">Внимание! Изменяйте состояние конфигурации с осторожностью!</span></p></body></html>"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Config1921 = QtWidgets.QWidget()
    ui = Ui_Config1921()
    ui.setupUi(Config1921)
    Config1921.show()
    sys.exit(app.exec_())

