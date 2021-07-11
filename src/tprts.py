#!/usr/bin/env python3
import time
import sys
from config import Config
from log import Log
from error import *

from tkinter import Tk, messagebox
from gui import Gui

appname = "TwitchPlaysRTS"
appauthor = "TwitchPlaysRTS"

# GUI: Display error message and exit
def errorOutGUI(log, msg):
    if log != None:
        log.log(msg)
    else:
        print(msg)
    messagebox.showerror("ERROR", msg)
    sys.exit()

def main():
    try:
        config = Config(appname, appauthor)
    except TomlError as e:
        print(str(e))
        errorOutGUI(None, "Failed to load config.toml\n%s" % str(e))
        return

    try:
        log = Log(config["log"])
    except Exception as e:
        print(str(e))
        errorOutGUI(None, "Failed to load config.toml\n%s" % str(e))
        return

    root = Tk()
    gui = Gui(root, config, log)
    root.mainloop()

if __name__ == "__main__":
    main()
