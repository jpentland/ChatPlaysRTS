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
        self.callbacks = {}
        self.descriptors = config.getDescriptors()
        self.notebook = ttk.Notebook(self)
        self.buildSettings(self.notebook)
        self.applyFrame = tk.Frame(self, padx = 5, pady = 5)
        self.okButton = tk.Button(self.applyFrame, text = "Ok", command = self.ok, width = 8)
        self.applyButton = tk.Button(self.applyFrame, text = "Apply", command = self.apply, width = 8)
        self.cancelButton = tk.Button(self.applyFrame, text = "Cancel", command = self.cancel, width = 8)
        self.defaultButton = tk.Button(self.applyFrame, text = "Reset to Default", command = self.default, width = 15)
        self.okButton.pack(side = tk.RIGHT, padx = 5)
        self.applyButton.pack(side = tk.RIGHT, padx = 5)
        self.cancelButton.pack(side = tk.RIGHT, padx = 5)
        self.defaultButton.pack(side = tk.LEFT, padx = 5)
        self.notebook.pack(anchor = tk.W, fill = tk.X, padx = 5)
        self.applyFrame.pack(fill = tk.BOTH)
        self.resizable(True, False)

    def buildSettings(self, notebook):
        self.gridSize = 0
        for section in self.config.data:
            self.vars[section] = {}
            self.callbacks[section] = {}
            self.buildSection(section, notebook)

    def validate(self, regex, string):
        return regex.match(string) != None

    def buildSection(self, section, notebook):
        if section not in self.descriptors:
            self.log.log(f"No descriptor for {section}", echo = False)
            return

        sectionFrame = ttk.Frame(notebook, relief = tk.GROOVE, borderwidth = 1)
        sectionFrame.gridSize = 0

        for setting in self.config[section]:
            self.buildSetting(section, setting, sectionFrame)

        notebook.add(sectionFrame, text = section)

    def buildSetting(self, section, setting, frame):
        try:
            description = self.descriptors[section][setting]["description"]
            regex = self.descriptors[section][setting]["regex"]
        except KeyError:
            self.log.log(f"No descriptor for {section} -> {setting}", echo = False)
            return

        frame.gridSize += 2
        label = tk.Label(frame, text = setting, font = ('Arial', 10, 'bold'), justify = tk.LEFT)

        if self.descriptors[section][setting]["convert"] != bool:
            self.vars[section][setting] = tk.StringVar(self)
            entry = tk.Entry(frame, textvariable = self.vars[section][setting])
            entry.grid(row = frame.gridSize, column = 2, sticky = tk.W, pady = 5)

            if regex != None:
                self.callbacks[section][setting] = self.register(lambda string : self.validate(regex, string))
                entry.configure(validate = "key", validatecommand = (self.callbacks[section][setting], '%P'))
        else:
            self.vars[section][setting] = tk.BooleanVar(self)
            checkButton = tk.Checkbutton(frame, variable = self.vars[section][setting])
            checkButton.grid(row = frame.gridSize, column = 2, sticky = tk.E, pady = 5)

        self.vars[section][setting].set(self.config[section][setting])

        descriptionLabel = tk.Label(frame, text = description, wraplength = 400, justify = tk.LEFT, font = ('Arial', 10, 'italic'))
        if frame.gridSize != 2:
            sep = ttk.Separator(frame, orient = 'horizontal')
            sep.grid(row = frame.gridSize - 1, column = 1, columnspan = 3, sticky = "ew")
        label.grid(row = frame.gridSize, column = 1, sticky = tk.E, padx = 5, pady =5)
        descriptionLabel.grid(row = frame.gridSize, column = 3, sticky = tk.W, padx = 5, pady = 5)

    def cancel(self):
        self.destroy()

    def apply(self):
        for section in self.vars:
            for value in self.vars[section]:
                convert = self.descriptors[section][value]["convert"]
                self.config[section][value] = convert(self.vars[section][value].get())
        self.config.write()

    def ok(self):
        self.apply()
        self.destroy()

    def default(self):
        for section in self.vars:
            for value in self.vars[section]:
                default = self.config.getDefault()
                try:
                    self.vars[section][value].set(default[section][value])
                except KeyError:
                    self.log.log(f"No default value for {section} -> {value}")
