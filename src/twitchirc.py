import threading
import socket
import time
import re
from queue import Queue

class TwitchIrc(threading.Thread):

    def __init__(self, config):
        threading.Thread.__init__(self)
        self.username = config["credentials"]["username"]
        self.channel = "#" + config["credentials"]["username"]
        self.oauth = config["credentials"]["oauth"]
        self.domain = config["irc"]["domain"]
        self.port = config["irc"]["port"]
        self.PING_MSG = config["irc"]["PING_MSG"]
        self.PONG_MSG = config["irc"]["PONG_MSG"]
        self.reMessage = re.compile(":([^\s]+)!.* PRIVMSG " + self.channel + " :(.*)")
        self.commandQueue = Queue()

    def sendMessage(self, message):
        send = "PRIVMSG " + self.channel + " :" + message
        print(send)
        self.send(send)

    def start(self):
        connection_data = (self.domain, self.port)
        try:
            print("Server: %s:%d" % (self.domain, self.port))
            print("Username: " + self.username)
            print("Channel: " + self.channel)
            print("Connecting...")
            self.server = socket.socket()
            self.server.connect(connection_data)
            self.send('PASS ' + self.oauth)
            self.send('NICK ' + self.username)
            self.send('JOIN ' + self.channel)
            while True:
                message = self.server.recv(2048).decode('utf-8')
                if len(message) == 0:
                    print("Connection failed")
                    raise Exception("connection failed")

                for msg in message.split("\n"):
                    regex = ":[^ ]+ [0-9]+ " + self.username + " " + self.channel + " :End of /NAMES list"
                    if re.match(regex, msg):
                        print("Connected")
                        threading.Thread.start(self)
                        return
        except:
            raise Exception("Connection failed")
            return False

    def run(self):

        while True:
            try:
                message = self.server.recv(2048).decode('utf-8')
                if len(message) == 0:
                    print("Connection to twitch terminated")
                    self.commandQueue.put((time.time(), None, "Disconnected"))
                    self.server.close()
                    return

                elif (self.PING_MSG[:4] == message[:4]):
                    print("twitch pinged")
                    print(repr(message))
                    self.send(self.PONG_MSG)

                else:
                    match = self.reMessage.match(message)
                    if match != None:
                        print("%s: %s" % (match.group(1), match.group(2)))
                        self.commandQueue.put((time.time(), match.group(1), match.group(2)))
                    else:
                        print(message)

            except Exception as error:
                print("Error type: ", type(error))
                print(error.args)
                self.commandQueue.put((time.time(), None, error.args))
                self.server.close()
                return


    def send(self, string):
        self.server.send(bytes(string + '\r\n', 'utf-8'))
