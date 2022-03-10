#!/user/bin/env python
# coding:utf-8

import os
import time
import mcu


LogId = {
    "DEVICE": "@D: ",
    "HOST": "@H: ",
    "PROG": "",
}

SignCode = {
    "DEVICE": 0x7EA3,
    "HOST": 0x5C81,
}

CmdCode = {
    # Get commands
    "GET_INFO": 0x35,
    "GET_CFGWORD": 0x3A,
    # Set commands
    "SET_CFGWORD": 0x65,
    # Write commands
    "WRITE_PAGE": 0x9A,
    # Read commands
    "READ_PAGE": 0xA5,
    # Erase commands
    "ERASE_FULL": 0xC5,
    "ERASE_PAGE": 0xCA,
    # Misc
    "NONE": 0x00,
    "EXIT_BOOTLOADER": 0xF5,
    "MSG": 0xFA
}

MsgCode = {
    "NONE": 0,
    "ERR_CMD": 1,
    "ERR_CRC": 2,
    "READY": 3,
    "OK": 4,
    "FAIL": 5
}


# -- Misc functions -----------------------------------------------------------
def dict_key(mydict, dict_value):
    return list(mydict.keys())[list(mydict.values()).index(dict_value)]


# -- Classes ----------------------------------------------------------------
class ProtException(Exception):
    def __init__(self, msg, win=None):
        if win:
            win.log_err(msg)
        super().__init__(msg)


class Packet:
    def __init__(self, mcu, serport, win=None):
        self.mcu = mcu
        self.serport = serport
        self.win = win
        self.cmd_code = CmdCode["NONE"]
        self.data8_n = 0
        self.data = []
    
    
    def log_dbg(self, msg):
        if self.win:
            self.win.log_dbg(msg)
        else:
            print("DBG: %s" % msg)

    def log_info(self, msg):
        if self.win:
            self.win.log_info(msg)
        else:
            print("INFO: %s" % msg)

    def log_err(self, msg, msgbox_en=True):
        if self.win:
            self.win.log_err(msg, msgbox_en)
        else:
            print("ERR: %s" % msg)

    def crc16(self, data_in, crc_in=0):
        '''crc16 byte by byte'''
        crc = crc_in & 0xFFFF
        data = (data_in & 0xFF) | 0x100

        while not (data & 0x10000):
            crc <<= 1
            data <<= 1
            if (data & 0x100):
                crc += 1
            if (crc & 0x10000):
                crc ^= 0x1021

        return crc & 0xFFFF

    def chunks(self, l, n):
        return [l[i:i + n] for i in range(0, len(l), n)]


class TxPacket(Packet):
    def __init__(self, mcu, serport, win=None):
        super().__init__(mcu, serport, win)
        self.host_sign = SignCode["HOST"]

    def transmit(self):
        packet_bytes = []
        packet_bytes += [(self.host_sign >> 0) & 0xFF]
        packet_bytes += [(self.host_sign >> 8) & 0xFF]

        packet_bytes += [(self.cmd_code >> 0) & 0xFF]
        crc = self.crc16(self.cmd_code)

        packet_bytes += [(~self.cmd_code >> 0) & 0xFF]
        crc = self.crc16(~self.cmd_code, crc)

        packet_bytes += [(self.data8_n >> 0) & 0xFF]
        packet_bytes += [(self.data8_n >> 8) & 0xFF]
        crc = self.crc16((self.data8_n >> 0) & 0xFF, crc)
        crc = self.crc16((self.data8_n >> 8) & 0xFF, crc)

        for i in range(0, self.data8_n):
            packet_bytes += [(self.data[i] >> 0) & 0xFF]
            crc = self.crc16(self.data[i], crc)

        self.log_dbg("data8_n: %d" % self.data8_n)
        self.log_dbg("crc: 0x%04x" % crc)
        packet_bytes += [(crc >> 0) & 0xFF]
        packet_bytes += [(crc >> 8) & 0xFF]

        self.serport.write_bytes(packet_bytes)


