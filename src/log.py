from threading import Lock
from time import localtime, strftime
import traceback as tb

class Log():
    def __init__(self, config):
        self.echo = config["echo"]
        self.logfile_path = config["logfile"]
        try:
            self.logfile = open(self.logfile_path, "a")
        except Exception as e:
            print(e)
            print("Failed to open logfile")

        self.lock = Lock()
        self.logfile.write("*****\n")
        self.logfile.write("STARTING %s" % strftime("%a, %d %b %Y %H:%M:%S +0000\n", localtime()))
        self.logfile.write("*****\n")
        self.logfile.flush()

    def logTime(self):
        return strftime("%H:%M:%S")

    def log(self, message, echo = True):
        with self.lock:
            if self.echo and echo:
                print(message)
            self.logfile.write("%s %s\n" % (self.logTime(), message))
            self.logfile.flush()

    def log_exception(self, exception):
        self.log("ERROR: " + str(exception))
        self.log(tb.format_exc(), echo = False)

