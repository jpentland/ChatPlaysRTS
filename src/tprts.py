#!/usr/bin/env python3
import time
import sys
from twitchirc import TwitchIrc, AuthenticationError, ConnectionFailedError
from execution import Execution
from config import Config
from log import Log
from commands import Commands

appname = "TwitchPlaysRTS"
appauthor = "TwitchPlaysRTS"

# CLI: display error message, press any key to exit
def errorOut(msg):
    log.log(msg)
    input("Press RETURN to exit\n")
    sys.exit(1)

# CLI: Get username and oauth values if not set in config
def getCredentials(config):
    if "credentials" not in config:
        config["credentials"] = {}

    if "username" not in config["credentials"]:
        config["credentials"]["username"] = input("Please enter your stream username: ")

    if "oauth" not in config["credentials"]:
        config["credentials"]["oauth"] = input("Please enter your stream oauth: ")

    return config

if __name__ == "__main__":
    config = Config(appname, appauthor)
    config = getCredentials(config)
    log = Log(config["log"])
    config.write()
    irc = TwitchIrc(config, log)

    try:
        irc.connect(5)
    except AuthenticationError:
        errorOut("Invalid username or oauth")
    except ConnectionFailedError:
        errorOut("Failed to connect to Twitch")
    except Exception:
        log.log_exception(e)
        errorOut("Failed to connect to Twitch")

    lastError = 0
    commands = Commands(config, log)
    execution = Execution(config, commands, irc, log)
    while True:
        try:
            execution.processCommandQueue()
        except Exception as e:
            log.log_exception(e)
            if time.time() - lastError < 10:
                log.log("Program keeps crashing, please restart")
                break
            lastError = time.time()

    errorOut("Quitting")
