import sys
import threading
import time
from simpleirc import SimpleIrc
from execution import Execution
from config import Config
from log import Log
from commands import Commands
from error import *

class Controller(threading.Thread):
    def __init__(self, config, log, onConnect, onDisconnect, onError):
        threading.Thread.__init__(self, daemon = True)
        self.config = config
        self.log = log
        self.onConnect = onConnect
        self.onDisconnect = onDisconnect
        self.onError = onError

    def errorOut(self, message, e = None, fatal = False):
        if e == None:
            self.onError(message, fatal)
        else:
            self.onError("%s\n%s" % (message, str(e)), fatal)
            self.log.log_exception(e)

        self.log.log(message)
        self.onDisconnect()

    def run(self):
        self.irc = SimpleIrc(self.config, self.log)

        try:
            self.commands = Commands(self.config, self.log)
        except (RegexError, TomlError, FileNotFoundError) as e:
            self.log.log_exception(e)
            self.errorOut("Failed to load commands")
            return

        try:
            self.irc.connect(5)
        except AuthenticationError:
            self.errorOut("Invalid username or oauth")
            return
        except ConnectionFailedError as e:
            self.errorOut("Failed to connect", e = e)
            return
        except ClientDisconnectError:
            self.onDisconnect()
            return
        except Exception:
            self.log.log_exception(e)
            self.errorOut("Failed to connect to Twitch", e = e)
            return

        self.execution = Execution(self.config, self.commands, self.irc, self.log)

        lastError = 0
        self.onConnect()

        while True:
            try:
                self.execution.processCommandQueue()
            except ConnectionFailedError as e:
                self.errorOut("IRC Disconnected", e)
                return
            except ClientDisconnectError as e:
                self.onDisconnect()
                self.log.log("IRC Disconnected")
                return
            except Exception as e:
                self.log.log_exception(e)
                if time.time() - lastError < 10:
                    self.errorOut("Cannot recover from error", e)
                    return
                self.lastError = time.time()
                continue

    def stop(self):
        self.irc.close()
