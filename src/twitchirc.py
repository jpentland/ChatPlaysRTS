import threading
import socket
import time
import re
from queue import Queue

class AuthenticationError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ConnectionFailedError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class TwitchIrc(threading.Thread):

    def __init__(self, config, log):
        threading.Thread.__init__(self, daemon = True)
        self.username = config["credentials"]["username"]
        self.channel = "#" + config["credentials"]["username"]
        self.oauth = config["credentials"]["oauth"]
        self.domain = config["irc"]["domain"]
        self.port = config["irc"]["port"]
        self.PING_MSG = config["irc"]["PING_MSG"]
        self.PONG_MSG = config["irc"]["PONG_MSG"]
        self.reMessage = re.compile(":([^\s]+)!.* PRIVMSG " + self.channel + " :(.*)")
        self.commandQueue = Queue()
        self.log = log

    def sendMessage(self, message):
        send = "PRIVMSG " + self.channel + " :" + message
        self.log.log("Sending: " + message)
        self.send(send)

    def connect(self, tries):
        triesLeft = tries
        while triesLeft > 0:
            try:
                self.start()
                break
            except AuthenticationError as e:
                raise e
            except Exception as e:
                if triesLeft == 1:
                    self.log.log_exception(e)
                    raise ConnectionFailedError()
                else:
                    triesLeft -= 1
                    self.log.log("retrying...")

    def start(self):
        connection_data = (self.domain, self.port)
        self.log.log("Server: %s:%d" % (self.domain, self.port))
        self.log.log("Username: " + self.username)
        self.log.log("Channel: " + self.channel)
        self.log.log("Connecting...")
        self.server = socket.socket()
        self.server.connect(connection_data)
        self.send('PASS ' + self.oauth)
        self.send('NICK ' + self.username)
        self.send('JOIN ' + self.channel)
        while True:
            message = self.server.recv(2048).decode('utf-8')
            if len(message) == 0:
                raise Exception("connection failed")

            for msg in message.split("\n"):
                regex = ":[^ ]+ [0-9]+ " + self.username + " " + self.channel + " :End of /NAMES list"
                if re.match(regex, msg):
                    self.log.log("Connected")
                    threading.Thread.start(self)
                    return

                regex = ".*Login authentication failed"
                if re.match(regex, msg.strip()):
                    raise AuthenticationError()

    def run(self):

        while True:
            try:
                message = self.server.recv(2048).decode('utf-8')
                if len(message) == 0:
                    self.log.log("Connection to twitch terminated")
                    self.commandQueue.put((time.time(), None, "Disconnected"))
                    self.server.close()
                    return

                elif (self.PING_MSG[:4] == message[:4]):
                    self.log.log("Responding to PING")
                    self.log.log(repr(message))
                    self.send(self.PONG_MSG)

                else:
                    match = self.reMessage.match(message)
                    if match != None:
                        self.log.log("%s: %s" % (match.group(1), match.group(2)))
                        self.commandQueue.put((time.time(), match.group(1), match.group(2)))
                    else:
                        self.log.log(message)

            except Exception as error:
                self.log.log(e)
                self.commandQueue.put((time.time(), None, error.args))
                self.server.close()
                return


    def send(self, string):
        self.server.send(bytes(string + '\r\n', 'utf-8'))
