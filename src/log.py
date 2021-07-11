from threading import Lock
from time import localtime, strftime
import traceback as tb
import pathlib
import os

class Log():
    def __init__(self, config):
        self.echo = config["echo"]
        self.logfile_path = config["logfile"]
        pathlib.Path("log").mkdir(parents=True, exist_ok=True)
        try:
            self.logfile = open(os.path.join("log", self.logfile_path), "a")
        except Exception as e:
            print(e)
            print("Failed to open logfile")

        self.lock = Lock()
        self.logfile.write("*****\n")
        self.logfile.write("STARTING %s" % strftime("%a, %d %b %Y %H:%M:%S +0000\n", localtime()))
        self.logfile.write("*****\n")
        self.logfile.flush()
        self.callbacks = []

    def logTime(self):
        return strftime("%H:%M:%S")

    def log(self, message, echo = True):
        with self.lock:
            if self.echo and echo:
                print(message)
            self.logfile.write("%s %s\n" % (self.logTime(), message))
            self.logfile.flush()

        if echo:
            for cb in self.callbacks:
                cb(message)

    def addCallback(self, cb):
        self.callbacks.append(cb)

    def log_exception(self, exception):
        self.log("ERROR: " + str(exception))
        self.log(tb.format_exc(), echo = False)

    def close(self):
        self.logfile.flush()
        self.logfile.close()

