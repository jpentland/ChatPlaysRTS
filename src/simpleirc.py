import threading
import socket
import time
import re
from queue import Queue
from error import *

class SimpleIrc(threading.Thread):

    def __init__(self, config, log):
        threading.Thread.__init__(self, daemon = True)
        self.username, self.oauth, _ = config.getCredentials()
        self.channel = f"#{self.username}"
        self.domain = config["irc"]["domain"]
        self.port = config["irc"]["port"]
        self.reMessage = re.compile(r"@(.*):([^\s]+)!.* PRIVMSG " + self.channel + " :(.*)")
        self.commandQueue = Queue()
        self.log = log
        self.connected = False
        self.clientDisconnect = False
        self.buff = ""
        self.server = None

    def sendMessage(self, message):
        send = "PRIVMSG " + self.channel + " :" + message
        self.log.log("Sending: " + message)
        self.send(send)

    def connect(self, tries):
        self.clientDisconnect = False
        triesLeft = tries
        while triesLeft > 0:
            try:
                self.start()
                break
            except AuthenticationError as e:
                raise e
            except Exception as e:
                if self.clientDisconnect:
                    self.log.log("Connection aborted")
                    raise ClientDisconnectError from e

                if triesLeft == 1:
                    self.log.log_exception(e)
                    raise ConnectionFailedError from e

                triesLeft -= 1
                self.log.log("retrying...")

        self.connected = True

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
        self.send('CAP REQ :twitch.tv/tags')
        while True:
            message = self.readline().strip()
            if not message:
                raise Exception("connection failed")

            #Check for connected message
            regex = ":[^ ]+ [0-9]+ " + self.username + " " + self.channel + " :End of /NAMES list"
            if re.match(regex, message):
                self.log.log("Connected")
                threading.Thread.start(self)
                return

            # Check for invalid oauth
            regex = ".*Login authentication failed"
            if re.match(regex, message.strip()):
                raise AuthenticationError()

            # Check for invalid username
            # invalid username means wrong username will be returned from server
            match = re.match(":[^ ]+ [0-9]+ (.*) :>", message)
            if match:
                if match.group(1) != self.username:
                    raise AuthenticationError()

    def run(self):

        while True:
            try:
                string = self.readline()
                if not string:
                    self.log.log("Connection to %s terminated" % self.domain)
                    self.commandQueue.put((time.time(), None, "Disconnected"))
                    self.connected = False
                    self.server.close()
                    return

                if string[:4] == "PING":
                    self.log.log("Got ping: %s" % repr(string))
                    pong = "PONG" + string[4:]
                    self.log.log("Responding to PING")
                    self.log.log("Responding: %s" % repr(pong))
                    self.send(pong)
                else:
                    result = self.parse_privmsg(string)
                    if result is not None:
                        username, message, badges, bits = result
                        self.log_privmsg(username, message, badges, bits)
                        self.commandQueue.put((time.time(), username, (message, badges, bits)))
                    else:
                        self.log.log(string)

            except UnicodeEncodeError:
                self.log.log("WARNING: UnicodeEncodeError when trying to read chat message")

            except Exception as error:
                self.log.log_exception(error)
                self.commandQueue.put((time.time(), None, error.args))
                self.server.close()
                self.connected = False
                return

    def log_privmsg(self, username, message, badges, bits):
        badgelog = ""
        for badge in badges:
            badgelog += f"{badge},"
        badgelog = badgelog[:-1]

        message = f"[{badgelog}] {username}: {message}"
        if bits > 0:
            message += f" [BITS: {bits}]"

        self.log.log(message)

    def parse_privmsg(self, string):
        match = self.reMessage.match(string)
        if match is None:
            return None

        taglist = match.group(1)
        username = match.group(2)
        message = match.group(3)

        tags = {}
        for tag in taglist.split(";"):
            kv = tag.split("=")
            tags[kv[0]] = kv[1]

        badges = []
        for badge in tags["badges"].split(","):
            badges.append(badge.split("/")[0])

        bits = 0
        try:
            bits = int(tags["bits"])
        except KeyError:
            pass

        return username, message, badges, bits

    def readline(self):
        while True:
            split = re.split("[\r\n]+", self.buff)
            if len(split) > 1:
                self.buff = '\n'.join(split[1:])
                return split[0]

            recv = self.server.recv(1024)
            if not recv:
                return self.buff
            self.buff += recv.decode("utf-8")

    def send(self, string):
        self.server.send(bytes(string + '\r\n', 'utf-8'))

    def receive(self):
        epoch, sender, info = self.commandQueue.get()
        if sender is None:
            if self.clientDisconnect:
                raise ClientDisconnectError()
            raise ConnectionFailedError(info)

        message, badges, bits = info

        return epoch, sender, message, badges, bits

    def close(self):
        self.clientDisconnect = True
        self.server.shutdown(socket.SHUT_RDWR)
        self.connected = False
