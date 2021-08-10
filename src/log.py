from threading import RLock
from time import localtime, strftime
import traceback as tb
import pathlib
import os

class Log():
    def __init__(self, config = None):
        self.lock = RLock()
        self.callbacks = []
        self.buffer = []
        self.logfile = None

        self.log("*****\n")
        self.log("STARTING %s" % strftime("%a, %d %b %Y %H:%M:%S +0000\n", localtime()))
        self.log("*****\n")

        if config is not None:
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
    @staticmethod
    def logTime():
        return strftime("%H:%M:%S")

    # Write a message to the log file with optional echo to callback
    # save to buffer first if log file not open yet
    def log(self, message, echo = True):
        print(message)
        with self.lock:
            if self.logfile is not None:
                try:
                    self.logfile.write(f"{message}\n")
                    self.logfile.flush()
                except Exception as e:
                    self.log("Failed to write log")
                    self.log_exception(e)

                if echo:
                    for cb in self.callbacks:
                        cb(message)

            else:
                self.buffer.append((message, echo))

    # Flush buffer to newly opened log file
    def flushBuffer(self):
        for (message, echo) in self.buffer:
            self.logfile.write(f"{message}\n")
            self.logfile.flush()
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
