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
import logger
import inspect
import serport
import mcu
import protocol
import traceback
import argparse


parser = argparse.ArgumentParser(description='K1921VKx Flasher Utility')
parser.add_argument(
    "--file",
    default="",
    help='(.bin) File for writing or reading'
)
parser.add_argument(
    "-c",
    "--cmd_mode",
    action='store_true',
    help='Enable cmd line mode.'
)
parser.add_argument(
    "-f",
    "--flash",
    choices=["bootflash", "userflash", "mflash", "bflash"],
    help='Select flash memory.'
)
parser.add_argument(
    "-n",
    "--flash_region",
    choices=["main", "nvr", "info"],
    help='Select flash memory region.'
)
parser.add_argument(
    "-e",
    "--erase",
    action='store_true',
    help='Erase (-L) count of pages from (-F) page'
)
parser.add_argument(
    "-E",
    "--full_erase",
    action='store_true',
    help='Full erase'
)

parser.add_argument(
    "-w",
    "--write",
    action='store_true',
    help='Write "file.bin" starting from (-F) page'
)
parser.add_argument(
    "-v",
    "--verfi",
    action='store_true',
    help='Verificate writed "file.bin", used with flag (-w)'
)
parser.add_argument(
    "-r",
    "--read",
    action='store_true',
    help='Read flash to "file.bin" starting from (-F) page'
)
parser.add_argument(
    "-j",
    "--jump_exe",
    type=lambda x: int(x,0),
    help='Jump to execute prog with global addr.'
)
parser.add_argument(
    "-F",
    "--first_page",
    type=lambda x: int(x,0),
    default=0,
    help='Num of first page.'
)
parser.add_argument(
    "-L",
    "--count_pages",
    type=int,
    help='Count pages.'
)

parser.add_argument(
    "-p",
    "--port",
    default="",
    help='COM port.'
)
parser.add_argument(
    "-b",
    "--baud",
    type=int,
    default=115200,
    help='Baudrate.'
)

args = parser.parse_args()

def cmd_exec(args):
    mcu_cur = mcu.get_by_name('k1921vkx')
    serport_cur = serport.SerPort()
    prot = protocol.Protocol(serport=serport_cur, win=None)
    flash_vars = {'bootflash': 0, 'userflash': 1, 'mflash': 0, 'bflash': 1}
    region_vars = {'main': 'region_main', 'nvr': 'region_nvr', 'info': 'region_nvr'}
    try:
        mcu_cur = prot.init(port=args.port, baud=args.baud)
    except:
        #print(" Сouldn't connect to the target")
        prot.deinit()
        raise Exception("Сouldn't connect to the target")
    if args.erase:
        pass
    if args.write:
        prot.write(filepath=args.file,
                   firstpage=args.first_page,
                   region=region_vars[args.flash_region],
                   flash=flash_vars[args.flash],
                   count_pages=args.count_pages,
                   ernone=not(args.full_erase or args.erase), 
                   erall=args.full_erase, 
                   erpages=args.erase,
                   verif=args.verfi,
                   jump=not(args.jump_exe is None),
                   jumpaddr=args.jump_exe)
    prot.deinit()

if __name__ == '__main__':
    if args.cmd_mode:
        cmd_exec(args)
    else:
        import k1921vkx_flasher_gui
        k1921vkx_flasher_gui.start_gui()
