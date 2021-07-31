#!/usr/bin/env python3
import sys
from tkinter import Tk, messagebox
from gui import Gui

from error import TomlError
from config import Config
from log import Log

APP_NAME = "ChatPlaysRTS"
APP_AUTHOR = "ChatPlaysRTS"


# GUI: Display error message and exit
def error_out(log, msg):
    if log is not None:
        log.log(msg)
    else:
        print(msg)
    messagebox.showerror("ERROR", msg)
    sys.exit()

def main():
    log = Log()

    try:
        config = Config(APP_NAME, APP_AUTHOR, log)
    except TomlError as e:
        print(str(e))
        error_out(log, "Failed to load config.toml\n%s" % str(e))
        return

    try:
        log.addConfig(config["log"])
    except Exception as e:
        print(str(e))
        error_out(log, "Failed to load config.toml\n%s" % str(e))
        return

    root = Tk()
    Gui(root, config, log)
    root.mainloop()

if __name__ == "__main__":
    main()