class RxPacket(Packet):
    def __init__(self, mcu, serport, win=None,cur_flash=0,cur_region='region_main'):
        super().__init__(mcu, serport, win)
        self.device_sign = SignCode["DEVICE"]
        self.rxcmd_code = CmdCode["NONE"]
        self.msg_code = MsgCode["NONE"]
        self.cur_flash = cur_flash
        self.cur_region = cur_region

    def msg_err_crc(self):
        self.log_dbg(LogId["DEVICE"] + "%s - ERR_CRC - CRC error in HOST command!" % dict_key(CmdCode, self.rxcmd_code))
        raise ProtException("ERR_CRC - CRC error in HOST command!", self.win)

    def parse_msg(self):
        flash_page_size = self.mcu.flash[self.cur_flash][self.cur_region].page_size
        info = {}
        self.msg_code = self.data[0]
        self.rxcmd_code = self.data[1]
        info['cmd_code'] = self.rxcmd_code
        info['msg_code'] = self.msg_code

        if (self.rxcmd_code == CmdCode["NONE"]):
            if (self.msg_code == MsgCode["ERR_CMD"]):
                self.log_dbg(LogId["DEVICE"] + "ERR_CMD - wrong command from HOST!")
                raise ProtException("ERR_CMD - wrong command from HOST!", self.win)
            elif (self.msg_code == MsgCode["READY"]):
                result = "Device ask ready"
                self.log_info(LogId["PROG"] + "%s" % result)
                self.log_dbg(LogId["DEVICE"] + "READY - %s" % result)

        elif (self.rxcmd_code == CmdCode["GET_INFO"]):
            if (self.msg_code == MsgCode["ERR_CRC"]):
                self.msg_err_crc()
            elif (self.msg_code == MsgCode["OK"]):
                chipid = (self.data[4] << 0) | (self.data[5] << 8) | (self.data[6] << 16) | (self.data[7] << 24)
                cpuid = (self.data[8] << 0) | (self.data[9] << 8) | (self.data[10] << 16) | (self.data[11] << 24)
                bootver = (self.data[12] << 0) | (self.data[13] << 8) | (self.data[14] << 16) | (self.data[15] << 24)
                result = ("SIU.CHIPID=[0x%08x] SCB.CPUID=[0x%08x] BOOTVER=[0x%08x]" %
                          (chipid, cpuid, bootver))

                info['chipid'] = "0x%08X" % chipid
                info['cpuid'] = "0x%08X" % cpuid
                info['bootver'] = "%d.%d" % ((bootver & 0xFFFF0000) >> 16, (bootver & 0x0000FFFF) >> 0)
                self.log_info(LogId["PROG"] + result)
                self.log_dbg(LogId["DEVICE"] + "GET_INFO - OK | %s" % result)

        elif (self.rxcmd_code == CmdCode["GET_CFGWORD"]):
            if (self.msg_code == MsgCode["ERR_CRC"]):
                self.msg_err_crc()
            elif (self.msg_code == MsgCode["OK"]):
                info.update(self.mcu.parse_cfgword(self.data[4:]))
                self.log_info(LogId["PROG"] + "%s" % info["res_str"])
                self.log_dbg(LogId["DEVICE"] + "GET_CFGWORD - OK | %s" % info["res_str"])
            elif (self.msg_code == MsgCode["FAIL"]):
                    raise ProtException("Device return error msg!", self.win)

        elif (self.rxcmd_code == CmdCode["SET_CFGWORD"]):
            if (self.msg_code == MsgCode["ERR_CRC"]):
                self.msg_err_crc()
            elif (self.msg_code == MsgCode["OK"]):
                info.update(self.mcu.parse_cfgword(self.data[4:]))
                self.log_dbg(LogId["DEVICE"] + "SET_CFGWORD - OK | %s" % info["res_str"])
            elif (self.msg_code == MsgCode["FAIL"]):
                    raise ProtException("Device return error msg!", self.win)

        elif (self.rxcmd_code == CmdCode["WRITE_PAGE"]):
            if (self.msg_code == MsgCode["ERR_CRC"]):
                self.msg_err_crc()
            elif (self.msg_code == MsgCode["OK"] or self.msg_code == MsgCode["FAIL"]):
                temp = (self.data[4] << 0) | (self.data[5] << 8) | (self.data[6] << 16) | (self.data[7] << 24)
                self.log_dbg(LogId["DEVICE"] + "WRITE_PAGE - %s | NVR=[%01d] FLASH=[%01d] ERASE=[%01d] ADDR=[0x%08x] PAGE=[%0d]" %
                             (dict_key(MsgCode, self.msg_code),
                             ((temp >> 31) & 0x1), ((temp >> 29) & 0x1), ((temp >> 30) & 0x1), (temp & 0x3FFFFFFF), (temp & 0x3FFFFFFF) // flash_page_size))
                if (self.msg_code == MsgCode["FAIL"]):
                    raise ProtException("Device return error msg!", self.win)

        elif (self.rxcmd_code == CmdCode["READ_PAGE"]):
            if (self.msg_code == MsgCode["ERR_CRC"]):
                self.msg_err_crc()
            elif (self.msg_code == MsgCode["OK"] or self.msg_code == MsgCode["FAIL"]):
                temp = (self.data[4] << 0) | (self.data[5] << 8) | (self.data[6] << 16) | (self.data[7] << 24)
                info['data'] = self.data[8:]
                self.log_dbg(LogId["DEVICE"] + "READ_PAGE - %s | NVR=[%01d] FLASH=[%01d] ADDR=[0x%08x] PAGE=[%0d]" %
                             (dict_key(MsgCode, self.msg_code),
                             ((temp >> 31) & 0x1), ((temp >> 29) & 0x1), (temp & 0x7FFFFFFF), (temp & 0x7FFFFFFF) // flash_page_size))
                if (self.msg_code == MsgCode["FAIL"]):
                    raise ProtException("Device return error msg!", self.win)

        elif (self.rxcmd_code == CmdCode["ERASE_FULL"]):
            if (self.msg_code == MsgCode["ERR_CRC"]):
                self.msg_err_crc()
            elif (self.msg_code == MsgCode["OK"] or self.msg_code == MsgCode["FAIL"]):
                temp = (self.data[4] << 0) | (self.data[5] << 8) | (self.data[6] << 16) | (self.data[7] << 24)
                self.log_dbg(LogId["DEVICE"] + "ERASE_FULL - %s | NVR=[%01d] FLASH=[%01d]" % (dict_key(MsgCode, self.msg_code), ((temp >> 31) & 0x1), ((temp >> 29) & 0x1)))
                if (self.msg_code == MsgCode["FAIL"]):
                    raise ProtException("Device return error msg!", self.win)

        elif (self.rxcmd_code == CmdCode["ERASE_PAGE"]):
            if (self.msg_code == MsgCode["ERR_CRC"]):
                self.msg_err_crc()
            elif (self.msg_code == MsgCode["OK"] or self.msg_code == MsgCode["FAIL"]):
                temp = (self.data[4] << 0) | (self.data[5] << 8) | (self.data[6] << 16) | (self.data[7] << 24)
                self.log_dbg(LogId["DEVICE"] + "ERASE_PAGE - %s | NVR=[%01d] FLASH=[%01d] ADDR=[0x%08x] PAGE=[%0d]" %
                             (dict_key(MsgCode, self.msg_code),
                             ((temp >> 31) & 0x1), ((temp >> 29) & 0x1), (temp & 0x7FFFFFFF), (temp & 0x7FFFFFFF) // flash_page_size))
                if (self.msg_code == MsgCode["FAIL"]):
                    raise ProtException("Device return error msg!", self.win)

        elif (self.rxcmd_code == CmdCode["EXIT_BOOTLOADER"]):
            if (self.msg_code == MsgCode["ERR_CRC"]):
                self.msg_err_crc()
            elif (self.msg_code == MsgCode["OK"]):
                self.log_dbg(LogId["DEVICE"] + "EXIT_BOOTLOADER - OK")

        n = 0
        for chunk in self.chunks(self.data, 4):
            temp_str = "0x%02x:" % n
            for b in chunk:
                temp_str += ' %02x' % b
                n += 1
            self.log_dbg(temp_str)
            if n > 63:
                self.log_dbg('More than 64 bytes of data, the rest are not printed')
                break

        return info

    def receive(self):
        # device signature detection
        rx_sign = 0
        while (rx_sign != self.device_sign):
            temp = self.serport.read_int()
            rx_sign = (rx_sign >> 8) | (temp << 8)
        # read special data
        rx_cmd = self.serport.read_int()
        rx_cmd_inv = self.serport.read_int()
        rx_data_n = self.serport.read_int(2)
        # check command
        if ((rx_cmd ^ rx_cmd_inv) != 0xFF):
            self.log_dbg(LogId["HOST"] + "MSG_CMD - ERR_CMD - wrong command from DEVICE!")
            raise ProtException("Wrong command received!", self.win)
        # start data load and crc16 calculation
        crc = self.crc16(rx_cmd)
        crc = self.crc16(rx_cmd_inv, crc)
        crc = self.crc16((rx_data_n >> 0) & 0xFF, crc)
        crc = self.crc16((rx_data_n >> 8) & 0xFF, crc)
        for i in range(0, rx_data_n):
            self.data += [self.serport.read_int()]
            crc = self.crc16(self.data[i], crc)
        rx_crc = self.serport.read_int(2)
        # check crc
        if (rx_crc == crc):
            self.cmd_code = rx_cmd
            self.data8_n = rx_data_n
            if (self.cmd_code == CmdCode["MSG"]):
                    return self.parse_msg()
            else:
                self.log_dbg(LogId["HOST"] + "Error! Waiting for MSG but recieve %s command" % dict_key(CmdCode, self.cmd_code))
                raise ProtException("Wrong command received!", self.win)
        else:
            self.log_dbg(LogId["HOST"] + "MSG - ERR_CRC - CRC error in DEVICE command!")
            raise ProtException("CRC error in device message!", self.win)


class CmdInterface:
    def __init__(self, mcu, serport, win=None,cur_flash=0,cur_region="region_main"):
        self.mcu = mcu
        self.serport = serport
        self.win = win
        self.cur_flash = cur_flash
        self.cur_region = cur_region
    def log_dbg(self, msg):
        if self.win:
            self.win.log_dbg(msg)
        else:
            print("DBG: %s" % msg)

    def log_info(self, msg):
        if self.win:
            self.win.log_info(msg)
        else:
            print(u"INFO: %s" % msg)

    def log_err(self, msg, msgbox_en=True):
        if self.win:
            self.win.log_err(msg, msgbox_en)
        else:
            print("ERR: %s" % msg)

    def reset_chip(self):
        self.log_info(LogId["PROG"] + "Reset mcu ...")
        time.sleep(0.1)
        self.serport.dtr = True
        time.sleep(0.3)
        self.serport.dtr = False
        time.sleep(0.1)

    def init_device(self):
        self.log_info(LogId["PROG"] + "Connecting ro target ...")
        # try RTS active 1
        self.log_info(LogId["PROG"] + "Activate loader: variant 1 ....")
        self.serport.reset_input_buffer()
        self.serport.rts = False
        self.reset_chip()
        self.serport.write_bytes([0x7F])
        ack = self.serport.read_int(2)
        self.log_info(LogId["DEVICE"] + "ack = 0x%04X" % ack)
        if (ack == ((((SignCode["DEVICE"]) >> 8) & 0x00FF) | (((SignCode["DEVICE"]) << 8) & 0xFF00))):
            self.log_info(LogId["PROG"] + "Device connected")
        else:
            # try RTS active 0
            self.log_info(LogId["PROG"] + "Activate loader: variant 2 ....")
            self.serport.reset_input_buffer()
            self.serport.rts = True
            self.reset_chip()
            self.serport.write_bytes([0x7F])
            ack = self.serport.read_int(2)
            self.log_info(LogId["DEVICE"] + "ack = 0x%04X" % ack)
            if (ack == ((((SignCode["DEVICE"]) >> 8) & 0x00FF) | (((SignCode["DEVICE"]) << 8) & 0xFF00))):
                 self.log_info(LogId["PROG"] + "Device connected")
            else:
                raise ProtException("Unknown response from the device", self.win)
        self.serport.rts = not self.serport.rts
        rx_info = self.cmd_msg()
        if ((rx_info['cmd_code'] != CmdCode["NONE"]) or (rx_info['msg_code'] != MsgCode["READY"])):
            raise ProtException("Unknown READY response from the device", self.win)

    def release_device(self):
        self.log_info(LogId["PROG"] + "Disconnecting from target ...")
        self.serport.rts = not self.mcu.booten_active
        self.reset_chip()

    def cmd_get_info(self):
        self.log_info(LogId["PROG"] + "Reading mcu info ...")
        packet = TxPacket(self.mcu, self.serport, self.win)
        packet.cmd_code = CmdCode["GET_INFO"]
        packet.data8_n = 0
        self.log_dbg(LogId["HOST"] + "GET_INFO")
        packet.transmit()
        return self.cmd_msg()

    def cmd_get_cfgword(self):
        self.log_info(LogId["PROG"] + "Reading CFGWORD ...")
        packet = TxPacket(self.mcu, self.serport, self.win)
        packet.cmd_code = CmdCode["GET_CFGWORD"]
        packet.data8_n = 0
        self.log_dbg(LogId["HOST"] + "GET_CFGWORD")
        packet.transmit()
        return self.cmd_msg()

    def cmd_set_cfgword(self, cfgword):
        self.log_info(LogId["PROG"] + "Writing CFGWORD ...")
        packet = TxPacket(self.mcu, self.serport, self.win)
        data, dbg_str = self.mcu.pack_cfgword(cfgword)
        packet.cmd_code = CmdCode["SET_CFGWORD"]
        packet.data += data
        packet.data8_n = len(data)
        temp_str = "data (%d): " % len(packet.data)
        for b in packet.data:
            temp_str += "0x%x " % b
        self.log_dbg(temp_str)
        self.log_dbg("data8_n: %d" % packet.data8_n)
        self.log_dbg(LogId["HOST"] + "%s" % dbg_str)
        packet.transmit()
        self.cmd_msg()

    def cmd_erase_page(self, page, flash, region):
        self.log_info(LogId["PROG"] + "Erasing page: %d ..." % page)
        page_size = self.mcu.flash[flash][region].page_size
        addr = page * page_size
        packet = TxPacket(self.mcu, self.serport, self.win)
        packet.cmd_code = CmdCode["ERASE_PAGE"]
        packet.data8_n = 4
        packet.data += [(addr >> 0) & 0xFF]
        packet.data += [(addr >> 8) & 0xFF]
        packet.data += [(addr >> 16) & 0xFF]
        nvr = 1 if 'nvr' in region else 0
        packet.data += [((nvr << 7) | (flash << 5)) & 0xFF]
        self.log_dbg(LogId["HOST"] + "ERASE_PAGE - NVR=[%01d] FLASH=[%01d] ADDR=[0x%08x] PAGE=[%0d]" %
                     (nvr, flash, addr, page))
        packet.transmit()

    def cmd_erase_full(self, flash, region):
        self.log_info(LogId["PROG"] + "Full erasing ...")
        packet = TxPacket(self.mcu, self.serport, self.win)
        packet.cmd_code = CmdCode["ERASE_FULL"]
        packet.data8_n = 4
        packet.data += [(0 >> 0) & 0xFF]
        packet.data += [(0 >> 8) & 0xFF]
        packet.data += [(0 >> 16) & 0xFF]
        nvr = 1 if 'nvr' in region else 0
        packet.data += [((nvr << 7) | (flash << 5)) & 0xFF]
        self.log_dbg(LogId["HOST"] + "ERASE_FULL - NVR=[%01d] FLASH=[%01d]" % (nvr, flash))
        packet.transmit()

    def cmd_write_page(self, page, page_data, flash, region, erpages):
        self.log_info(LogId["PROG"] + "Write page: %d ..." % page)
        page_size = self.mcu.flash[flash][region].page_size
        addr = page * page_size
        packet = TxPacket(self.mcu, self.serport, self.win)
        packet.cmd_code = CmdCode["WRITE_PAGE"]
        packet.data8_n = page_size + 4
        packet.data += [(addr >> 0) & 0xFF]
        packet.data += [(addr >> 8) & 0xFF]
        packet.data += [(addr >> 16) & 0xFF]
        nvr = 1 if 'nvr' in region else 0
        erase = 1 if erpages else 0
        packet.data += [((nvr << 7) | (erase << 6) | (flash << 5)) & 0xFF]
        packet.data += page_data
        self.log_dbg(LogId["HOST"] + "WRITE_PAGE - NVR=[%01d] FLASH=[%01d] ERASE=[%01d] ADDR=[0x%08x] PAGE=[%0d]" %
                     (nvr, flash, erase, addr, page))
        packet.transmit()

    def cmd_read_page(self, page, flash, region):
        self.log_info(LogId["PROG"] + "Read page: %d ..." % page)
        addr = page * self.mcu.flash[flash][region].page_size
        packet = TxPacket(self.mcu, self.serport, self.win)
        packet.flash_page_size = self.mcu.flash[flash][region].page_size
        packet.cmd_code = CmdCode["READ_PAGE"]
        packet.data8_n = 4
        packet.data += [(addr >> 0) & 0xFF]
        packet.data += [(addr >> 8) & 0xFF]
        packet.data += [(addr >> 16) & 0xFF]
        nvr = 1 if 'nvr' in region else 0
        packet.data += [((nvr << 7) | (flash << 5)) & 0xFF]
        self.log_dbg(LogId["HOST"] + "READ_PAGE - NVR=[%01d] FLASH=[%01d] ADDR=[0x%08x] PAGE=[%0d]" %
                     (nvr, flash, addr, page))
        packet.transmit()

    def cmd_exit_bootloader(self):
        self.log_info(LogId["PROG"] + "Software reset and exit from bootloader")
        packet = TxPacket(self.mcu, self.serport, self.win)
        packet.cmd_code = CmdCode["EXIT_BOOTLOADER"]
        packet.data8_n = 0
        self.log_dbg(LogId["HOST"] + "EXIT_BOOTLOADER")
        packet.transmit()

    def cmd_msg(self):
        packet = RxPacket(self.mcu, self.serport, self.win,cur_flash=self.cur_flash,cur_region=self.cur_region)
        return packet.receive()


class Protocol:
    def __init__(self, serport, win=None):
        self.mcu = mcu.get_by_name('k1921vkx')
        self.serport = serport
        self.win = win
        self.cur_flash = 0
        self.cur_region = "region_main"
    def pbar_set(self, state):
        if self.win:
            self.win.pbar_set(state)
    # -- Helpers --
    def log_dbg(self, msg):
        if self.win:
            self.win.log_dbg(msg)
        else:
            print("DBG: %s" % msg)

    def log_info(self, msg):
        if self.win:
            self.win.log_info(msg)
        else:
            print("INFO: %s" % msg)

    def log_err(self, msg, msgbox_en=True):
        if self.win:
            self.win.log_err(msg, msgbox_en)
        else:
            print("ERR: %s" % msg)

    def save_bin(self, name, data):
        self.log_info("Saving %0d data bytes to file %s" % (len(data), name))
        binfile = open(name, "wb")
        binfile.write(bytes(data))
        binfile.close()

    def open_bin(self, name):
        binfile = open(name, "rb")
        data = []
        while True:
            current_byte = binfile.read(1)
            if (not current_byte):
                break
            data += [ord(current_byte)]
        binfile.close()
        self.log_dbg("Readed %0d data bytes from file %s" % (len(data), name))
        return data

    # -- API --
    def init(self, **kwargs):
        #self.log_dbg("%s->%s()" % (os.path.basename(__file__), self.win.whoami()))
        #self.log_dbg(kwargs)
        cmd = CmdInterface(mcu=self.mcu, serport=self.serport, win=self.win,cur_flash=self.cur_flash,cur_region=self.cur_region)
        try:
            self.serport.open_port(port=kwargs['port'], baudrate=kwargs['baud'])
        except:
            raise ProtException("Couldn't open port %s"%(kwargs['port']), self.win)
        self.serport.reset_input_buffer()
        self.pbar_set(25)
        cmd.init_device()
        self.pbar_set(50)
        mcu_info = cmd.cmd_get_info()
        inited_mcu = mcu.get_by_chipid(mcu_info["chipid"])
        if inited_mcu is None:
            raise ProtException("Unknown CHIPID!", self.win)
        else:
            self.mcu = inited_mcu
            cmd.mcu = self.mcu
        self.pbar_set(75)
        mcu_cfgword = cmd.cmd_get_cfgword()
        self.mcu.apply_cfgword(mcu_cfgword)
        self.mcu.cpuid = mcu_info['cpuid']
        self.mcu.bootver = mcu_info['bootver']
        self.log_info("Detected %s with bootloader v%s" % (self.mcu.name_ru, self.mcu.bootver))
        self.pbar_set(100)
        return self.mcu

    def deinit(self, **kwargs):
        #self.log_dbg("%s->%s()" % (os.path.basename(__file__), self.win.whoami()))
        #self.log_dbg(kwargs)
        cmd = CmdInterface(mcu=self.mcu, serport=self.serport, win=self.win,cur_flash=self.cur_flash,cur_region=self.cur_region)
        if self.win:
            self.pbar_set(50)
        cmd.release_device()
        #self.serport.close_port()
        self.log_info("Disconnect from target")
        if self.win:
            self.pbar_set(100)
        return True

    def write(self, **kwargs):
        self.serport.reset_input_buffer()
        #self.log_dbg("%s->%s()" % (os.path.basename(__file__), self.win.whoami()))
        #self.log_dbg(kwargs)

        if "region" in kwargs:
            self.cur_region = kwargs["region"]
        else:
            self.cur_region = self.win.get_curr_region()
        if "flash" in kwargs:
            self.cur_flash = kwargs["flash"]
        else:
            self.cur_flash = self.win.get_curr_flash()

        cmd = CmdInterface(mcu=self.mcu, serport=self.serport, win=self.win,cur_flash=self.cur_flash,cur_region=self.cur_region)
        
            
        region = self.cur_region
        flash = self.cur_flash
        page_size = self.mcu.flash[flash][region].page_size
        if kwargs['count_pages'] is None:
            filesize = os.path.getsize(kwargs['filepath'])
            pages_total = self.mcu.flash[flash][region].pages
            addr = kwargs['firstpage'] * page_size
            if filesize > ((page_size * pages_total) - addr):
                raise ProtException("Filesize more then mcu flash size!", self.win)
            count_pages = ((filesize // page_size) + (1 if filesize % page_size else 0))
        else:
            count_pages = kwargs['count_pages']

        lastpage = kwargs['firstpage'] + count_pages - 1
        raw_data = self.open_bin(kwargs['filepath'])
        self.log_info("Completing a binary file to the size of an entire page...")
        data = [0xFF] * (lastpage - kwargs['firstpage'] + 1) * page_size
        for i in range(0, len(raw_data)):
            data[i] = raw_data[i]
        state = 0.0
        self.pbar_set(state)

        cmd_count = 0
        if (kwargs['erall']):
            cmd.cmd_erase_full(flash, region)
            cmd_count += 1
        state += 20.0
        self.pbar_set(state)

        self.log_info("Write pages %s:" % (" with pre-erasing" if kwargs['erpages'] else ""))
        for p in range(0, lastpage - kwargs['firstpage'] + 1):
            cmd.cmd_write_page(kwargs['firstpage'] + p, data[p * page_size:p * page_size + page_size], flash, region, kwargs['erpages'])
            state += 15 / (lastpage- kwargs['firstpage'] + 1)
            self.pbar_set(state)
            cmd_count += 1

        self.log_info("Waiting for completing commands ...")
        for i in range(0, cmd_count):
            cmd.cmd_msg()
            state += 20 / cmd_count
            self.pbar_set(state)

        if (kwargs["verif"]):
            self.log_info("Verification ...")
            # read pages
            read_data = []
            for p in range(kwargs['firstpage'], lastpage+ 1):
                cmd.cmd_read_page(p, flash, region)
                state += 15 / (lastpage- kwargs['firstpage'] + 1)
                self.pbar_set(state)
            self.log_info("Waiting for completing commands ...")
            for p in range(kwargs['firstpage'], lastpage+ 1):
                read_data += cmd.cmd_msg()['data']
                state += 20 / (lastpage- kwargs['firstpage'] + 1)
                self.pbar_set(state)
            # compare
            err = 0
            err_limit = 16
            for i in range(0, len(read_data)):
                if (read_data[i] != data[i]):
                    err += 1
                    if err_limit > 0:
                        self.log_err("Addr 0%08X, writed 0x%02X, but readed 0x%02X" % (i, data[i], read_data[i]), msgbox_en=False)
                        err_limit -= 1
                        if err_limit == 0:
                            self.log_err("Only the first 16 verification errors are shown.")
            self.log_info("Verification completed, number of errors: %0d" % err)
        self.pbar_set(100)

    def erase(self, **kwargs):
        self.serport.reset_input_buffer()
        #self.log_dbg("%s->%s()" % (os.path.basename(__file__), self.win.whoami()))
        #self.log_dbg(kwargs)
        if "region" in kwargs:
            self.cur_region = kwargs["region"]
        else:
            self.cur_region = self.win.get_curr_region()
        if "flash" in kwargs:
            self.cur_flash = kwargs["flash"]
        else:
            self.cur_flash = self.win.get_curr_flash()
        cmd = CmdInterface(mcu=self.mcu, serport=self.serport, win=self.win,cur_flash=self.cur_flash,cur_region=self.cur_region)
        region = self.cur_region
        flash = self.cur_flash

        cmd_count = 0
        state = 0.0
        self.pbar_set(state)
        if (kwargs['erall']):
            self.pbar_set(50)
            cmd.cmd_erase_full(flash, region)
            cmd.cmd_msg()
        else:
            for p in range(kwargs['firstpage'], lastpage + 1):
                cmd.cmd_erase_page(p, flash, region)
                state += 50 / (lastpage - kwargs['firstpage'] + 1)
                self.pbar_set(state)
                cmd_count += 1
            self.log_info("Ожидание выполнения команд ...")
            for i in range(0, cmd_count):
                cmd.cmd_msg()
                state += 50 / cmd_count
                self.pbar_set(state)
        self.pbar_set(100)

    def read(self, **kwargs):
        self.serport.reset_input_buffer()
        #self.log_dbg("%s->%s()" % (os.path.basename(__file__), self.win.whoami()))
        #self.log_dbg(kwargs)
        if "region" in kwargs:
            self.cur_region = kwargs["region"]
        else:
            self.cur_region = self.win.get_curr_region()
        if "flash" in kwargs:
            self.cur_flash = kwargs["flash"]
        else:
            self.cur_flash = self.win.get_curr_flash()

        cmd = CmdInterface(mcu=self.mcu, serport=self.serport, win=self.win,cur_flash=self.cur_flash,cur_region=self.cur_region)
        region = self.cur_region
        flash = self.cur_flash

        page_data = []
        state = 10.0
        self.pbar_set(state)
        for page in range(kwargs['firstpage'], lastpage + 1):
            cmd.cmd_read_page(page, flash, region)
            state += 40 / (lastpage - kwargs['firstpage'] + 1)
            self.pbar_set(state)
        self.log_info("Ожидание выполнения команд ...")
        for page in range(kwargs['firstpage'], lastpage + 1):
            page_data += cmd.cmd_msg()['data']
            state += 40 / (lastpage - kwargs['firstpage'] + 1)
            self.pbar_set(state)
        self.save_bin(kwargs['filepath'], page_data)
        self.pbar_set(100)

    def get_cfgword(self, **kwargs):
        self.serport.reset_input_buffer()
        #self.log_dbg("%s->%s()" % (os.path.basename(__file__), self.win.whoami()))
        #self.log_dbg(kwargs)
        cmd = CmdInterface(mcu=self.mcu, serport=self.serport, win=self.win,cur_flash=self.cur_flash,cur_region=self.cur_region)
        self.pbar_set(50)
        cfgword = cmd.cmd_get_cfgword()
        self.pbar_set(100)
        return cfgword

    def set_cfgword(self, **kwargs):
        self.serport.reset_input_buffer()
        #self.log_dbg("%s->%s()" % (os.path.basename(__file__), self.win.whoami()))
        #self.log_dbg(kwargs)
        cmd = CmdInterface(mcu=self.mcu, serport=self.serport, win=self.win,cur_flash=self.cur_flash,cur_region=self.cur_region)
        self.pbar_set(50)
        cmd.cmd_set_cfgword(kwargs['cfgword'])
        self.pbar_set(100)
