import tkinter as tk
from tkinter import ttk

class Settingswindow(tk.Toplevel):
    def __init__(self, master, log, config):
        super().__init__(master)
        self.title("Settings")
        self.master = master
        self.config = config
        self.log = log
        self.vars = {}
        self.descriptions = config.getDescriptions()
        self.settingsFrame = tk.Frame(self, relief = tk.GROOVE, borderwidth = 1)
        self.buildSettings(self.settingsFrame)
        # add apply button
        self.applyFrame = tk.Frame(self, padx = 5, pady = 5)
        self.applyButton = tk.Button(self.applyFrame, text = "Apply", command = self.apply)
        self.cancelButton = tk.Button(self.applyFrame, text = "Cancel", command = self.cancel)
        self.applyButton.pack(side = tk.RIGHT)
        self.cancelButton.pack(side = tk.RIGHT)
        self.settingsFrame.pack(anchor = tk.W, fill = tk.X, padx = 5, pady = 5)
        self.applyFrame.pack(fill = tk.X)

    def buildSettings(self, frame):
        self.gridSize = 0
        for section in self.config.data:
            self.vars[section] = {}
            self.buildSection(section, frame)

    def buildSection(self, section, frame):
        # Add section header
        for setting in self.config[section]:
            self.buildSetting(section, setting, frame)

    def buildSetting(self, section, setting, frame):
        try:
            description = self.descriptions[section][setting]
        except KeyError:
            return

        self.gridSize += 2
        label = tk.Label(frame, text = setting, font = ('Arial', 10, 'bold'), justify = tk.LEFT)
        self.vars[section][setting] = tk.StringVar(self)
        self.vars[section][setting].set(self.config[section][setting])
        entry = tk.Entry(frame, textvariable = self.vars[section][setting])
        descriptionLabel = tk.Label(frame, text = description, wraplength = 400, justify = tk.LEFT, font = ('Arial', 10, 'italic'))
        if self.gridSize != 2:
            sep = ttk.Separator(frame, orient = 'horizontal')
            sep.grid(row = self.gridSize - 1, column = 1, columnspan = 3, sticky = "ew")
        label.grid(row = self.gridSize, column = 1, sticky = tk.E, padx = 5, pady =5)
        entry.grid(row = self.gridSize, column = 2, sticky = tk.W, pady = 5)
        descriptionLabel.grid(row = self.gridSize, column = 3, sticky = tk.W, padx = 5, pady = 5)

    def cancel(self):
        pass

    def apply(self):
        pass
