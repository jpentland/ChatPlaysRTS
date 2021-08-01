import toml
import pathlib
import re
from appdirs import *
from error import *
from shutil import copytree, rmtree
from monitor import Monitor
from threading import RLock

defaultConfig = {
        "execution" : {
            "timeout" : 10,
            "defaultDistance" : 10,
            "mouseBorder" : 11,
            "clickRateLimit" : 0.5,
            "mousespeed" : 0.5,
            "sendStartMessage" : True,
            "startMessage" : "Chat control has started!",
            "stopMessage" : "Chat control has stopped!"
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
        },
        "command" : {
            "commands" : ["default.toml", "usercommands.toml"]
        }
}

configDescriptors = {
        "execution" : {
            "timeout" : {
                "description" : "Start skipping commands if they are older than the following number of seconds",
                "regex" : re.compile("^[0-9\.]+$"),
                "convert" : float
            },
            "defaultDistance" : {
                "description" : "Default distance in screen percentage to move the mouse for !mouseup !mousedown etc commands",
                "regex" : re.compile("^[0-9\.]+$"),
                "convert" : float
            },
            "mouseBorder" : {
                "description" : "Size of border around screen where mouse cannot go (in pixels)",
                "regex" : re.compile("^[0-9]+$"),
                "convert" : int
            },
            "clickRateLimit" : {
                "description" : "Minimum time in seconds between mouse clicks to prevent accidental doubleclicks",
                "regex" : re.compile("^[0-9\.]+$"),
                "convert" : float
            },
            "sendStartMessage" : {
                "description" : "If selected, the chat message will be sent on connect.",
                "regex" : None,
                "convert" : bool
            },
            "mousespeed" : {
                "description" : "Time in seconds that it takes the mouse to move on mouse and box actions.",
                "regex" : re.compile("^[0-9\.]+$"),
                "convert" : float
            },
            "startMessage" : {
                "description" : "Chat message to send when chat control starts",
                "regex" : None,
                "convert" : str
            },
            "stopMessage" : {
                "description" : "Chat message to send when chat control stops",
                "regex" : None,
                "convert" : str
            },
        },
        "irc" : {
            "domain" : {
                "description" : "IRC server to connect to",
                "regex" : re.compile("^[a-zA-Z0-9\.]+$"),
                "convert" : str
            },
            "port" : {
                "description" : "IRC port number",
                "regex" : re.compile("^[0-9]+$"),
                "convert" : int
            },
        },
        "log": {
            "logfile" : {
                "description" : "Where to store log file",
                "regex" : re.compile(".*"),
                "convert" : str
            },
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
        self.lock = RLock()
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

    # Decorator for sync
    def sync(fn):
        def syncfn(self, *args, **kwargs):
            with self.lock:
                result = fn(self, *args, **kwargs)
            return result

        return syncfn

    # Get contents of config file or defaultconfig if doesnt exist
    @sync
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

    # Get config descripors - metadata about config options
    def getDescriptors(self):
        return configDescriptors

    # Get config defaults
    def getDefault(self):
        return defaultConfig

    # Read credentials from toml
    @sync
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
    @sync
    def writeCredentials(self):
        if "credentials" not in self.data:
            self.data["credentials"] = {}

        self.data["credentials"]["username"] = self.username
        self.data["credentials"]["oauth"] = self.oauth

        self.write()

    # Set currently used credentials
    @sync
    def setCredentials(self, username, oauth, remember):
        self.username = username
        self.oauth = oauth
        self.remember = remember
        if self.remember:
            self.writeCredentials()

    # Get currently used credentials
    @sync
    def getCredentials(self):
        return self.username, self.oauth, self.remember

    # Change remembering of credentials
    @sync
    def rememberCredentials(self, remember):
        self.remember = remember

    # Migrate old config files from before rename
    @sync
    def migrateOldConfig(self):
        OLD_APPNAME = "TwitchPlaysRTS"
        OLD_APPAUTHOR = "TwitchPlaysRTS"
        OLD_PATH = user_data_dir(OLD_APPNAME, OLD_APPAUTHOR)

        if os.path.isdir(OLD_PATH) and not os.path.isdir(self.config_dir):
                pathlib.Path(os.path.dirname(self.config_dir)).mkdir(parents=True, exist_ok=True)
                copytree(OLD_PATH, self.config_dir)
                rmtree(OLD_PATH)

    # Delete deleted configs from config
    @sync
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
    @sync
    def write(self):
        config_path = os.path.join(self.config_dir, self.config_file)
        self.log.log("Write config to %s" % config_path)
        pathlib.Path(self.config_dir).mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as configFile:
            toml.dump(self.data, configFile)

    # Pass through self.data
    @sync
    def __getitem__(self, key):
        return self.data[key]

    # Pass through self.data
    @sync
    def __setitem__(self, key, item):
        self.data[key] = item

    # Pass through self.data
    @sync
    def __contains__(self, key):
        return key in self.data

