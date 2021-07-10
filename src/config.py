import toml
import pathlib
from appdirs import *
from error import *

defaultConfig = {
        "execution" : {
            "timeout" : 10,
            "defaultDistance" : 10,
            "mouseBorder" : 11,
            "clickRateLimit" : 0.5,
        },
        "irc" : {
            "domain" : "irc.chat.twitch.tv",
            "port" : 6667,
            "PING_MSG" : "PING :tmi.twitch.tv",
            "PONG_MSG" : "PONG :tmi.twitch.tv"
        },
        "log": {
            "echo" : True,
            "logfile" : "output.log",
        }
}

# Stores config object and reads from disk
class Config:
    def __init__(self, appname, appauthor):
        self.appname = appname
        self.appauthor = appauthor
        self.config_dir = user_data_dir(appname, appauthor)
        self.config_file = "config.toml"
        self.commands_file = "commands.toml"
        self.user_commands_file = "usercommands.toml"
        self.defaultconf_dir = "defaultconf"
        self.data = self.loadConfig()

    # Get contents of config file or defaultconfig if doesnt exist
    def loadConfig(self):
        try:
            with open(os.path.join(self.config_dir, self.config_file)) as configFile:
                content = configFile.read()
                try:
                    config = toml.loads(content)
                except toml.decoder.TomlDecodeError as e:
                    print("Failed to read %s" % self.config_file)
                    raise TomlError(e)

                # Copy any missing default config options
                for k, v in defaultConfig.items():
                    for ki, vi in v.items():
                        if k in config:
                            if ki not in config[k]:
                                config[k][ki] = vi
                        else:
                            config[k] = v

                return config

        except FileNotFoundError:
            return defaultConfig

    # Write config to disk
    def write(self):
        pathlib.Path(self.config_dir).mkdir(parents=True, exist_ok=True)
        with open(os.path.join(self.config_dir, self.config_file), "w") as configFile:
            toml.dump(self.data, configFile)

    # Pass through self.data
    def __getitem__(self, key):
        return self.data[key]

    # Pass through self.data
    def __setitem__(self, key, item):
        self.data[key] = item

    # Pass through self.data
    def __contains__(self, key):
        return key in self.data

