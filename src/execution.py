import pyautogui as pg
import re
import time

pg.PAUSE = 0
pg.FAILSAFE=False

class Execution():
    def __init__(self, config, commands, irc, log):
        self.config = config["execution"]
        self.screenWidth, self.screenHeight = pg.size()
        self.reEval = re.compile("^\s*{(.*)}\s*$")
        self.lastClick = 0
        self.log = log
        self.commandQueue = irc.commandQueue
        self.commands = commands
        self.irc = irc
        self.reStart = re.compile("^!startcontrol\s*$")
        self.reStop = re.compile("^!stopcontrol\s*$")
        self.timeout = self.config["timeout"]
        self.owner = config["credentials"]["username"]
        self.on = False

        self.operations = {
            "movemouse" : Execution.moveMouse,
            "click" : Execution.click,
            "relmouse" : Execution.relMouse,
            "box" : Execution.box,
            "relbox" : Execution.relBox,
            "presskey" : Execution.pressKey
        }

    # Process an incoming command at runtime
    def processCommand(self, message):
        message = message.lower()
        for command in self.commands:
            match = command["re"].match(message)
            if match != None:
                self.log.log("Got command: %s" % message)
                operation = self.parse_operation(command["operation"])
                try:
                    kwargs = self.processArgs(command["params"], match)
                except KeyError:
                    kwargs = {}
                operation(self, **kwargs)


    # Read commands from command queue
    def processCommandQueue(self):

        self.on = True
        self.irc.sendMessage("Chat control has started!")

        while(True):
            epoch, sender, command = self.irc.receive()

            if sender == self.owner:
                match = self.reStart.match(command)
                if match:
                    self.irc.sendMessage("Chat control has started!")
                    self.on = True
                match = self.reStop.match(command)
                if match:
                    self.irc.sendMessage("Chat control has stopped!")
                    self.on = False

            if self.on:
                age = time.time() - epoch
                if age < self.timeout:
                    self.processCommand(command)
                else:
                    self.log.log("Skipped a command, took too long to come in (%d seconds)" % age)

    # Process args for execution of an incoming command at runtime
    def processArgs(self, kwargs, match):
        newkwArgs = {}
        group = []
        config = self.config

        # Try to convert all matched values to float, if possible
        for g in match.groups():
            try:
                group.append(float(g))
            except ValueError:
                group.append(g)

        # Evaluate all args contained in {} as python code
        for k, arg in kwargs.items():
            try:
                newkwArgs[k] = eval(self.reEval.match(str(arg)).group(1))
            except AttributeError:
                try:
                    newkwArgs[k] = int(arg)
                except (ValueError, TypeError):
                    try:
                        newkwArgs[k] = float(arg)
                    except (ValueError, TypeError):
                        newkwArgs[k] = arg

        return newkwArgs

    # Parse function call and parameters as defined in command config
    def parse_operation(self, fstring):
        return self.operations[fstring.strip().lower()]

    # Convert percentage coordinatre system to actual screen position
    def percentageToPixel(self, x, y):
        return self.screenWidth * (x/100), self.screenHeight * (y/100)

    def keepInsideBorder(self, x, y):
        if x < self.config["mouseBorder"]:
            x = self.config["mouseBorder"]
        if x > self.screenWidth - self.config["mouseBorder"]:
            x = self.screenWidth - self.config["mouseBorder"]
        if y < self.config["mouseBorder"]:
            y = self.config["mouseBorder"]
        if y > self.screenHeight - self.config["mouseBorder"]:
            y = self.screenHeight - self.config["mouseBorder"]

        return x, y

    # Move mouse to location on screen
    def moveMouse(self, x, y):
        x, y = self.percentageToPixel(float(x), float(y))
        x, y = self.keepInsideBorder(x, y)
        pg.moveTo(x, y, 0.5, pg.easeInOutQuad)

    # Move mouse relatively
    def relMouse(self, x, y):
        x, y = self.percentageToPixel(float(x), float(y))
        px, py = pg.position()
        tx, ty = self.keepInsideBorder(px + x, py + y)
        pg.moveTo(tx, ty, 0.5, pg.easeInOutQuad)

    # Draw a box to target position on screen
    def box(self, x, y):
        x, y = self.percentageToPixel(float(x), float(y))
        x, y = self.keepInsideBorder(x, y)
        pg.dragTo(x, y, 0.5, pg.easeInOutQuad)

    # Make box relatively
    def relBox(self, x, y):
        x, y = self.percentageToPixel(float(x), float(y))
        px, py = pg.position()
        tx, ty = self.keepInsideBorder(px + x, py + y)
        pg.dragTo(tx, ty, 0.5, pg.easeInOutQuad)

    # Call pg.click directly
    def click(self, shift = False, ctrl = False, alt = False, *args, **kwargs):
        timeDifference = time.time() - self.lastClick

        mods = zip([ctrl, alt, shift], ["ctrl", "alt","shift"])
        for on, mod in mods:
            if on:
                pg.keyDown(mod)

        if timeDifference < self.config["clickRateLimit"]:
            self.log.log("Sleeping to prevent doubleclick")
            time.sleep(self.config["clickRateLimit"] - timeDifference)

        for on, mod in mods:
            if on:
                pg.keyUp(mod)

        pg.click(*args, **kwargs)
        self.lastClick = time.time()

    # Allow pressing a key
    def pressKey(self, key, shift = False, ctrl = False, alt = False, duration = 0, maxduration = -1):

        # Used to prevent viewers from specifying very large durations
        if maxduration != -1 and maxduration < duration:
            duration = maxduration

        mods = zip([ctrl, alt, shift], ["ctrl", "alt","shift"])
        for on, mod in mods:
            if on:
                pg.keyDown(mod)

        if type(key) is list:
            for k in key:
                pg.keyDown(k)
            if duration > 0:
                time.sleep(duration)
            for k in key:
                pg.keyUp(k)
        else:
            pg.keyDown(key)
            time.sleep(duration)
            pg.keyUp(key)

        for on, mod in mods:
            if on:
                pg.keyUp(mod)

