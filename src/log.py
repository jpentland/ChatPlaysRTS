from threading import Lock
from time import localtime, strftime
import traceback as tb
import pathlib
import os

class Log():
    def __init__(self, config = None):
        self.lock = Lock()
        self.callbacks = []
        self.buffer = []
        self.logfile = None

        self.log("*****\n")
        self.log("STARTING %s" % strftime("%a, %d %b %Y %H:%M:%S +0000\n", localtime()))
        self.log("*****\n")

        if config != None:
            self.addConfig(config)

    # Open log file based on config object
    def addConfig(self, config):
        self.logfile_path = config["logfile"]
        pathlib.Path("log").mkdir(parents=True, exist_ok=True)

        try:
            self.logfile = open(os.path.join("log", self.logfile_path), "a")
            self.flushBuffer()
        except Exception as e:
            print(e)
            print("Failed to open logfile")
            self.logfile = None

    # Get time in log format
    def logTime(self):
        return strftime("%H:%M:%S")

    # Write to logfile or buffer if logfile not available yet
    def writeOrBuffer(self, message):
        if self.logfile != None:
            try:
                self.logfile.write(message)
                self.logfile.flush()
            except Exception as e:
                self.log("Failed to write log")
                self.log_exception(e)
        else:
            self.buffer.append(message)

    # Flush buffer to newly opened log file
    def flushBuffer(self):
        for message in self.buffer:
            self.logfile.write(message)
            self.logfile.flush()

    # Write a message to the log file with optional echo to callback and console
    def log(self, message, echo = True):
        with self.lock:
            if echo:
                print(message)
            self.writeOrBuffer("%s %s\n" % (self.logTime(), message))

        if echo:
            for cb in self.callbacks:
                cb(message)

    # Log an exception, add stack trace with no echo
    def log_exception(self, exception):
        self.log("ERROR: " + str(exception))
        self.log(tb.format_exc(), echo = False)

    # Add a callback method which should be called for each log message
    def addCallback(self, cb):
        self.callbacks.append(cb)

    # Close the log file
    def close(self):
        self.logfile.flush()
        self.logfile.close()

