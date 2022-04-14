# k1921vk_flasher tool
A Python-based, platform-independent utility to communicate with the bootloader in k1921vk chips.

# Install 
```
python setup.py install
```
# Usage
You can run tool by:
1. From repo folder
```
python k1921vkx_flasher.py
```
2. By entry_point
```
k1921vkx_flasher
```

```
usage: k1921vkx_flasher [-h] [--file FILE] [-c] [-f {bootflash,userflash,mflash,bflash}] [-n {main,nvr,info}] [-e] [-E] [-w] [-v] [-r] [-j JUMP_EXE] [-F FIRST_PAGE] [-L COUNT_PAGES] [-p PORT] [-b BAUD]

K1921VKx Flasher Utility

options:
  -h, --help            show this help message and exit
  --file FILE           (.bin) File for writing or reading
  -c, --cmd_mode        Enable cmd line mode.
  -f {bootflash,userflash,mflash,bflash}, --flash {bootflash,userflash,mflash,bflash}
                        Select flash memory.
  -n {main,nvr,info}, --flash_region {main,nvr,info}
                        Select flash memory region.
  -e, --erase           Erase (-L) count of pages from (-F) page
  -E, --full_erase      Full erase
  -w, --write           Write "file.bin" starting from (-F) page
  -v, --verfi           Verificate writed "file.bin", used with flag (-w)
  -r, --read            Read flash to "file.bin" starting from (-F) page
  -j JUMP_EXE, --jump_exe JUMP_EXE
                        Jump to execute prog with global addr.
  -F FIRST_PAGE, --first_page FIRST_PAGE
                        Num of first page.
  -L COUNT_PAGES, --count_pages COUNT_PAGES
                        Count pages.
  -p PORT, --port PORT  COM port.
  -b BAUD, --baud BAUD  Baudrate.
  ```
Note: Read cmd not implemented  
  
Example cmd for flash K1921VK035 by frimware.bin
```
k1921vkx_flasher -c -w -E -f mflash -n main -F 0x00000000 -p COM6 -b 460800 --file firmware.bin 
```



# Building app

Run cmd:
```
python setup.py build_app
```