#!/user/bin/env python3
# coding:utf-8

"""
K1921VKx Flasher Utility
"""

# -- Imports ------------------------------------------------------------------
import sys
import os
import time
import getopt
import inspect
import traceback

import k1921vkx_flasher.logger as logger
import k1921vkx_flasher.serport as serport
import k1921vkx_flasher.mcu as mcu
import k1921vkx_flasher.protocol as protocol

from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QMainWindow, QDialog, QTableWidgetItem, QMessageBox,
                             QHeaderView, QAction, QFileDialog, QLineEdit, QFrame, QWidget, QComboBox, QCheckBox)
from PyQt5.QtGui import (QIcon, QPixmap, QCursor,
                         QRegExpValidator, QTextCursor)
from k1921vkx_flasher.ui_main import Ui_MainWindow
from k1921vkx_flasher.ui_about import Ui_AboutDialog
from k1921vkx_flasher.ui_config035 import Ui_Config035
from k1921vkx_flasher.ui_config028 import Ui_Config028
from k1921vkx_flasher.ui_config01t import Ui_Config01T
from k1921vkx_flasher.ui_config1921 import Ui_Config1921


# -- Global variables ---------------------------------------------------------
VERSION = "1.2"


# -- Misc functions -----------------------------------------------------------

# -- Main window --------------------------------------------------------------
class MyMainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.debug = False

        self.mcu = mcu.get_by_name('k1921vkx')
        self.serport = serport.SerPort(self)
        self.prot = protocol.Protocol(serport=self.serport, win=self)

        # Set up the user interface from QtDesigner
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.tconfig_widget_cfg = QWidget(self.ui.tab_config)
        self.ui.tconfig_vbox.addWidget(self.ui.tconfig_widget_cfg)

        self.ui.tconfig_frm_cfg = QFrame(self.ui.tab_config)

        self.ui.btn_updport.clicked.emit()

        self.ui.tedit_log.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.tedit_log.customContextMenuRequested.connect(
            self.handle_tedit_log_context_menu)

        allowed_nums = "^((0x|)[0-9A-Fa-f]{1,8})|([0-9]{1,10})$"
        self.ui.twrite_ledit_addr.setValidator(
            QRegExpValidator(QtCore.QRegExp(allowed_nums)))
        self.ui.twrite_ledit_size.setValidator(
            QRegExpValidator(QtCore.QRegExp(allowed_nums)))
        self.ui.twrite_ledit_page.setValidator(
            QRegExpValidator(QtCore.QRegExp(allowed_nums)))
        self.ui.twrite_ledit_pages.setValidator(
            QRegExpValidator(QtCore.QRegExp(allowed_nums)))
        self.ui.twrite_ledit_jumpaddr.setValidator(
            QRegExpValidator(QtCore.QRegExp(allowed_nums)))
        self.ui.terase_ledit_addr.setValidator(
            QRegExpValidator(QtCore.QRegExp(allowed_nums)))
        self.ui.terase_ledit_size.setValidator(
            QRegExpValidator(QtCore.QRegExp(allowed_nums)))
        self.ui.terase_ledit_page.setValidator(
            QRegExpValidator(QtCore.QRegExp(allowed_nums)))
        self.ui.terase_ledit_pages.setValidator(
            QRegExpValidator(QtCore.QRegExp(allowed_nums)))
        self.ui.tread_ledit_addr.setValidator(
            QRegExpValidator(QtCore.QRegExp(allowed_nums)))
        self.ui.tread_ledit_size.setValidator(
            QRegExpValidator(QtCore.QRegExp(allowed_nums)))
        self.ui.tread_ledit_page.setValidator(
            QRegExpValidator(QtCore.QRegExp(allowed_nums)))
        self.ui.tread_ledit_pages.setValidator(
            QRegExpValidator(QtCore.QRegExp(allowed_nums)))

        self.icon_lock = QIcon()
        self.icon_unlock = QIcon()
        self.icon_lock.addPixmap(QPixmap(":/icons/lock.png"))
        self.icon_unlock.addPixmap(QPixmap(":/icons/unlock.png"))
        self.ui.tinfo_tbl_flash.horizontalHeader(
        ).setSectionResizeMode(0, QHeaderView.Fixed)
        self.ui.tinfo_tbl_flash.horizontalHeader(
        ).setSectionResizeMode(1, QHeaderView.Fixed)
        self.ui.tinfo_tbl_flash.horizontalHeader(
        ).setSectionResizeMode(2, QHeaderView.Fixed)
        self.ui.tinfo_tbl_flash.horizontalHeader(
        ).setSectionResizeMode(3, QHeaderView.Fixed)
        self.ui.tinfo_tbl_flash.horizontalHeader(
        ).setSectionResizeMode(4, QHeaderView.Fixed)
        self.ui.tinfo_tbl_flash.horizontalHeader().resizeSection(0, 120)
        self.ui.tinfo_tbl_flash.horizontalHeader().resizeSection(1, 120)
        self.ui.tinfo_tbl_flash.horizontalHeader().resizeSection(2, 120)
        self.ui.tinfo_tbl_flash.horizontalHeader().resizeSection(3, 40)
        self.ui.tinfo_tbl_flash.horizontalHeader().resizeSection(4, 40)
        self.ui.tinfo_tbl_flash.horizontalHeaderItem(
            0).setToolTip("Номер страницы")
        self.ui.tinfo_tbl_flash.horizontalHeaderItem(
            1).setToolTip("Начальный адрес страницы")
        self.ui.tinfo_tbl_flash.horizontalHeaderItem(
            2).setToolTip("Размер страницы в байтах")
        self.ui.tinfo_tbl_flash.horizontalHeaderItem(
            3).setToolTip("Защита страницы от чтения")
        self.ui.tinfo_tbl_flash.horizontalHeaderItem(
            4).setToolTip("Защита страницы от записи")

        self.ui.twrite_ledit_filepath.path_for_open = True
        self.ui.tread_ledit_filepath.path_for_open = False
        self.ui.twrite_ledit_filepath.last_text = ""
        self.ui.tread_ledit_filepath.last_text = ""

        self.about_dialog = QDialog(self)
        self.about_dialog.ui = Ui_AboutDialog()
        self.about_dialog.ui.setupUi(self.about_dialog)

        self.upd_flash_selected()
        self.upd_tconfig_widget_cfg()

    # -- Helpers --
    def whoami(self):
        return inspect.getouterframes(inspect.currentframe())[1].function

    def pbar_set(self, value):
        self.log_dbg("<%s> %d" % (self.whoami(), int(value)))
        self.ui.pbar.setValue(int(value))

    def log_dbg(self, msg):
        if self.debug:
            logger.debug(msg)

    def log_info(self, msg):
        logger.info(msg)
        self.ui.tedit_log.appendHtml(
            '[<span style=" color:#4e9a06;">INFO</span>]: %s' % msg)
        QtCore.QCoreApplication.processEvents(QtCore.QEventLoop.AllEvents)

    def log_warn(self, msg):
        logger.warning(msg)
        self.ui.tedit_log.appendHtml(
            '[<span style=" color:#e9b96e;">WARN</span>]: %s' % msg)
        QtCore.QCoreApplication.processEvents(QtCore.QEventLoop.AllEvents)

    def log_err(self, msg, msgbox_en=True):
        logger.error(msg)
        self.ui.tedit_log.appendHtml(
            '[<span style=" color:#ef2929;">ERR</span>]: %s' % msg)
        QtCore.QCoreApplication.processEvents(QtCore.QEventLoop.AllEvents)
        if msgbox_en:
            msgbox = QMessageBox(self)
            msgbox.addButton(QMessageBox.Ok)
            msgbox.setText(msg)
            msgbox.setIcon(QMessageBox.Critical)
            msgbox.exec_()

    def log_crit(self, msg):
        logger.critical(msg)
        self.ui.tedit_log.appendHtml(
            '[<span style=" color:#ad7fa8;">CRIT</span>]: %s' % msg)
        QtCore.QCoreApplication.processEvents(QtCore.QEventLoop.AllEvents)
        msgbox = QMessageBox(self)
        msgbox.addButton(QMessageBox.Ok)
        msgbox.setText(msg)
        msgbox.setIcon(QMessageBox.Critical)
        msgbox.exec_()

    def text2int(self, qobject):
        try:
            num = int(qobject.text(), 10)
            num_format = 'dec'
        except ValueError:
            num = int(qobject.text(), 16)
            num_format = 'hex'
        return (num, num_format)

    # -- Events --
    def closeEvent(self, event):
        if self.serport.is_open:
            self.prot.deinit()
        event.accept()

    # -- Slots --
    def handle_ledit_addr_edited(self):
        self.log_dbg("Handler <%s> called" % self.whoami())
        ledit_addr = self.sender().parent().findChildren(
            QLineEdit, QtCore.QRegExp('^.*_addr$'))[0]
        ledit_page = self.sender().parent().findChildren(
            QLineEdit, QtCore.QRegExp('^.*_page$'))[0]
        self.log_dbg("Object <%s>" % ledit_addr.objectName())
        addr, addr_format = self.text2int(ledit_addr)
        page_size = self.mcu.flash[self.get_curr_flash(
        )][self.get_curr_region()].page_size
        pages = self.mcu.flash[self.get_curr_flash()
                               ][self.get_curr_region()].pages

        if addr >= (page_size * pages):
            self.log_warn(
                "Адрес выходит за границы диапазона 0x00000000-0x%08X" % ((page_size * pages) - 1))
            addr = 0

        aligned_addr = ((addr & 0xFFFFFF) // page_size) * page_size
        ledit_addr.setText("%s" % (
            "%d" % aligned_addr if addr_format == 'dec' else "0x%08X" % aligned_addr))
        if addr != aligned_addr:
            self.log_info("Адрес 0x%08X был выровнен по размеру страницы (0x%X) - 0x%08X" %
                          (addr, page_size, aligned_addr))

        ledit_page.setText("%d" % (aligned_addr // page_size))

    def handle_ledit_size_edited(self):
        self.log_dbg("Handler <%s> called" % self.whoami())
        ledit_addr = self.sender().parent().findChildren(
            QLineEdit, QtCore.QRegExp('^.*_addr$'))[0]
        ledit_size = self.sender().parent().findChildren(
            QLineEdit, QtCore.QRegExp('^.*_size$'))[0]
        ledit_pages = self.sender().parent().findChildren(
            QLineEdit, QtCore.QRegExp('^.*_pages$'))[0]
        self.log_dbg("Object <%s>" % ledit_size.objectName())
        addr, addr_format = self.text2int(ledit_addr)
        size, size_format = self.text2int(ledit_size)
        page_size = self.mcu.flash[self.get_curr_flash(
        )][self.get_curr_region()].page_size
        pages_total = self.mcu.flash[self.get_curr_flash(
        )][self.get_curr_region()].pages

        if size > ((page_size * pages_total) - addr):
            self.log_warn("Размер области должен быть не более 0x%X байт" % (
                (page_size * pages_total) - addr))
            size = 0

        aligned_size = ((size // page_size) + (1 if size %
                        page_size else 0)) * page_size
        ledit_size.setText("%s" % (
            "%d" % aligned_size if size_format == 'dec' else "0x%08X" % aligned_size))
        if size != aligned_size:
            self.log_info("Размер 0x%X был выровнен по размеру страницы (0x%X) - 0x%X" %
                          (size, page_size, aligned_size))

        ledit_pages.setText("%d" % (aligned_size // page_size))

    def handle_ledit_page_edited(self):
        self.log_dbg("Handler <%s> called" % self.whoami())
        ledit_addr = self.sender().parent().findChildren(
            QLineEdit, QtCore.QRegExp('^.*_addr$'))[0]
        ledit_page = self.sender().parent().findChildren(
            QLineEdit, QtCore.QRegExp('^.*_page$'))[0]
        self.log_dbg("Object <%s>" % ledit_page.objectName())
        page, page_format = self.text2int(ledit_page)
        page_size = self.mcu.flash[self.get_curr_flash(
        )][self.get_curr_region()].page_size
        pages = self.mcu.flash[self.get_curr_flash()
                               ][self.get_curr_region()].pages

        if page >= pages:
            self.log_warn(
                "Номер страницы выходит за границы диапазона 0-%d" % (pages - 1))
            page = 0

        ledit_page.setText("%d" % page)
        ledit_addr.setText("0x%08X" % (page * page_size))

    def handle_ledit_pages_edited(self):
        self.log_dbg("Handler <%s> called" % self.whoami())
        ledit_size = self.sender().parent().findChildren(
            QLineEdit, QtCore.QRegExp('^.*_size$'))[0]
        ledit_pages = self.sender().parent().findChildren(
            QLineEdit, QtCore.QRegExp('^.*_pages$'))[0]
        ledit_page = self.sender().parent().findChildren(
            QLineEdit, QtCore.QRegExp('^.*_page$'))[0]
        self.log_dbg("Object <%s>" % ledit_pages.objectName())
        pages, pages_format = self.text2int(ledit_pages)
        page, page_format = self.text2int(ledit_page)
        page_size = self.mcu.flash[self.get_curr_flash(
        )][self.get_curr_region()].page_size
        pages_total = self.mcu.flash[self.get_curr_flash(
        )][self.get_curr_region()].pages

        if pages > (pages_total - page):
            self.log_warn("Указанное количество страниц больше максимального (%d)" % (
                pages_total - page))
            pages = 0

        ledit_pages.setText("%d" % pages)
        ledit_size.setText("0x%08X" % (pages * page_size))

    def handle_twrite_chbox_jump_toggled(self, state):
        self.log_dbg("Handler <%s> called" % (self.whoami() + "(%d)" % state))
        # self.ui.twrite_ledit_jumpaddr.setEnabled(state)

    def handle_tedit_log_context_menu(self, pos):
        self.log_dbg("Handler <%s> called" % self.whoami())
        menu = self.ui.tedit_log.createStandardContextMenu()
        menu.act_clear = QAction("Очистить")
        menu.act_clear.triggered.connect(self.ui.tedit_log.clear)
        menu.insertActions(menu.actions()[0], [menu.act_clear])
        menu.exec_(QCursor.pos())

    def handle_btn_updport_clicked(self):
        self.log_dbg("Handler <%s> called" % self.whoami())
        self.ui.combo_port.clear()
        [self.ui.combo_port.addItem(port)
         for port in self.serport.list_ports()]

    def handle_act_about_triggered(self):
        self.log_dbg("Handler <%s> called" % self.whoami())
        text = self.about_dialog.ui.lab_version.text().replace("x.x", VERSION)
        self.about_dialog.ui.lab_version.setText(text)
        self.about_dialog.exec_()

    def handle_btn_connect_clicked(self):
        self.log_dbg("Handler <%s> called" % self.whoami())
        self.ui.tedit_log.moveCursor(QTextCursor.End)
        self.ui.pbar.reset()
        self.log_info("--------------------")
        update_gui = False
        port = self.ui.combo_port.currentText()
        baud = self.ui.combo_baud.currentText()
        if (not self.is_connected()):
            if not self.ui.combo_port.count():
                self.log_warn("Выберите COM-порт!")
            else:
                state = True
                btn_text = "Отключиться"
                try:
                    self.mcu = self.prot.init(port=port, baud=baud)
                    update_gui = True
                except:
                    self.prot.deinit()
                    self.log_err(
                        "Подключиться не удалось. Убедитесь что загрузчик разрешён и сбросьте устройство.")
                    traceback.print_exc()
        else:
            state = False
            btn_text = "Подключиться"
            self.prot.deinit()
            self.mcu = mcu.get_by_name('k1921vkx')
            update_gui = True

        if update_gui:
            self.ui.btn_connect.setText(btn_text)
            self.ui.combo_port.setEnabled(not state)
            self.ui.combo_baud.setEnabled(not state)
            self.ui.btn_updport.setEnabled(not state)
            self.ui.btn_exec.setEnabled(state)
            self.ui.tab_info.setEnabled(state)
            self.ui.tab_write.setEnabled(state)
            self.ui.tab_erase.setEnabled(state)
            self.ui.tab_read.setEnabled(state)
            self.ui.tab_config.setEnabled(state)
            self.ui.gbox_flash.setEnabled(state)
            self.ui.gbox_region.setEnabled(state)
            self.upd_gbox_flash()
            self.upd_tinfo_values()
            self.upd_flash_selected()
            self.upd_twrite_jumpaddr()
            self.upd_twrite_addr()
            self.upd_tconfig_widget_cfg()

    def handle_flash_select_toggled(self, state):
        self.log_dbg("Handler <%s> called" % (self.whoami() + "(%d)" % state))
        if state:
            self.upd_flash_selected()

    def handle_region_select_toggled(self, state):
        self.log_dbg("Handler <%s> called" % (self.whoami() + "(%d)" % state))
        if state:
            self.upd_flash_selected()

    def handle_btn_exec_clicked(self):
        self.log_dbg("Handler <%s> called" % self.whoami())
        curr_tab = self.ui.tabs_cmd.currentWidget().objectName()
        self.log_dbg("Tab <%s> active" % curr_tab)
        self.ui.tedit_log.moveCursor(QTextCursor.End)
        self.ui.pbar.reset()
        self.log_info("--------------------")
        if curr_tab == "tab_info":
            self.exec_tab_info()
        elif curr_tab == "tab_write":
            self.exec_tab_write()
        elif curr_tab == "tab_read":
            self.exec_tab_read()
        elif curr_tab == "tab_erase":
            self.exec_tab_erase()
        elif curr_tab == "tab_config":
            self.exec_tab_config()

    def handle_ledit_filepath_changed(self, text):
        self.log_dbg("Handler <%s> called" % self.whoami())
        self.log_dbg("Sender <%s>" % self.sender().objectName())

        if self.sender().path_for_open:
            if (os.path.isfile(self.sender().text()) and self.sender().text()[-4:] == '.bin' and self.sender().text() != self.sender().last_text):

                self.sender().setStyleSheet("color: black;")
            else:
                self.sender().setStyleSheet("color: red;")
        self.sender().last_text = self.sender().text()

        if ("twrite" in self.sender().objectName() and
           self.is_valid_path(self.ui.twrite_ledit_filepath)):
            filesize = os.path.getsize(self.ui.twrite_ledit_filepath.text())
            page_size = self.mcu.flash[self.get_curr_flash(
            )][self.get_curr_region()].page_size
            addr, addr_format = self.text2int(self.ui.twrite_ledit_addr)
            pages_total = self.mcu.flash[self.get_curr_flash(
            )][self.get_curr_region()].pages
            if filesize > ((page_size * pages_total) - addr):
                self.ui.twrite_ledit_size.setText("ошибка")
                self.ui.twrite_ledit_pages.setText("ошибка")
            else:
                self.ui.twrite_ledit_size.setText("0x%08X" % (
                    ((filesize // page_size) + (1 if filesize % page_size else 0)) * page_size))
                self.ui.twrite_ledit_pages.setText(
                    "%d" % ((filesize // page_size) + (1 if filesize % page_size else 0)))

    def handle_btn_fileopen_clicked(self):
        self.log_dbg("Handler <%s> called" % self.whoami())
        rexp_ledit = QtCore.QRegExp('^.*_filepath$')
        linked_ledit = self.sender().parent().findChildren(
            QLineEdit, rexp_ledit)[0]
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, "Открыть бинарный файл", linked_ledit.text(), "Бинарные файлы (*.bin)",
                                                  options=options)
        if filename:
            linked_ledit.setText(filename)

    def handle_btn_filesave_clicked(self):
        self.log_dbg("Handler <%s> called" % self.whoami())
        rexp_ledit = QtCore.QRegExp('^.*_filepath$')
        linked_ledit = self.sender().parent().findChildren(
            QLineEdit, rexp_ledit)[0]
        options = QFileDialog.Options()
        if linked_ledit.text():
            save_name = linked_ledit.text()
        else:
            save_name = "dump.bin"
        filename, _ = QFileDialog.getSaveFileName(self, "Сохранить бинарный файл", save_name, "Бинарные файлы (*.bin)",
                                                  options=options)
        if filename:
            linked_ledit.setText(filename)

    def handle_terase_mode_select_toggled(self, state):
        self.log_dbg("Handler <%s> called" % (self.whoami() + "(%d)" % state))
        if state:
            self.ui.terase_frm_addr.setEnabled(
                self.ui.terase_rbtn_erpages.isChecked())

    def handle_tconfig_mode_select_toggled(self, state):
        self.log_dbg("Handler <%s> called" % (self.whoami() + "(%d)" % state))
        if state:
            for child in self.ui.tconfig_widget_cfg.findChildren(QCheckBox, QtCore.QRegExp('.*')):
                child.setEnabled(self.ui.tconfig_rbtn_write.isChecked())
            for child in self.ui.tconfig_widget_cfg.findChildren(QComboBox, QtCore.QRegExp('.*')):
                child.setEnabled(self.ui.tconfig_rbtn_write.isChecked())

    def handle_tabs_cmd_changed(self, num):
        self.log_dbg("Handler <%s> called" % (self.whoami() + "(%d)" % num))
        self.ui.pbar.reset()
        if self.is_connected():
            if self.ui.tabs_cmd.currentWidget().objectName() == 'tab_info':
                self.ui.btn_exec.setEnabled(False)
            else:
                self.ui.btn_exec.setEnabled(True)

    def handle_firstpage_select_changed(self, num):
        self.log_dbg("Handler <%s> called" % (self.whoami() + "(%d)" % num))
        self.log_dbg("Sender <%s>" % self.sender().objectName())
        if num != -1:
            rexp_combo = QtCore.QRegExp('^.*_lastpage$')
            combo_firstpage = self.sender()
            combo_lastpage = self.sender().parent(
            ).findChildren(QComboBox, rexp_combo)[0]
            combo_lastpage.clear()
            for i in range(combo_firstpage.currentIndex(), combo_firstpage.count()):
                combo_lastpage.addItem(combo_firstpage.itemText(i))
            if "twrite" in self.sender().objectName():
                self.handle_twrite_combo_lastpage_changed(0)

    # -- Application specific code --
    def is_connected(self):
        return not self.ui.combo_port.isEnabled()

    def is_valid_path(self, ledit_path):
        return False if ('red' in ledit_path.styleSheet()) or (not ledit_path.text()) else True

    def get_curr_flash(self):
        if self.ui.rbtn_flash0.isChecked():
            return 0
        else:
            return 1

    def get_curr_region(self):
        if self.ui.rbtn_regionnvr.isChecked():
            return 'region_nvr'
        else:
            return 'region_main'

    def upd_gbox_flash(self):
        self.ui.rbtn_flash0.setText(self.mcu.flash[0]['name'].upper())
        if len(self.mcu.flash) == 2:
            self.ui.rbtn_flash1.setEnabled(True)
            self.ui.rbtn_flash1.setText(self.mcu.flash[1]['name'].upper())
        else:
            self.ui.rbtn_flash1.setEnabled(False)
            self.ui.rbtn_flash1.setText('')

    def upd_tinfo_values(self):
        self.ui.tinfo_ledit_chipid.setText(self.mcu.chipid)
        self.ui.tinfo_ledit_cpuid.setText(self.mcu.cpuid)
        self.ui.tinfo_ledit_bootver.setText(self.mcu.bootver)
        self.ui.tinfo_lab_mcu.setText(self.mcu.name)

    def upd_flash_selected(self):
        table = self.ui.tinfo_tbl_flash

        table.clearContents()

        for r in reversed(range(table.rowCount())):
            table.removeRow(r)
        pages = self.mcu.flash[self.get_curr_flash()
                               ][self.get_curr_region()].pages
        page_size = self.mcu.flash[self.get_curr_flash(
        )][self.get_curr_region()].page_size
        rd_lock = self.mcu.flash[self.get_curr_flash(
        )][self.get_curr_region()].rd_lock
        wr_lock = self.mcu.flash[self.get_curr_flash(
        )][self.get_curr_region()].wr_lock
        for r in range(0, pages):
            table.insertRow(r)
            table.setItem(r, 0, QTableWidgetItem("Страница %d" % r))
            table.setItem(r, 1, QTableWidgetItem("0x%x" % (r * page_size)))
            if page_size < 1024:
                page_size_str = "0x%x (%d)" % (page_size, page_size)
            else:
                page_size_str = "0x%x (%dK)" % (page_size, page_size // 1024)
            table.setItem(r, 2, QTableWidgetItem("%s" % page_size_str))
            if rd_lock[r]:
                rd_cell = QTableWidgetItem(self.icon_lock, "")
                rd_cell.setToolTip("Заблокировано")
            else:
                rd_cell = QTableWidgetItem(self.icon_unlock, "")
                rd_cell.setToolTip("Разблокировано")
            table.setItem(r, 3, rd_cell)
            if wr_lock[r]:
                wr_cell = QTableWidgetItem(self.icon_lock, "")
                wr_cell.setToolTip("Заблокировано")
            else:
                wr_cell = QTableWidgetItem(self.icon_unlock, "")
                wr_cell.setToolTip("Разблокировано")
            table.setItem(r, 4, wr_cell)

    def upd_twrite_jumpaddr(self):
        self.ui.twrite_ledit_jumpaddr.setEnabled(False)
        if self.mcu.name == 'k1921vk035':
            self.ui.twrite_ledit_jumpaddr.setText('0x00000000')
        elif self.mcu.name == 'k1921vk028':
            self.ui.twrite_ledit_jumpaddr.setText('0x10000000')
        elif self.mcu.name == 'k1921vk01t':
            self.ui.twrite_ledit_jumpaddr.setText('0x00002000')
        elif self.mcu.name == 'k1921vkx':
            self.ui.twrite_ledit_jumpaddr.setText('0x00000000')

    def upd_twrite_addr(self):
        if self.mcu.name == 'k1921vk01t':
            self.ui.twrite_ledit_addr.setText('0x00002000')
        else:
            self.ui.twrite_ledit_addr.setText('0x00000000')
        self.ui.twrite_ledit_addr.editingFinished.emit()

    def upd_tconfig_widget_cfg(self):
        self.ui.tconfig_rbtn_read.setChecked(True)
        self.ui.tconfig_vbox.removeWidget(self.ui.tconfig_widget_cfg)
        self.ui.tconfig_widget_cfg.deleteLater()
        self.ui.tconfig_widget_cfg = None

        self.ui.tconfig_widget_cfg = QWidget(self.ui.tab_config)
        self.ui.tconfig_vbox.addWidget(self.ui.tconfig_widget_cfg)
        # pre-setup
        if self.mcu.name == 'k1921vk035':
            self.ui.tconfig_widget_cfg.ui = Ui_Config035()
        elif self.mcu.name == 'k1921vk028':
            self.ui.tconfig_widget_cfg.ui = Ui_Config028()
        elif self.mcu.name == 'k1921vk01t':
            self.ui.tconfig_widget_cfg.ui = Ui_Config01T()
        elif self.mcu.name == 'k1921vkx':
            self.ui.tconfig_widget_cfg.ui = Ui_Config1921()
        # setup
        self.ui.tconfig_widget_cfg.ui.setupUi(self.ui.tconfig_widget_cfg)
        self.ui.tconfig_rbtn_read.toggled['bool'].emit(True)
        # post-setup
        if self.mcu.name == 'k1921vk035':
            self.exec_tab_config_035(self.mcu.cfgword)
        elif self.mcu.name == 'k1921vk028':
            allowed_nums = "^((0x|)[0-9A-Fa-f]{1,3})|([0-9]{1,4})$"
            self.ui.tconfig_widget_cfg.ui.ledit_mask.setValidator(
                QRegExpValidator(QtCore.QRegExp(allowed_nums)))
            allowed_nums = "^((0x|)[0-9A-Fa-f]{1})|([0-9]{1,2})$"
            self.ui.tconfig_widget_cfg.ui.ledit_wrc.setValidator(
                QRegExpValidator(QtCore.QRegExp(allowed_nums)))
            self.ui.tconfig_widget_cfg.ui.ledit_rdc.setValidator(
                QRegExpValidator(QtCore.QRegExp(allowed_nums)))
            self.ui.tconfig_widget_cfg.ui.ledit_tac.setValidator(
                QRegExpValidator(QtCore.QRegExp(allowed_nums)))
        elif self.mcu.name == 'k1921vk01t':
            self.exec_tab_config_01t(self.mcu.cfgword)
        elif self.mcu.name == 'k1921vkx':
            pass

    def exec_prot_wrapper(self, str_ok, str_fail, cmdf):
        ret = None
        #msgbox = QMessageBox(self)
        # msgbox.addButton(QMessageBox.Ok)
        # msgbox.setIcon(QMessageBox.Information)
        try:
            exec_start = time.time()
            ret = cmdf()
            res_str = "%s Время: %0.3f сек." % (
                str_ok, (time.time() - exec_start))
            self.log_info(res_str)
            # msgbox.setText(res_str)
            # msgbox.exec_()
        except:
            self.log_err(str_fail)
            traceback.print_exc()
        return ret

    def exec_tab_info(self):
        pass

    def exec_tab_write(self):
        self.log_info(
            'Подготовка к выполнению команды записи. Чтение опций ...')
        self.log_info('Флеш - %s' %
                      self.mcu.flash[self.get_curr_flash()]["name"].upper())
        self.log_info('Область - %s' % ("основная" if self.get_curr_region()
                      == "region_main" else "NVR/Info"))
        filepath = self.ui.twrite_ledit_filepath.text()
        filevalid = self.is_valid_path(self.ui.twrite_ledit_filepath)
        addr = self.text2int(self.ui.twrite_ledit_addr)[0]
        firstpage = self.text2int(self.ui.twrite_ledit_page)[0]
        if self.ui.twrite_ledit_size.text() == 'ошибка':
            return self.log_err('Не выполнено - размер файла превышает размер выбранной области!')
        else:
            lastpage = firstpage + \
                self.text2int(self.ui.twrite_ledit_pages)[0] - 1

        ernone = True if self.ui.twrite_rbtn_ernone.isChecked() else False
        erall = True if self.ui.twrite_rbtn_erall.isChecked() else False
        erpages = True if self.ui.twrite_rbtn_erpages.isChecked() else False
        verif = True if self.ui.twrite_chbox_verif.isChecked() else False
        jump = True if self.ui.twrite_chbox_jump.isChecked() else False
        jumpaddr = self.text2int(self.ui.twrite_ledit_jumpaddr)[0]

        if filevalid:
            self.log_info('Файл - "%s", размер %d байт' %
                          (filepath, os.path.getsize(filepath)))
        else:
            return self.log_err('Не выполнено - файла "%s" не существует!' % filepath)

        self.log_info('Модифицируемые страницы - %d ... %d' %
                      (firstpage, lastpage))

        if ernone:
            self.log_info('Стирание - нет')
        elif erall:
            self.log_info('Стирание - вся область')
        elif erpages:
            self.log_info('Стирание - только необходимые страницы')
        else:
            return self.log_err('Не выполнено - режим стирания не определён')

        curr_flash = self.mcu.flash[self.get_curr_flash(
        )][self.get_curr_region()]
        if verif:
            for p in range(firstpage, lastpage + 1):
                if curr_flash.rd_lock[p]:
                    verif = False
                    self.log_warn(
                        'Верификация невозможна - одна или несколько считываемых страниц защищены от чтения')
        self.log_info('Верификация - %s' % ("да" if verif else "нет"))
        if jump:
            self.log_info(
                'Переход к исполнению программы - адрес 0x%08X' % jumpaddr)
        else:
            self.log_info('Переход к исполнению программы - нет')

        for p in range(firstpage, lastpage + 1):
            if curr_flash.wr_lock[p]:
                return self.log_err('Не выполнено - одна или несколько модифицируемых страниц защищены от записи/стирания')
        if erall:
            for page_locked in curr_flash.wr_lock:
                if page_locked:
                    return self.log_err('Не выполнено - одна или несколько модифицируемых страниц защищены от записи/стирания')

        self.exec_prot_wrapper(str_ok='Команда записи выполнена!',
                               str_fail='Команда записи не выполнена - ошибка протокола!',
                               cmdf=lambda: self.prot.write(filepath=filepath, addr=addr, firstpage=firstpage, lastpage=lastpage,
                                                            ernone=ernone, erall=erall, erpages=erpages,
                                                            verif=verif, jump=jump, jumpaddr=jumpaddr))

    def exec_tab_erase(self):
        self.log_info(
            'Подготовка к выполнению команды стирания. Чтение опций ...')
        self.log_info('Флеш - %s' %
                      self.mcu.flash[self.get_curr_flash()]["name"].upper())
        self.log_info('Область - %s' % ("основная" if self.get_curr_region()
                      == "region_main" else "NVR/Info"))

        erall = True if self.ui.terase_rbtn_erall.isChecked() else False
        erpages = True if self.ui.terase_rbtn_erpages.isChecked() else False

        curr_flash = self.mcu.flash[self.get_curr_flash(
        )][self.get_curr_region()]
        if erall:
            firstpage = 0
            lastpage = curr_flash.pages - 1
            self.log_info('Стирание - вся область')
        elif erpages:
            firstpage = self.text2int(self.ui.terase_ledit_page)[0]
            pages = self.text2int(self.ui.terase_ledit_pages)[0]
            if pages:
                lastpage = firstpage + pages - 1
            else:
                return self.log_err('Не выполнено - не определён размер стираемой области')
        else:
            return self.log_err('Не выполнено - режим стирания не определён')

        if erpages:
            size = self.text2int(self.ui.terase_ledit_size)[0]
        else:
            size = curr_flash.size
        self.log_info('Модифицируемые страницы - %d ... %d (%d байт)' %
                      (firstpage, lastpage, size))

        for p in range(firstpage, lastpage + 1):
            if curr_flash.wr_lock[p]:
                return self.log_err('Не выполнено - одна или несколько модифицируемых страниц защищены от записи/стирания')

        self.exec_prot_wrapper(str_ok='Команда стирания выполнена!',
                               str_fail='Команда стирания не выполнена - ошибка протокола!',
                               cmdf=lambda: self.prot.erase(firstpage=firstpage, lastpage=lastpage, erall=erall, erpages=erpages))

    def exec_tab_read(self):
        self.log_info(
            'Подготовка к выполнению команды чтения. Чтение опций ...')
        self.log_info('Флеш - %s' %
                      self.mcu.flash[self.get_curr_flash()]["name"].upper())
        self.log_info('Область - %s' % ("основная" if self.get_curr_region()
                      == "region_main" else "NVR/Info"))
        filepath = self.ui.tread_ledit_filepath.text()
        try:
            open(filepath, 'w')
        except (FileNotFoundError, IsADirectoryError, PermissionError):
            return self.log_err('Не выполнено - некорректный путь для сохранения')
        size = self.text2int(self.ui.tread_ledit_size)[0]
        self.log_info('Файл - "%s", размер %d байт' % (filepath, size))
        firstpage = self.text2int(self.ui.tread_ledit_page)[0]
        pages = self.text2int(self.ui.tread_ledit_pages)[0]
        if pages:
            lastpage = firstpage + pages - 1
        else:
            return self.log_err('Не выполнено - не определён размер считываемой области')

        self.log_info('Считываемые страницы - %d ... %d' %
                      (firstpage, lastpage))

        curr_flash = self.mcu.flash[self.get_curr_flash(
        )][self.get_curr_region()]
        for p in range(firstpage, lastpage + 1):
            if curr_flash.rd_lock[p]:
                return self.log_err('Не выполнено - одна или несколько считываемых страниц защищены от чтения')

        self.exec_prot_wrapper(str_ok='Команда чтения выполнена!',
                               str_fail='Команда чтения не выполнена - ошибка протокола!',
                               cmdf=lambda: self.prot.read(filepath=filepath, firstpage=firstpage, lastpage=lastpage))

    def exec_tab_config(self):
        if self.ui.tconfig_rbtn_read.isChecked():
            cfgword = self.exec_prot_wrapper(str_ok='Команда чтения CFGWORD выполнена!',
                                             str_fail='Команда чтения CFGWORD не выполнена!',
                                             cmdf=lambda: self.prot.get_cfgword())
            self.mcu.apply_cfgword(cfgword)
            self.upd_flash_selected()
            if self.mcu.name == 'k1921vk035':
                self.exec_tab_config_035(cfgword)
            elif self.mcu.name == 'k1921vk028':
                self.exec_tab_config_028(cfgword)
            elif self.mcu.name == 'k1921vk01t':
                self.exec_tab_config_01t(cfgword)
        else:
            if self.mcu.name == 'k1921vk035':
                cfgword = self.exec_tab_config_035()
            elif self.mcu.name == 'k1921vk028':
                cfgword = self.exec_tab_config_028()
            elif self.mcu.name == 'k1921vk01t':
                cfgword = self.exec_tab_config_01t()
            self.exec_prot_wrapper(str_ok='Команда записи CFGWORD выполнена!',
                                   str_fail='Команда записи CFGWORD не выполнена!',
                                   cmdf=lambda: self.prot.set_cfgword(cfgword=cfgword))
            self.mcu.apply_cfgword(cfgword)
            self.upd_flash_selected()

    def exec_tab_config_035(self, cfgword=None):
        widget035 = self.ui.tconfig_widget_cfg
        if cfgword:
            widget035.ui.chbox_bmodedis.setChecked(cfgword['bmodedis'])
            widget035.ui.chbox_flashwe.setChecked(cfgword['flashwe'])
            widget035.ui.chbox_nvrwe.setChecked(cfgword['nvrwe'])
            widget035.ui.chbox_debugen.setChecked(cfgword['debugen'])
            widget035.ui.chbox_jtagen.setChecked(cfgword['jtagen'])
            widget035.ui.chbox_flashre.setChecked(cfgword['flashre'])
            widget035.ui.chbox_nvrre.setChecked(cfgword['nvrre'])
        else:
            cfgword = {}
            cfgword['bmodedis'] = widget035.ui.chbox_bmodedis.isChecked()
            cfgword['flashwe'] = widget035.ui.chbox_flashwe.isChecked()
            cfgword['nvrwe'] = widget035.ui.chbox_nvrwe.isChecked()
            cfgword['debugen'] = widget035.ui.chbox_debugen.isChecked()
            cfgword['jtagen'] = widget035.ui.chbox_jtagen.isChecked()
            cfgword['flashre'] = widget035.ui.chbox_flashre.isChecked()
            cfgword['nvrre'] = widget035.ui.chbox_nvrre.isChecked()
            return cfgword

    def exec_tab_config_028(self, cfgword=None):
        widget028 = self.ui.tconfig_widget_cfg
        if cfgword:
            widget028.ui.chbox_bflashre.setChecked(cfgword['bflashre'])
            widget028.ui.chbox_bflashwe.setChecked(cfgword['bflashwe'])
            widget028.ui.chbox_bnvrre.setChecked(cfgword['bnvrre'])
            widget028.ui.chbox_bnvrwe.setChecked(cfgword['bnvrwe'])
            widget028.ui.chbox_mflashre.setChecked(cfgword['mflashre'])
            widget028.ui.chbox_mflashwe.setChecked(cfgword['mflashwe'])
            widget028.ui.chbox_mnvrre.setChecked(cfgword['mnvrre'])
            widget028.ui.chbox_mnvrwe.setChecked(cfgword['mnvrwe'])
            widget028.ui.chbox_debugen.setChecked(cfgword['debugen'])
            widget028.ui.chbox_jtagen.setChecked(cfgword['jtagen'])
            widget028.ui.combo_af.setCurrentIndex(int(cfgword['af']))
            widget028.ui.combo_mode.setCurrentIndex(int(cfgword['mode']))
            widget028.ui.ledit_mask.setText('0x%03x' % cfgword['mask'])
            widget028.ui.ledit_rdc.setText('0x%01x' % cfgword['rdc'])
            widget028.ui.ledit_wrc.setText('0x%01x' % cfgword['wrc'])
            widget028.ui.ledit_tac.setText('0x%01x' % cfgword['tac'])
        else:
            cfgword = {}
            cfgword['bflashre'] = widget028.ui.chbox_bflashre.isChecked()
            cfgword['bflashwe'] = widget028.ui.chbox_bflashwe.isChecked()
            cfgword['bnvrre'] = widget028.ui.chbox_bnvrre.isChecked()
            cfgword['bnvrwe'] = widget028.ui.chbox_bnvrwe.isChecked()
            cfgword['mflashre'] = widget028.ui.chbox_mflashre.isChecked()
            cfgword['mflashwe'] = widget028.ui.chbox_mflashwe.isChecked()
            cfgword['mnvrre'] = widget028.ui.chbox_mnvrre.isChecked()
            cfgword['mnvrwe'] = widget028.ui.chbox_mnvrwe.isChecked()
            cfgword['debugen'] = widget028.ui.chbox_debugen.isChecked()
            cfgword['jtagen'] = widget028.ui.chbox_jtagen.isChecked()
            cfgword['af'] = widget028.ui.combo_af.currentIndex()
            cfgword['mode'] = widget028.ui.combo_mode.currentIndex()
            cfgword['mask'] = self.text2int(widget028.ui.ledit_mask)[0]
            cfgword['rdc'] = self.text2int(widget028.ui.ledit_rdc)[0]
            cfgword['wrc'] = self.text2int(widget028.ui.ledit_wrc)[0]
            cfgword['tac'] = self.text2int(widget028.ui.ledit_tac)[0]
            return cfgword

    def exec_tab_config_01t(self, cfgword=None):
        widget01t = self.ui.tconfig_widget_cfg
        bflock = widget01t.findChildren(
            QCheckBox, QtCore.QRegExp('^chbox_bf_lock_page_.*$'))
        uflock = widget01t.findChildren(
            QCheckBox, QtCore.QRegExp('^chbox_uf_lock_page_.*$'))
        if cfgword:
            widget01t.ui.chbox_bootfrom_ifb.setChecked(
                cfgword['boot_from_ifb'])
            widget01t.ui.chbox_en_gpio.setChecked(cfgword['en_gpio'])
            widget01t.ui.combo_extmemsel.setCurrentIndex(
                int(cfgword['extmem_sel']))
            widget01t.ui.combo_pinnum.setCurrentIndex(int(cfgword['pinnum']))
            widget01t.ui.combo_portnum.setCurrentIndex(
                int(cfgword['portnum']) & 7)
            widget01t.ui.chbox_lock_ifb_lf.setChecked(cfgword['lock_ifb_lf'])
            widget01t.ui.chbox_bfre.setChecked(cfgword['bfre'])
            widget01t.ui.chbox_bfifbre.setChecked(cfgword['bfifbre'])
            widget01t.ui.chbox_lock_ifb_uf.setChecked(cfgword['lock_ifb_uf'])
            widget01t.ui.chbox_ufre.setChecked(cfgword['ufre'])
            widget01t.ui.chbox_ufifbre.setChecked(cfgword['ufifbre'])
            for p in range(0, len(bflock)):
                bflock[p].setChecked(cfgword['bflock'][p])
            for p in range(0, len(uflock)):
                uflock[p].setChecked(cfgword['uflock'][p])
        else:
            cfgword = {}
            cfgword['boot_from_ifb'] = widget01t.ui.chbox_bootfrom_ifb.isChecked()
            cfgword['en_gpio'] = widget01t.ui.chbox_en_gpio.isChecked()
            cfgword['extmem_sel'] = widget01t.ui.combo_extmemsel.currentIndex()
            cfgword['pinnum'] = widget01t.ui.combo_pinnum.currentIndex()
            cfgword['portnum'] = widget01t.ui.combo_portnum.currentIndex() & 7
            cfgword['lock_ifb_lf'] = widget01t.ui.chbox_lock_ifb_lf.isChecked()
            cfgword['bfre'] = widget01t.ui.chbox_bfre.isChecked()
            cfgword['bfifbre'] = widget01t.ui.chbox_bfifbre.isChecked()
            cfgword['lock_ifb_uf'] = widget01t.ui.chbox_lock_ifb_uf.isChecked()
            cfgword['ufre'] = widget01t.ui.chbox_ufre.isChecked()
            cfgword['ufifbre'] = widget01t.ui.chbox_ufifbre.isChecked()
            cfgword['bflock'] = [1] * len(bflock)
            cfgword['uflock'] = [1] * len(uflock)
            for p in range(0, len(bflock)):
                cfgword['bflock'][p] = 1 if bflock[p].isChecked() else 0
            for p in range(0, len(uflock)):
                cfgword['uflock'][p] = 1 if uflock[p].isChecked() else 0
            return cfgword



# -- Standalone run -----------------------------------------------------------

def start_gui():
    logger.init(debug=True, logfile="flasher.log")
    app = QApplication(sys.argv)
    main_window = MyMainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    start_gui()
