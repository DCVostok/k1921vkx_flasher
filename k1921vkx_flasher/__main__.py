#!/usr/bin/env python
# coding:utf-8

"""
K1921VKx Flasher Utility
"""

# -- Imports ------------------------------------------------------------------
import k1921vkx_flasher
import k1921vkx_flasher.serport as serport
import k1921vkx_flasher.mcu as mcu
import k1921vkx_flasher.protocol as protocol
import argparse

def print_version():
    print(k1921vkx_flasher.__version__)

def cmd_exec(args):
    serport_cur = serport.SerPort()
    prot = protocol.Protocol(serport=serport_cur,debug_log=False, win=None)
    flash_vars = {'bootflash': 0, 'userflash': 1, 'mflash': 0, 'bflash': 1}
    region_vars = {'main': 'region_main',
                   'nvr': 'region_nvr', 'info': 'region_nvr'}
    
    
    try:
        mcu_cur = prot.init(port=args.port, baud=args.baud)
    except:
        #print(" Сouldn't connect to the target")
        prot.deinit()
        raise Exception("Сouldn't connect to the target")
    
    try:

             
        if args.write:
            try:
                    prot.write(filepath=args.file,
                               firstpage=args.first_page,
                               region=region_vars[args.flash_region],
                               flash=flash_vars[args.flash],
                               count_pages=args.count_pages,
                               ernone=not(args.full_erase or args.erase),
                               erall=args.full_erase,
                               erpages=args.erase,
                               verif=args.verfi)
            except:
                raise Exception("Writing programm error.")
        elif args.read:
            try:
                    prot.read(filepath=args.file,
                               firstpage=args.first_page,
                               region=region_vars[args.flash_region],
                               flash=flash_vars[args.flash],
                               count_pages=args.count_pages,
                               verif=args.verfi)
            except:
                raise Exception("Reading programm error.")
        elif args.erase or args.full_erase:
            try:
                    prot.erase(filepath=args.file,
                               firstpage=args.first_page,
                               region=region_vars[args.flash_region],
                               flash=flash_vars[args.flash],
                               count_pages=args.count_pages,
                               erall=args.full_erase,
                               erpages=args.erase,
                               verif=args.verfi)
            except:
                raise Exception("Erase programm error.")
        #Setting cfgword after another operations
        if args.set_cfgword:
            try:
                prot.set_cfgword(cfgword=args.set_cfgword)
            except:
                raise Exception("Setting cfgword error.")
    finally:
        prot.deinit()

class StoreDictKeyPair(argparse.Action):
     def __call__(self, parser, namespace, values, option_string=None):
         my_dict = {}
         for kv in values.split(","):
             k,v = kv.split("=")
             my_dict[k.lower()] = v
         setattr(namespace, self.dest, my_dict)




def main():
    parser = argparse.ArgumentParser(description='K1921VKx Flasher Utility')
    parser.add_argument(
        "--version",
        action='store_true',
        help='Print version'
    )
    parser.add_argument("--set_cfgword", 
                        action=StoreDictKeyPair, 
                        metavar="KEY1=VAL1,KEY2=VAL2...",
                        help='Setting cfgword after all another operations')

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
        default="mflash",
        choices=["bootflash", "userflash", "mflash", "bflash"],
        help='Select flash memory. (default: %(default)s)'
    )
    parser.add_argument(
        "-n",
        "--flash_region",
        default="main",
        choices=["main", "nvr", "info"],
        help='Select flash memory region. (default: %(default)s)'
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
    # parser.add_argument(
    #     "-j",
    #     "--jump_exe",
    #     type=lambda x: int(x, 0),
    #     help='Jump to execute prog with global addr.'
    # )
    parser.add_argument(
        "-F",
        "--first_page",
        type=lambda x: int(x, 0),
        default=0,
        help='Num of first page. (default: %(default)s)'
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
        help='Baudrate. (default: %(default)s)'
    )


    args = parser.parse_args()
    if args.version:
        print_version()
        return 0
    if args.cmd_mode:
        cmd_exec(args)
    else:
        import k1921vkx_flasher.k1921vkx_flasher_gui
        k1921vkx_flasher.k1921vkx_flasher_gui.start_gui()


if __name__ == '__main__':
    main()
