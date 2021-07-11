import tkinter as tk
import tkinter.scrolledtext as tkst
from error import *
import sys
import time
from threading import Lock
from controller import Controller

class Gui:
    def __init__(self, master, config, log):
        self.config = config
        self.log = log
        self.master = master
        self.username = tk.StringVar(master)
        self.oauth = tk.StringVar(master)
        self.remember = tk.IntVar(master)
        master.title("Twitch Plays RTS")

        if "username" in config["credentials"]:
            self.username.set(config["credentials"]["username"])

        if "oauth" in config["credentials"]:
            self.oauth.set(config["credentials"]["oauth"])

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
        if "remember" in self.config["credentials"] \
                and self.config["credentials"]["remember"] == 1:
            self.remember.set(1)

        self.connectButton = tk.Button(self.mainframe, text="Connect", command=self.connect)
        self.connectButton.grid(row=4, column=1)

        self.disconnectButton = tk.Button(self.mainframe, text="Disconnect", command=self.disconnect)
        self.disconnectButton.grid(row=4, column=2)
        self.disconnectButton.config(state = tk.DISABLED)

        self.close_button = tk.Button(self.mainframe, text="Close", command=self.mainframe.quit)
        self.close_button.grid(row=4, column=3)

        self.text = tkst.ScrolledText(self.master, height = 20, width = 80)
        self.text.pack(fill = tk.Y)
        self.textLock = Lock()
        self.log.addCallback(self.writeLog)

        self.connectionFrame = tk.Frame(master)
        self.connectionFrame.pack(fill = tk.X)
        self.connectedLabel = tk.Label(self.connectionFrame, text = "Not connected", fg = "red")
        self.connectedLabel.pack(side = tk.LEFT)

    def connect(self):
        self.connectButton.config(state = tk.DISABLED)
        self.disconnectButton.config(state = tk.NORMAL)
        self.connectedLabel.config(text = "Connecting...", fg = "yellow")

        self.config["credentials"]["username"] = self.username.get()
        self.config["credentials"]["oauth"] = self.oauth.get()
        if self.remember.get() == 1:
            self.config["credentials"]["remember"] = 1
            self.config.write()

        self.controller = Controller(self.config, self.log, self.onConnect, self.onDisconnect, self.error)
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
            sys.exit()

    def onConnect(self):
        self.connectedLabel.config(text = "Connected", fg = "green")
        self.connectButton.config(state = tk.DISABLED)
        self.disconnectButton.config(state = tk.NORMAL)

    def onDisconnect(self):
        self.connectedLabel.config(text = "Not connected", fg = "red")
        self.connectButton.config(state = tk.NORMAL)
        self.disconnectButton.config(state = tk.DISABLED)
