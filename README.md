# k1921vk flasher tool
[![PlatformIO Registry](https://badges.registry.platformio.org/packages/dcvostok/tool/tool-k1921vkx-flasher.svg)](https://registry.platformio.org/tools/dcvostok/tool-k1921vkx-flasher)  
A Python-based, platform-independent utility to communicate with the bootloader in k1921vk chips.

# Install 

With GUI:
```
pip install "k1921vkx_flasher[GUI] @ git+https://github.com/DCVostok/k1921vkx_flasher.git"
```

Without GUI:
```
pip install "k1921vkx_flasher @ git+https://github.com/DCVostok/k1921vkx_flasher.git"
```

To use this tool without GUI, you need to pass `--cmd_mode` when running commands.

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
3. As Python module
```
python -m k1921vkx_flasher
```

```
usage: k1921vkx_flasher.py [-h] [--version] [--set_cfgword KEY1=VAL1,KEY2=VAL2...] [--file FILE] [-c] [-f {bootflash,userflash,mflash,bflash}] [-n {main,nvr,info}] [-e] [-E] [-w] [-v] [-r] [-F FIRST_PAGE] [-L COUNT_PAGES]
                           [-p PORT] [-b BAUD]

K1921VKx Flasher Utility

options:
  -h, --help            show this help message and exit
  --version             Print version
  --set_cfgword KEY1=VAL1,KEY2=VAL2...
                        Setting cfgword after all another operations
  --file FILE           (.bin) File for writing or reading
  -c, --cmd_mode        Enable cmd line mode.
  -f {bootflash,userflash,mflash,bflash}, --flash {bootflash,userflash,mflash,bflash}
                        Select flash memory. (default: mflash)
  -n {main,nvr,info}, --flash_region {main,nvr,info}
                        Select flash memory region. (default: main)
  -e, --erase           Erase (-L) count of pages from (-F) page
  -E, --full_erase      Full erase
  -w, --write           Write "file.bin" starting from (-F) page
  -v, --verfi           Verificate writed "file.bin", used with flag (-w)
  -r, --read            Read flash to "file.bin" starting from (-F) page
  -F FIRST_PAGE, --first_page FIRST_PAGE
                        Num of first page. (default: 0)
  -L COUNT_PAGES, --count_pages COUNT_PAGES
                        Count pages.
  -p PORT, --port PORT  COM port.
  -b BAUD, --baud BAUD  Baudrate. (default: 115200)
  ```


### Write frimware.bin
```
k1921vkx_flasher -cwvE -f mflash -n main -F 0x00000000 -p COM6 -b 460800 --file firmware.bin 
```
### Read all flash memory into frimware.bin
```
k1921vkx_flasher -cr -p COM6 -b 460800 --file firmware.bin 
```

### Earse all flash memory into frimware.bin
```
k1921vkx_flasher -cE -p COM6 -b 460800 
```
### Set config word
```
k1921vkx_flasher -c -p COM6 -b 460800 --set_cfgword FLASHRE=1,NVRRE=1,JTAGEN=1,DEBUGEN=1,NVRWE=1,FLASHWE=1,BMODEDIS=0
```
# Supported MCUs
## K1921VK035
### Memory
* `mflash`
  * **Region**
  * `main` - 64 kB, 64 pages of 1 kB each
  * `nvr`  - 4 kB, 4 pages of 1 kB each

### CFGWORD 
* **FLASHRE** - mflash region read enable. (1 - enbale, 0 - disable)
* **NVRRE** - nvr region read enable. (1 - enbale, 0 - disable)
* **JTAGEN** - jtag/swd interface enable. (1 - enbale, 0 - disable)
* **DEBUGEN** - kernel debug enable. (1 - enbale, 0 - disable)
* **NVRWE** - nvr region write enable. (1 - enbale, 0 - disable)
* **FLASHWE** - mflash region write enable. (1 - enbale, 0 - disable)
* **BMODEDIS** - bootloader disable (1 - disable, 0 - enable)
# Building app

Run cmd:
Install dependencies
```
python setup.py egg_info
pip install -r k1921vkx_flasher.egg-info/requires.txt 
```
Build
```
pyinstaller k1921vkx_flasher.spec
```
# Building app with Windows 7 support
Create conda environment
```
conda create -y -n k1921vkx_flasher python=3.7
conda activate k1921vkx_flasher
pip install pyinstaller==5.8.0
```
Install dependencies
```
python setup.py egg_info
pip install -r k1921vkx_flasher.egg-info/requires.txt 
```
Build
```
pyinstaller k1921vkx_flasher.spec
```
