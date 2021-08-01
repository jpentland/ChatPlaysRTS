import os
import tkinter as tk
from tkinter import ttk

class CommandWindow(tk.Toplevel):
    def __init__(self, master, log, config):
        super().__init__(master)
        self.title("Commands")
        self.master = master
        self.config = config
        self.log = log
        self.defaultConfigs = \
                os.listdir("defaultconf") + \
                ["usercommands.toml"]
        self.files = []

        self.fileGrid = tk.Frame(self, padx = 5, pady = 5)

        for file in self.config["command"]["commands"]:
            self.add_file(file)

        self.plusButton = tk.Button(self.fileGrid, text = "+", file = None)
        self.plusButton.grid(row = len(self.files), column = 1, padx = 5, pady = 5, sticky = "w")

        self.fileGrid.pack(fill = tk.BOTH)

        self.applyFrame = tk.Frame(self, padx = 5, pady = 5)
        self.okButton = tk.Button(self.applyFrame, text = "Ok", command = self.ok, width = 5)
        self.applyButton = tk.Button(self.applyFrame, text = "Apply", command = self.apply, width = 5)
        self.cancelButton = tk.Button(self.applyFrame, text = "Cancel", command = self.cancel, width = 5)
        self.okButton.pack(side = tk.RIGHT, padx = 5)
        self.applyButton.pack(side = tk.RIGHT, padx = 5)
        self.cancelButton.pack(side = tk.RIGHT, padx = 5)
        self.applyFrame.pack(fill = tk.BOTH)

    def add_file(self, file):
        fileDict = {"var" : tk.StringVar(self)}
        fileDict["var"].set(file)
        fileDict["menu"] = \
                tk.OptionMenu(
                        self.fileGrid,
                        fileDict["var"],
                        *(self.defaultConfigs + ["... browse"])
                )
        fileDict["menu"].grid(row = len(self.files), column = 1, sticky = "ew", pady = 5, padx = 5)

        fileDict["editButton"] = tk.Button(self.fileGrid, text = "Edit", command =None)
        fileDict["editButton"].grid(row = len(self.files), column = 2, padx = 5)

        fileDict["browseButton"] = tk.Button(self.fileGrid, text = "📂", command =None)
        fileDict["browseButton"].grid(row = len(self.files), column = 3, padx = 5)

        fileDict["deleteButton"] = tk.Button(self.fileGrid, text = "❌", command =None)
        fileDict["deleteButton"].grid(row = len(self.files), column = 4, padx = 5)

        self.files.append(fileDict)

    def delete_file(self, i):
        pass

    def edit_file(self, i):
        pass

    def ok(self):
        pass

    def apply(self):
        pass

    def cancel(self):
        pass
