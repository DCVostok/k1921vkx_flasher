#!/user/bin/env python
# coding:utf-8

import sys
import glob
import serial


class SerPort(serial.Serial):
    def __init__(self, win=None):
        self.win = win
        super().__init__()

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

    def log_err(self, msg):
        if self.win:
            self.win.log_err(msg)
        else:
            print("ERR: %s" % msg)

    def open_port(self, port='/dev/ttyUSB0', baudrate=115200, quiet=False):
        if self.is_open:
            self.close()
        self.port = port
        self.baudrate = baudrate
        self.timeout = 0.3
        self.dtr = False
        self.rts = False
        if not quiet:
            self.log_info("Try open port %s %s" % (port, baudrate))
        self.open()

    def close_port(self, quiet=False):
        if not quiet:
            self.log_info("COM port closed")
        self.close()

    def write_bytes(self, blist):
        self.write(bytes(blist))

    def read_int(self, size=1):
        bytes_str = self.read(size)
        return int.from_bytes(bytes_str, byteorder='little')

    # https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
    def list_ports(self):
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            self.log_err("Невозможно открыть порты - неподдерживаемая платформа")
            raise EnvironmentError('Unsupported platform')

        result = []
        self.log_dbg(ports)
        for port in ports:
            try:
                s = serial.Serial(port, baudrate=115200)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        self.log_dbg(result)
        return result


if __name__ == '__main__':
    serport = SerPort()
    serport.list_ports()
