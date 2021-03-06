import tkinter as tk
import tkinter.scrolledtext as tkst
from error import *
import sys
import time
import os
import subprocess
from threading import Lock
from controller import Controller
from monitor import Monitor
from settingswindow import Settingswindow

class Gui:
    def __init__(self, master, config, log):
        self.config = config
        self.log = log
        self.master = master
        self.username = tk.StringVar(master)
        self.oauth = tk.StringVar(master)
        self.remember = tk.IntVar(master)
        self.selectedMonitor = tk.IntVar(master)
        self.monitor = self.config.monitor
        self.selectedMonitor.set(self.monitor.getSelectedMonitor())
        master.title("Chat Plays RTS")

        username, oauth, remember = config.getCredentials()
        self.username.set(username)
        self.oauth.set(oauth)

        self.mainframe = tk.Frame(master)
        self.mainframe.pack()

        self.usernameLabel = tk.Label(self.mainframe, text="Username")
        self.usernameLabel.grid(row=1, column=1)

        self.usernameEntry = tk.Entry(self.mainframe, textvariable = self.username)
        self.usernameEntry.grid(row=1, column=2, columnspan=2)

        self.oauthLabel = tk.Label(self.mainframe, text="Twitch Oauth")
        self.oauthLabel.grid(row=2, column=1)

        self.oauthEntry = tk.Entry(self.mainframe, show = "*", textvariable = self.oauth)
        self.oauthEntry.grid(row=2, column=2, columnspan=2)

        self.rememberFrame = tk.Frame(self.mainframe)
        self.rememberFrame.grid(row=3, column=3)
        self.rememberLabel = tk.Label(self.rememberFrame, text = "Remember")
        self.rememberLabel.pack(side = tk.LEFT)
        self.rememberButton = tk.Checkbutton(self.rememberFrame, variable = self.remember)
        self.rememberButton.pack(side = tk.RIGHT)
        self.remember.set(remember)

        self.connectButton = tk.Button(self.mainframe, text="Connect", command=self.connect)
        self.connectButton.grid(row=4, column=1)

        self.disconnectButton = tk.Button(self.mainframe, text="Disconnect", command=self.disconnect)
        self.disconnectButton.grid(row=4, column=2)
        self.disconnectButton.config(state = tk.DISABLED)

        self.close_button = tk.Button(self.mainframe, text="Close", command=self.master.quit)
        self.close_button.grid(row=4, column=3)

        self.text = tkst.ScrolledText(self.master, height = 0, width = 60)
        self.text.pack(fill = tk.BOTH, expand = True)
        self.textLock = Lock()
        self.log.addCallback(self.writeLog)

        self.build_menubar()
        self.build_statusbar()

        self.master.geometry("400x400")

    def build_menubar(self):
        self.menu = tk.Menu(self.master)
        self.tprtsMenu = tk.Menu(self.menu, tearoff = 0)
        self.tprtsMenu.add_command(label = "Open Config Directory", command = self.openConfigDir)
        self.tprtsMenu.add_separator()
        self.tprtsMenu.add_command(label = "Quit", command = self.master.quit)
        self.menu.add_cascade(label = "ChatPlaysRTS", menu = self.tprtsMenu)

        self.configMenu = tk.Menu(self.menu, tearoff = 0)
        self.monitorMenu = tk.Menu(self.configMenu, tearoff = 0)
        self.refreshMonitorMenu()
        self.configMenu.add_cascade(label = "Monitor", menu = self.monitorMenu)
        self.menu.add_cascade(label = "Config", menu = self.configMenu)
        self.configMenu.add_command(label = "Settings", command = self.open_config)

        self.helpMenu = tk.Menu(self.menu, tearoff = 0)
        self.helpMenu.add_command(label = "Readme", command = self.open_readme)
        self.helpMenu.add_command(label = "Commands Help", command = self.open_commands_help)
        self.helpMenu.add_command(label = "Keys list", command = self.open_keys_list)
        self.menu.add_cascade(label = "Help", menu = self.helpMenu)

        self.master.config(menu = self.menu)

    def build_statusbar(self):
        self.statusbar = tk.Frame(self.master)
        self.statusbar.pack(fill = tk.X)
        self.connectedLabel = tk.Label(self.statusbar, text = "Not connected", fg = "red", padx = 5)
        self.connectedLabel.pack(side = tk.LEFT)
        tk.ttk.Separator(self.statusbar, orient=tk.VERTICAL).pack(side = tk.LEFT, fill = tk.Y, padx = 5)
        self.statusbar.pack(fill = tk.X)


        self.stoppedFrame = tk.Frame(self.statusbar)
        self.stoppedLabel = tk.Label(self.stoppedFrame, text = "Stopped", fg = "red")
        self.stoppedLabel.pack(side = tk.LEFT)

        tk.ttk.Separator(self.stoppedFrame, orient=tk.VERTICAL).pack(side = tk.LEFT, fill = tk.Y, padx = 5)

        self.restrictFrame = tk.Frame(self.statusbar)
        self.restrictLabel = tk.Label(self.restrictFrame, text = "")
        self.restrictLabel.pack(side = tk.LEFT)

        tk.ttk.Separator(self.restrictFrame, orient=tk.VERTICAL).pack(side = tk.LEFT, fill = tk.Y, padx = 5)

    def connect(self):
        self.connectButton.config(state = tk.DISABLED)
        self.disconnectButton.config(state = tk.NORMAL)
        self.connectedLabel.config(text = "Connecting...", fg = "yellow")

        self.config.setCredentials(self.username.get(), self.oauth.get(), self.remember.get())

        self.controller = Controller(self.config, self.log, self.onConnect, self.onDisconnect, self.error)
        self.controller.setControlStateCallback(self.updateControlState)
        self.controller.start()

    def disconnect(self):
        self.connectButton.config(state = tk.NORMAL)
        self.disconnectButton.config(state = tk.DISABLED)

        self.controller.stop()

    def writeLog(self, msg):
        with self.textLock:
            self.text.insert(tk.END, "%s\n" % msg.strip())
            self.text.see("end")

    def error(self, message, fatal = False):
        tk.messagebox.showerror("ERROR", message)
        if fatal:
            print("FATAL")
            self.master.quit()

    def onConnect(self):
        self.connectedLabel.config(text = "Connected", fg = "green")
        self.connectButton.config(state = tk.DISABLED)
        self.disconnectButton.config(state = tk.NORMAL)

    def onDisconnect(self):
        self.connectedLabel.config(text = "Not connected", fg = "red")
        self.connectButton.config(state = tk.NORMAL)
        self.disconnectButton.config(state = tk.DISABLED)
        self.updateControlState(True, None)

    def openConfigDir(self):
        if os.name == 'nt':
            subprocess.Popen(['explorer', self.config.config_dir])
        elif os.name == 'posix':
            subprocess.Popen(['xdg-open', self.config.config_dir])
        else:
            self.error("Not implemented for your OS: %s" % os.name)

    def openFile(self, file):
        if os.name == 'nt':
            subprocess.Popen(['notepad', file])
        elif os.name == 'posix':
            subprocess.Popen(['xdg-open', file])
        else:
            self.error("Not implemented for your OS: %s" % os.name)

    def open_readme(self):
        self.openFile("README.md")

    def open_commands_help(self):
        self.openFile(os.path.join("doc", "Commands.txt"))

    def open_keys_list(self):
        self.openFile(os.path.join("doc", "keys.txt"))

    def refreshMonitorMenu(self):
        self.monitorMenu.delete(0, tk.END)
        self.monitor.refresh()
        selected = self.monitor.getSelectedMonitor()
        monitors = self.monitor.listMonitors()
        for i, monitor in zip(range(len(monitors)), monitors):
            self.monitorMenu.add_radiobutton(label = monitor, value = i, variable = self.selectedMonitor, command = self.onSelectMonitor)
        self.selectedMonitor.set(selected)

        self.monitorMenu.add_separator()
        self.monitorMenu.add_command(label = "Refresh", command = self.refreshMonitorMenu)

    def onSelectMonitor(self):
        self.monitor.selectMonitor(self.selectedMonitor.get())

    def open_config(self):
        self.configWindow = Settingswindow(self.master, self.log, self.config)

    def updateControlState(self, state, restrict):
        if state:
            self.stoppedFrame.pack_forget()
        else:
            self.stoppedFrame.pack(side = tk.LEFT)

        if restrict == None:
            self.restrictFrame.pack_forget()
        else:
            restrictStr = ""
            for badge in restrict:
                restrictStr += f"{badge}, "
            restrictStr = restrictStr[:-2]
            self.restrictLabel.config(text = f"Restricted: {restrictStr}")
            self.restrictFrame.pack(side = tk.LEFT)


