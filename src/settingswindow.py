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
        self.notebook = ttk.Notebook(self)
        self.buildSettings(self.notebook)
        self.applyFrame = tk.Frame(self, padx = 5, pady = 5)
        self.okButton = tk.Button(self.applyFrame, text = "Ok", command = self.ok)
        self.applyButton = tk.Button(self.applyFrame, text = "Apply", command = self.apply)
        self.cancelButton = tk.Button(self.applyFrame, text = "Cancel", command = self.cancel)
        self.defaultButton = tk.Button(self.applyFrame, text = "Reset to Default", command = self.default)
        self.okButton.pack(side = tk.RIGHT)
        self.applyButton.pack(side = tk.RIGHT)
        self.cancelButton.pack(side = tk.RIGHT)
        self.defaultButton.pack(side = tk.LEFT)
        self.notebook.pack(anchor = tk.W, fill = tk.X, padx = 5, pady = 5)
        self.applyFrame.pack(fill = tk.BOTH)

    def buildSettings(self, notebook):
        self.gridSize = 0
        for section in self.config.data:
            self.vars[section] = {}
            self.buildSection(section, notebook)

    def buildSection(self, section, notebook):
        if section not in self.descriptions:
            return

        sectionFrame = ttk.Frame(notebook, relief = tk.GROOVE, borderwidth = 1)
        sectionFrame.gridSize = 0

        for setting in self.config[section]:
            self.buildSetting(section, setting, sectionFrame)

        notebook.add(sectionFrame, text = section)

    def buildSetting(self, section, setting, frame):
        try:
            description = self.descriptions[section][setting]
        except KeyError:
            return

        frame.gridSize += 2
        label = tk.Label(frame, text = setting, font = ('Arial', 10, 'bold'), justify = tk.LEFT)
        self.vars[section][setting] = tk.StringVar(self)
        self.vars[section][setting].set(self.config[section][setting])
        entry = tk.Entry(frame, textvariable = self.vars[section][setting])
        descriptionLabel = tk.Label(frame, text = description, wraplength = 400, justify = tk.LEFT, font = ('Arial', 10, 'italic'))
        if frame.gridSize != 2:
            sep = ttk.Separator(frame, orient = 'horizontal')
            sep.grid(row = frame.gridSize - 1, column = 1, columnspan = 3, sticky = "ew")
        label.grid(row = frame.gridSize, column = 1, sticky = tk.E, padx = 5, pady =5)
        entry.grid(row = frame.gridSize, column = 2, sticky = tk.W, pady = 5)
        descriptionLabel.grid(row = frame.gridSize, column = 3, sticky = tk.W, padx = 5, pady = 5)

    def cancel(self):
        self.destroy()

    def apply(self):
        self.log.log("Updating config not implemented")

    def ok(self):
        self.apply()
        self.cancel()

    def default(self):
        self.log.log("Reset default not implemented")
