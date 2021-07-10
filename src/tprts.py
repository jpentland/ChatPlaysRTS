#!/usr/bin/env python3
import time
import sys
from twitchirc import TwitchIrc, AuthenticationError, ConnectionFailedError
from execution import Execution
from config import Config
from log import Log
from commands import Commands, RegexError, TomlError

appname = "TwitchPlaysRTS"
appauthor = "TwitchPlaysRTS"

# CLI: display error message, press any key to exit
def errorOut(log, msg):
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

def main():
    config = Config(appname, appauthor)
    config = getCredentials(config)
    log = Log(config["log"])
    config.write()
    irc = TwitchIrc(config, log)

    try:
        irc.connect(5)
    except AuthenticationError:
        errorOut(log, "Invalid username or oauth")
        return
    except ConnectionFailedError:
        errorOut(log, "Failed to connect to Twitch")
        return
    except Exception:
        log.log_exception(e)
        errorOut(log, "Failed to connect to Twitch")
        return

    try:
        commands = Commands(config, log)
    except (RegexError, TomlError, FileNotFoundError) as e:
        log.log_exception(e)
        errorOut(log, "Failed to load commands")
        return

    execution = Execution(config, commands, irc, log)

    lastError = 0

    while True:
        try:
            execution.processCommandQueue()
        except Exception as e:
            log.log_exception(e)
            if time.time() - lastError < 10:
                log.log("Program keeps crashing, please restart")
                break
            lastError = time.time()

    errorOut(log, "Quitting")

if __name__ == "__main__":
    main()
