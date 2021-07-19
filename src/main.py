#!/usr/bin/env python3
import time
import sys
from config import Config
from log import Log
from error import *

from tkinter import Tk, messagebox
from gui import Gui

appname = "ChatPlaysRTS"
appauthor = "ChatPlaysRTS"


# GUI: Display error message and exit
def errorOutGUI(log, msg):
    if log != None:
        log.log(msg)
    else:
        print(msg)
    messagebox.showerror("ERROR", msg)
    sys.exit()

def main():
    log = Log()

    try:
        config = Config(appname, appauthor, log)
    except TomlError as e:
        print(str(e))
        errorOutGUI(log, "Failed to load config.toml\n%s" % str(e))
        return

    try:
        log.addConfig(config["log"])
    except Exception as e:
        print(str(e))
        errorOutGUI(log, "Failed to load config.toml\n%s" % str(e))
        return

    root = Tk()
    gui = Gui(root, config, log)
    root.mainloop()

if __name__ == "__main__":
    main()
