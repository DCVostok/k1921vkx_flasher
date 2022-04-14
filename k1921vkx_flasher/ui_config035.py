# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'config035.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Config035(object):
    def setupUi(self, Config035):
        Config035.setObjectName("Config035")
        Config035.resize(534, 607)
        font = QtGui.QFont()
        font.setFamily("DejaVu Sans")
        font.setPointSize(10)
        Config035.setFont(font)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Config035)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tconfig_frm_cfg = QtWidgets.QFrame(Config035)
        self.tconfig_frm_cfg.setEnabled(True)
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
        self.lbl_warn0_2 = QtWidgets.QLabel(self.tconfig_frm_cfg)
        self.lbl_warn0_2.setTextFormat(QtCore.Qt.RichText)
        self.lbl_warn0_2.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_warn0_2.setObjectName("lbl_warn0_2")
        self.verticalLayout.addWidget(self.lbl_warn0_2)
        self.label = QtWidgets.QLabel(self.tconfig_frm_cfg)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.grid_cfgword = QtWidgets.QGridLayout()
        self.grid_cfgword.setObjectName("grid_cfgword")
        self.form_col0 = QtWidgets.QFormLayout()
        self.form_col0.setObjectName("form_col0")
        self.lbl_bmodedis = QtWidgets.QLabel(self.tconfig_frm_cfg)
        self.lbl_bmodedis.setToolTip("<html><head/><body><p>0 - загрузка из NVR области</p><p align=\"justify\">1 - загрузка из основной области</p></body></html>")
        self.lbl_bmodedis.setObjectName("lbl_bmodedis")
        self.form_col0.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.lbl_bmodedis)
        self.chbox_bmodedis = QtWidgets.QCheckBox(self.tconfig_frm_cfg)
        self.chbox_bmodedis.setText("")
        self.chbox_bmodedis.setChecked(True)
        self.chbox_bmodedis.setObjectName("chbox_bmodedis")
        self.form_col0.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.chbox_bmodedis)
        self.lbl_flashwe = QtWidgets.QLabel(self.tconfig_frm_cfg)
        self.lbl_flashwe.setObjectName("lbl_flashwe")
        self.form_col0.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.lbl_flashwe)
        self.chbox_flashwe = QtWidgets.QCheckBox(self.tconfig_frm_cfg)
        self.chbox_flashwe.setText("")
        self.chbox_flashwe.setChecked(True)
        self.chbox_flashwe.setObjectName("chbox_flashwe")
        self.form_col0.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.chbox_flashwe)
        self.lbl_jtagen = QtWidgets.QLabel(self.tconfig_frm_cfg)
        self.lbl_jtagen.setObjectName("lbl_jtagen")
        self.form_col0.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.lbl_jtagen)
        self.chbox_jtagen = QtWidgets.QCheckBox(self.tconfig_frm_cfg)
        self.chbox_jtagen.setText("")
        self.chbox_jtagen.setChecked(True)
        self.chbox_jtagen.setObjectName("chbox_jtagen")
        self.form_col0.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.chbox_jtagen)
        self.grid_cfgword.addLayout(self.form_col0, 0, 0, 1, 1)
        self.form_col1 = QtWidgets.QFormLayout()
        self.form_col1.setObjectName("form_col1")
        self.lbl_nvrwe = QtWidgets.QLabel(self.tconfig_frm_cfg)
        self.lbl_nvrwe.setObjectName("lbl_nvrwe")
        self.form_col1.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.lbl_nvrwe)
        self.chbox_nvrwe = QtWidgets.QCheckBox(self.tconfig_frm_cfg)
        self.chbox_nvrwe.setText("")
        self.chbox_nvrwe.setChecked(True)
        self.chbox_nvrwe.setObjectName("chbox_nvrwe")
        self.form_col1.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.chbox_nvrwe)
        self.lbl_debugen = QtWidgets.QLabel(self.tconfig_frm_cfg)
        self.lbl_debugen.setObjectName("lbl_debugen")
        self.form_col1.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.lbl_debugen)
        self.chbox_debugen = QtWidgets.QCheckBox(self.tconfig_frm_cfg)
        self.chbox_debugen.setText("")
        self.chbox_debugen.setChecked(True)
        self.chbox_debugen.setObjectName("chbox_debugen")
        self.form_col1.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.chbox_debugen)
        self.grid_cfgword.addLayout(self.form_col1, 0, 1, 1, 1)
        self.verticalLayout.addLayout(self.grid_cfgword)
        self.label_2 = QtWidgets.QLabel(self.tconfig_frm_cfg)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.grid_cfgword_2 = QtWidgets.QGridLayout()
        self.grid_cfgword_2.setObjectName("grid_cfgword_2")
        self.form_col1_2 = QtWidgets.QFormLayout()
        self.form_col1_2.setObjectName("form_col1_2")
        self.lbl_nvrre = QtWidgets.QLabel(self.tconfig_frm_cfg)
        self.lbl_nvrre.setObjectName("lbl_nvrre")
        self.form_col1_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.lbl_nvrre)
        self.chbox_nvrre = QtWidgets.QCheckBox(self.tconfig_frm_cfg)
        self.chbox_nvrre.setText("")
        self.chbox_nvrre.setChecked(True)
        self.chbox_nvrre.setObjectName("chbox_nvrre")
        self.form_col1_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.chbox_nvrre)
        self.grid_cfgword_2.addLayout(self.form_col1_2, 0, 1, 1, 1)
        self.form_col0_2 = QtWidgets.QFormLayout()
        self.form_col0_2.setObjectName("form_col0_2")
        self.lbl_flashre = QtWidgets.QLabel(self.tconfig_frm_cfg)
        self.lbl_flashre.setObjectName("lbl_flashre")
        self.form_col0_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.lbl_flashre)
        self.chbox_flashre = QtWidgets.QCheckBox(self.tconfig_frm_cfg)
        self.chbox_flashre.setText("")
        self.chbox_flashre.setChecked(True)
        self.chbox_flashre.setObjectName("chbox_flashre")
        self.form_col0_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.chbox_flashre)
        self.grid_cfgword_2.addLayout(self.form_col0_2, 0, 0, 1, 1)
        self.verticalLayout.addLayout(self.grid_cfgword_2)
        self.verticalLayout_2.addWidget(self.tconfig_frm_cfg)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)

        self.retranslateUi(Config035)
        QtCore.QMetaObject.connectSlotsByName(Config035)

    def retranslateUi(self, Config035):
        _translate = QtCore.QCoreApplication.translate
        Config035.setWindowTitle(_translate("Config035", "Form"))
        self.lbl_warn0.setText(_translate("Config035", "<html><head/><body><p><span style=\" color:#ef2929;\">Изменяйте состояние конфигурации с осторожностью!</span></p></body></html>"))
        self.lbl_warn0_2.setText(_translate("Config035", "<html><head/><body><p><span style=\" color:#ef2929;\">Изменения вступят в силу только после сброса контроллера!</span></p></body></html>"))
        self.label.setText(_translate("Config035", "CFGWORD"))
        self.lbl_bmodedis.setText(_translate("Config035", "BMODEDIS"))
        self.lbl_flashwe.setToolTip(_translate("Config035", "<html><head/><body><p align=\"justify\">0 - запрещение записи и стирания основной области Flash-памяти</p><p align=\"justify\">1 - разрешение записи и стирания основной области Flash-памяти</p></body></html>"))
        self.lbl_flashwe.setText(_translate("Config035", "FLASHWE"))
        self.lbl_jtagen.setToolTip(_translate("Config035", "<html><head/><body><p>0 - запрещение работы JTAG/SWD функции пина</p><p align=\"justify\">1 - разрешение работы JTAG/SWD функции пина</p></body></html>"))
        self.lbl_jtagen.setText(_translate("Config035", "JTAGEN"))
        self.lbl_nvrwe.setToolTip(_translate("Config035", "<html><head/><body><p>0 - запрещение записи и стирания NVR области Flash-памяти</p><p align=\"justify\">1 - разрешение записи и стирания NVR области Flash-памяти</p></body></html>"))
        self.lbl_nvrwe.setText(_translate("Config035", "NVRWE"))
        self.lbl_debugen.setToolTip(_translate("Config035", "<html><head/><body><p>0 - запрещение работы функции отладки внутри ядра</p><p>1 - разрешение работы функции отладки внутри ядра</p></body></html>"))
        self.lbl_debugen.setText(_translate("Config035", "DEBUGEN"))
        self.label_2.setText(_translate("Config035", "Дополнительные биты конфигурации"))
        self.lbl_nvrre.setToolTip(_translate("Config035", "<html><head/><body><p>0 - запрещение записи и стирания NVR области Flash-памяти</p><p align=\"justify\">1 - разрешение записи и стирания NVR области Flash-памяти</p></body></html>"))
        self.lbl_nvrre.setText(_translate("Config035", "NVRRE"))
        self.lbl_flashre.setToolTip(_translate("Config035", "<html><head/><body><p align=\"justify\">0 - запрещение записи и стирания основной области Flash-памяти</p><p align=\"justify\">1 - разрешение записи и стирания основной области Flash-памяти</p></body></html>"))
        self.lbl_flashre.setText(_translate("Config035", "FLASHRE"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Config035 = QtWidgets.QWidget()
    ui = Ui_Config035()
    ui.setupUi(Config035)
    Config035.show()
    sys.exit(app.exec_())
