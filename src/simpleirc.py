import threading
import socket
import time
import re
from queue import Queue
from error import *

class SimpleIrc(threading.Thread):

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
        self.connected = False
        self.clientDisconnect = False

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
                    raise ClientDisconnectError()
                elif triesLeft == 1:
                    self.log.log_exception(e)
                    raise ConnectionFailedError(e)
                else:
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
        while True:
            message = self.server.recv(2048).decode('utf-8')
            if len(message) == 0:
                raise Exception("connection failed")

            for msg in message.split("\n"):
                #Check for connected message
                regex = ":[^ ]+ [0-9]+ " + self.username + " " + self.channel + " :End of /NAMES list"
                if re.match(regex, msg):
                    self.log.log("Connected")
                    threading.Thread.start(self)
                    return

                # Check for invalid oauth
                regex = ".*Login authentication failed"
                if re.match(regex, msg.strip()):
                    raise AuthenticationError()

                # Check for invalid username
                # invalid username means wrong username will be returned from server
                match = re.match(":[^ ]+ [0-9]+ (.*) :>", msg)
                if match != None:
                    if match.group(1) != self.username:
                        raise AuthenticationError()

    def run(self):

        while True:
            try:
                message = self.server.recv(2048).decode('utf-8')
                if len(message) == 0:
                    self.log.log("Connection to %s terminated" % self.domain)
                    self.commandQueue.put((time.time(), None, "Disconnected"))
                    self.connected = False
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
                self.connected = False
                return


    def send(self, string):
        self.server.send(bytes(string + '\r\n', 'utf-8'))

    def receive(self):
        epoch, sender, command = self.commandQueue.get()
        if sender == None:
            if self.clientDisconnect == True:
                raise ClientDisconnectError()
            else:
                raise ConnectionFailedError(command)

        return epoch, sender, command

    def close(self):
        self.clientDisconnect = True
        self.server.shutdown(socket.SHUT_RDWR)
        self.connected = False
