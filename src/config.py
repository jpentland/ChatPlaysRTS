import toml
import pathlib
from appdirs import *
from error import *
from shutil import copytree, rmtree
from monitor import Monitor

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
        },
        "log": {
            "logfile" : "output.log",
        },
        "monitor" : {
            "monitor" : "ALL",
        }
}

configDescriptions = {
        "execution" : {
            "timeout" : "Start skipping commands if they are older than the following number of seconds",
            "defaultDistance" : "Default distance in screen percentage to move the mouse for !mouseup !mousedown etc commands",
            "mouseBorder" : "Size of border around screen where mouse cannot go (in pixels)",
            "clickRateLimit" : "Minimum time in seconds between mouse clicks to prevent accidental doubleclicks",
        },
        "irc" : {
            "domain" : "IRC server to connect to",
            "port" : "IRC port number",
        },
        "log": {
            "logfile" : "Where to store log file",
        },
}

deletedConfigs = {
        "irc" : {
            "PING_MSG" : None,
            "PONG_MSG" : None,
        },
        "log": {
            "echo" : True,
        }
}

# Stores config object and reads from disk
class Config:
    def __init__(self, appname, appauthor, log):
        self.appname = appname
        self.appauthor = appauthor
        self.log = log
        self.config_dir = user_data_dir(appname, appauthor)
        self.config_file = "config.toml"
        self.commands_file = "commands.toml"
        self.user_commands_file = "usercommands.toml"
        self.defaultconf_dir = "defaultconf"
        self.migrateOldConfig()
        self.data = self.loadConfig()
        self.deleteDeletedConfigs()
        self.readCredentials()
        self.monitor = Monitor(self, log)

    # Get contents of config file or defaultconfig if doesnt exist
    def loadConfig(self):
        try:
            with open(os.path.join(self.config_dir, self.config_file)) as configFile:
                content = configFile.read()
                try:
                    config = toml.loads(content)
                except toml.decoder.TomlDecodeError as e:
                    self.log.log("Failed to read %s" % self.config_file)
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

    # Get config descriptions
    def getDescriptions(self):
        return configDescriptions

    # Read credentials from toml
    def readCredentials(self):
        self.username = ""
        self.oauth = ""
        self.remember = False
        if "credentials" in self.data:
            credentials = self.data["credentials"]
            if "username" in credentials:
                self.username = credentials["username"]
            if "oauth" in credentials:
                self.oauth = credentials["oauth"]
            if "remember" in credentials:
                self.remember = credentials["remember"]

    # Write credentials to toml
    def writeCredentials(self):
        if "credentials" not in self.data:
            self.data["credentials"] = {}

        self.data["credentials"]["username"] = self.username
        self.data["credentials"]["oauth"] = self.oauth

        self.write()

    # Set currently used credentials
    def setCredentials(self, username, oauth, remember):
        self.username = username
        self.oauth = oauth
        self.remember = remember
        if self.remember:
            self.writeCredentials()

    # Get currently used credentials
    def getCredentials(self):
        return self.username, self.oauth, self.remember

    # Change remembering of credentials
    def rememberCredentials(self, remember):
        self.remember = remember

    # Migrate old config files from before rename
    def migrateOldConfig(self):
        OLD_APPNAME = "TwitchPlaysRTS"
        OLD_APPAUTHOR = "TwitchPlaysRTS"
        OLD_PATH = user_data_dir(OLD_APPNAME, OLD_APPAUTHOR)

        if os.path.isdir(OLD_PATH) and not os.path.isdir(self.config_dir):
                pathlib.Path(os.path.dirname(self.config_dir)).mkdir(parents=True, exist_ok=True)
                copytree(OLD_PATH, self.config_dir)
                rmtree(OLD_PATH)

    # Delete deleted configs from config
    def deleteDeletedConfigs(self):
        count = 0
        for k, v in deletedConfigs.items():
            if k in self.data:
                if v == None:
                    del self.data[k]
                    self.log.log("Deleting %s from config" % k)
                    count += 1
                    continue
                for k2, v2 in deletedConfigs[k].items():
                    if k2 in self.data[k]:
                        del self.data[k][k2]
                        self.log.log("Deleting %s.%s from config" % (k, k2))
                        count += 1

        if count > 0:
            self.write()

    # Write config to disk
    def write(self):
        config_path = os.path.join(self.config_dir, self.config_file)
        self.log.log("Write config to %s" % config_path)
        pathlib.Path(self.config_dir).mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as configFile:
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

