#!/usr/bin/env python3
import time
import sys
import os
from queue import Queue
import toml
from twitchirc import TwitchIrc, AuthenticationError, ConnectionFailedError
from execution import Execution
from config import Config
from log import Log

appname = "TwitchPlaysRTS"
appauthor = "TwitchPlaysRTS"

# Return combined default commands and user commands
def loadCommands(config):
    commands = []

    if os.path.isfile(os.path.join(config.config_dir, config.commands_file)):
        migrateOldCommands()

    with open(os.path.join(config.defaultconf_dir, config.commands_file)) as commandsFile:
            content = commandsFile.read()
            defaultCommands = toml.loads(content)["command"]
            commands += defaultCommands
    try:
        with open(os.path.join(config.config_dir, config.user_commands_file)) as commandsFile:
            content = commandsFile.read()
            userCommands = toml.loads(content)["command"]
            log.log("Loaded %d custom commands from %s" % (len(userCommands), config.user_commands_file))
            commands += userCommands
    except FileNotFoundError:
        log.log("No user commands file found")

    return commands

# Migrate old commands file (pre v0.8)
def migrateOldCommands():
    defaultCommands = []
    oldCommands = []
    newCommands = []

    with open(os.path.join(defaultconf_dir, commands_file)) as commandsFile:
            content = commandsFile.read()
            defaultCommands += toml.loads(content)["command"]

    with open(os.path.join(config_dir, commands_file)) as commandsFile:
            content = commandsFile.read()
            oldCommands += toml.loads(content)["command"]

    # Import any non-default commands in commands.toml to user_commands.toml
    for command in oldCommands:
        try:
            next(filter(lambda x : x["regex"] == command["regex"], defaultCommands))
        except StopIteration:
            newCommands.append(command)

    if len(newCommands) > 0:
        with open(os.path.join(config_dir, user_commands_file), "w") as commandsFile:
            toml.dump({"command" : newCommands}, commandsFile)

        log.log("Migrated %d commands from old commands.toml to new user_commands.toml" % len(newCommands))

    log.log("Deleting old " + commands_file)
    os.remove(os.path.join(config_dir, commands_file))

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
    commands = loadCommands(config)
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
