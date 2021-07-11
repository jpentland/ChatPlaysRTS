import sys
import threading
import time
from twitchirc import TwitchIrc
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

    def errorOut(self, message, fatal = False):
        self.log.log(message)
        self.onError(message, fatal)

    def run(self):
        self.irc = TwitchIrc(self.config, self.log)

        try:
            self.irc.connect(5)
        except AuthenticationError:
            self.errorOut("Invalid username or oauth")
            return
        except ConnectionFailedError:
            self.errorOut("Failed to connect to Twitch")
            return
        except ClientDisconnectError:
            self.onDisconnect()
            return
        except Exception:
            self.log.log_exception(e)
            self.errorOut("Failed to connect to Twitch")
            return

        try:
            self.commands = Commands(self.config, self.log)
        except (RegexError, TomlError, FileNotFoundError) as e:
            self.log.log_exception(e)
            self.errorOut("Failed to load commands")
            return

        self.execution = Execution(self.config, self.commands, self.irc, self.log)

        lastError = 0
        self.onConnect()

        while True:
            try:
                self.execution.processCommandQueue()
            except Exception as e:
                if self.irc.connected == False:
                    self.onDisconnect()
                    if self.irc.clientDisconnect:
                        return
                    else:
                        self.errorOut("IRC Disconnected")
                self.log.log_exception(e)
                if time.time() - lastError < 10:
                    self.log.log("Program keeps crashing, please restart")
                    break
                self.lastError = time.time()
                return

        self.errorOut("Quitting")

    def stop(self):
        self.irc.close()