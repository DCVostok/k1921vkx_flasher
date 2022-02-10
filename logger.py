#!/user/bin/env python
# coding:utf-8

import logging
import sys

# based on https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
# and https://stackoverflow.com/questions/13733552/logger-configuration-to-log-to-file-and-print-to-stdout

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

# The background is set with 40 plus the number of the color, and the foreground with 30

# These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"


def formatter_message(message, use_color=True):
    if use_color:
        message = message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
    else:
        message = message.replace("$RESET", "").replace("$BOLD", "")
    return message


COLORS = {
    '[WARN]': YELLOW,
    '[INFO]': BLUE,
    '[DBG]': GREEN,
    '[CRIT]': MAGENTA,
    '[ERR]': RED
}


class ColoredFormatter(logging.Formatter):

    def __init__(self, msg, use_color=True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in COLORS:
            levelname_color = COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)


def init(debug=False, logfile=None):
    logging.addLevelName(logging.DEBUG, "[DBG]")
    logging.addLevelName(logging.INFO, "[INFO]")
    logging.addLevelName(logging.WARNING, "[WARN]")
    logging.addLevelName(logging.ERROR, "[ERR]")
    logging.addLevelName(logging.CRITICAL, "[CRIT]")

    rootLogger = logging.getLogger()
    if debug:
        rootLogger.setLevel(logging.DEBUG)
    else:
        rootLogger.setLevel(logging.INFO)

    if logfile:
        fileHandler = logging.FileHandler(logfile, 'w')
        fileHandler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        rootLogger.addHandler(fileHandler)

    FORMAT = "$BOLD%(levelname)s$RESET: %(message)s"
    COLOR_FORMAT = formatter_message(FORMAT, True)
    consoleHandler = logging.StreamHandler(sys.stdout)
    if sys.platform.startswith('win'):
        consoleHandler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    else:
        consoleHandler.setFormatter(ColoredFormatter(COLOR_FORMAT))
    rootLogger.addHandler(consoleHandler)


def debug(msg):
    logging.debug(msg)


def info(msg):
    logging.info(msg)


def warning(msg):
    logging.warning(msg)


def error(msg):
    logging.error(msg)


def critical(msg):
    logging.critical(msg)


if __name__ == '__main__':
    pass
