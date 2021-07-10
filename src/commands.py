import os
import toml
import re
from error import *

class Commands():
    def __init__(self, config, log):
        self.config = config
        self.data = []
        self.log = log
        self.commands_file_path = os.path.join(
                self.config.defaultconf_dir,
                self.config.commands_file
        )
        self.user_commands_file_path = os.path.join(
                self.config.config_dir,
                self.config.user_commands_file
        )
        self.loadCommands()

    # Load commands from usercommands and default commands
    def loadCommands(self):
        try:
            self.migrateOldCommands()
        except Exception as e:
            self.log.log("Error occurred while migrating old %s, you may want to delete it" % self.config.commands_file)
            self.log.log_exception(e)

        self.loadDefaultCommands()

        try:
            self.loadUserCommands()
        except FileNotFoundError as e:
            self.log.log("%s not found" % self.config.user_commands_file)

        self.compile()

        self.log.log("%d total commands compiled" % len(self.data))

    # Load default commands
    def loadDefaultCommands(self):
        with open(self.commands_file_path) as commandsFile:
            content = commandsFile.read()

            try:
                defaultCommands = toml.loads(content)["command"]
            except toml.decoder.TomlDecodeError as e:
                self.log.log("Failed to read %s" % self.commands_file_path)
                raise TomlError(e)

            self.data += defaultCommands

    # Load user commands
    def loadUserCommands(self):
        with open(self.user_commands_file_path) as commandsFile:
            content = commandsFile.read()
            try:
                userCommands = toml.loads(content)["command"]
            except toml.decoder.TomlDecodeError as e:
                self.log.log("Failed to read %s" % self.config.user_commands_file)
                raise TomlError(e)

            self.log.log("Loaded %d custom commands from %s" \
                    % (len(userCommands), self.config.user_commands_file))

            self.data += userCommands

    # Migrate old commands file (pre v0.8)
    def migrateOldCommands(self):
        old_commands_file_path = os.path.join(
                self.config.config_dir,
                self.config.commands_file
        )
        if os.path.isfile(old_commands_file_path):
            defaultCommands = []
            oldCommands = []
            newCommands = []

            with open(self.commands_file_path) as commandsFile:
                    content = commandsFile.read()
                    defaultCommands += toml.loads(content)["command"]

            try:
                with open(self.user_commands_file_path) as commandsFile:
                        content = commandsFile.read()
                        newCommands += toml.loads(content)["command"]
            except FileNotFoundError:
                pass

            with open(old_commands_file_path) as commandsFile:
                    content = commandsFile.read()
                    oldCommands += toml.loads(content)["command"]

            # Import any non-default commands in commands.toml to user_commands.toml
            for command in oldCommands:
                try:
                    next(filter(lambda x : x["regex"] == command["regex"], defaultCommands))
                except StopIteration:
                    newCommands.append(command)

            if len(newCommands) > 0:
                with open(self.user_commands_file_path, "w") as commandsFile:
                    toml.dump({"command" : newCommands}, commandsFile)

                self.log.log("Migrated %d commands from old %s to new %s" % \
                        (len(newCommands), self.config.commands_file, self.config.user_commands_file))

            self.log.log("Deleting old " + self.config.commands_file)
            os.remove(old_commands_file_path)

    # Compile regex for all commands before main program start
    def compile(self):
        try:
            for t in self.data:
                # Surround regex with ^ and \s$ to sanitize
                t["re"] = re.compile("^%s\s*$" % t["regex"])
        except re.error as e:
            self.log.log("Error in command regex: %s" % t["regex"])
            raise RegexError(e)

    # Pass through self.data
    def __getitem__(self, key):
        return self.data[key]

    # Pass through self.data
    def __setitem__(self, key, item):
        self.data[key] = item

    # Pass through self.data
    def __contains__(self, key):
        return key in self.data

    # Make iterable
    def __iter__(self):
        return iter(self.data)

