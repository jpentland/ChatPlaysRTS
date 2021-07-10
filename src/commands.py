import os
import toml

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

    def loadCommands(self):
        if os.path.isfile(os.path.join(self.config.config_dir, self.config.commands_file)):
            self.migrateOldCommands()

        with open(self.commands_file_path) as commandsFile:
                content = commandsFile.read()
                defaultCommands = toml.loads(content)["command"]
                self.data += defaultCommands
        try:
            with open(self.user_commands_file_path) as commandsFile:
                content = commandsFile.read()
                userCommands = toml.loads(content)["command"]
                self.log.log("Loaded %d custom commands from %s" \
                        % (len(userCommands), self.config.user_commands_file))
                self.data += userCommands
        except FileNotFoundError:
            self.log.log("No user commands file found")

    # Migrate old commands file (pre v0.8)
    def migrateOldCommands():
        defaultCommands = []
        oldCommands = []
        newCommands = []
        old_commands_file_path = os.path.join(
                self.config.config_dir,
                self.config.commands_file
        )

        with open(self.commands_file_path) as commandsFile:
                content = commandsFile.read()
                defaultCommands += toml.loads(content)["command"]

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

            self.log.log("Migrated %d commands from old commands.toml to new user_commands.toml" % len(newCommands))

        self.log.log("Deleting old " + commands_file)
        os.remove(self.old_commands_file_path)

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

