import pyautogui as pg
import re
import time

pg.PAUSE = 0
pg.FAILSAFE=False

class Execution():
    def __init__(self, config, commands, irc, log):
        self.config = config["execution"]
        self.reEval = re.compile("^\s*{(.*)}\s*$")
        self.lastClick = 0
        self.log = log
        self.commandQueue = irc.commandQueue
        self.commands = commands
        self.irc = irc
        self.reStart = re.compile("^!startcontrol\s*$")
        self.reStop = re.compile("^!stopcontrol\s*$")
        self.reRestrict = re.compile("^!restrict ([a-z\-,]+)\s*$")
        self.reUnrestrict = re.compile("^!unrestrict")
        self.timeout = self.config["timeout"]
        self.owner = config["credentials"]["username"]
        self.on = False
        self.monitor = config.monitor
        self.restrict = None

        self.operations = {
            "movemouse" : Execution.moveMouse,
            "click" : Execution.click,
            "relmouse" : Execution.relMouse,
            "box" : Execution.box,
            "relbox" : Execution.relBox,
            "presskey" : Execution.pressKey
        }

    # Process an incoming command at runtime
    def processCommand(self, message, badges, bits):
        message = message.lower()
        for command in self.commands:
            match = command["re"].match(message)
            if match != None:
                if self.commandAuthorized(command, badges, bits):
                    self.log.log(f"Got command: {message}")
                    if type(command["operation"]) is str:
                        self.performSingleOperation(command, match)
                    elif type(command["operation"]) is list:
                        self.performMultipleOperations(command, match)
                    else:
                        raise TomlError("Invalid operation type")
                    break
                else:
                    self.log.log(f"Command not allowed: {message}")

    # Check whether command is authorized (required badges or min bits)
    def commandAuthorized(self, command, badges, bits):

        allowed = True

        if "badges" in command and set(command["badges"]).isdisjoint(set(badges)):
            allowed = False

        if "bits" in command and bits < int(command["bits"]):
            allowed = False

        if self.restrict != None and set(self.restrict).isdisjoint(set(badges)):
            allowed = False

        return allowed

    # Perform a single operation (legacy format)
    def performSingleOperation(self, command, match):
        op_func = self.parse_operation(command["operation"])
        try:
            kwargs = self.processArgs(command["params"], match)
        except KeyError:
            kwargs = {}
        op_func(self, **kwargs)

    # Perform multiple operations (new format)
    def performMultipleOperations(self, command, match):
        for operation in command["operation"]:
            op_func = self.parse_operation(operation["operation"])
            try:
                kwargs = self.processArgs(operation["params"], match)
            except KeyError:
                kwargs = {}

            op_func(self, **kwargs)

    # Read commands from command queue
    def processCommandQueue(self):

        self.on = True
        if self.config["sendStartMessage"]:
            self.irc.sendMessage(self.config["startMessage"])

        while(True):
            epoch, sender, command, badges, bits = self.irc.receive()

            # broadcaster and moderator only commands
            if not set(badges).isdisjoint(set(["broadcaster", "moderator"])):

                # !startcontrol
                match = self.reStart.match(command)
                if match:
                    if self.config["sendStartMessage"]:
                        self.irc.sendMessage(self.config["startMessage"])
                    self.on = True

                # !stopcontrol
                match = self.reStop.match(command)
                if match:
                    if self.config["sendStartMessage"]:
                        self.irc.sendMessage(self.config["stopMessage"])
                    self.on = False

                # !restrict
                match = self.reRestrict.match(command)
                if match:
                    self.irc.sendMessage(f"Chat controls restricted to: {match.group(1)}")
                    self.restrict = match.group(1).split(",")

                # !unrestrict
                match = self.reUnrestrict.match(command)
                if match:
                    self.irc.sendMessage("Chat control unrestricted")
                    self.restrict = None

            if self.on:
                age = time.time() - epoch
                if age < self.timeout:
                    self.processCommand(command, badges, bits)
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
        width, height = self.monitor.getScreenSize()
        xOff, yOff = self.monitor.getScreenOffset()
        return width * (x/100) + xOff, height * (y/100) + yOff

    # Convert percentage coordinatre system to pixel distance
    def relPercentageToPixel(self, x, y):
        width, height = self.monitor.getScreenSize()
        return width * (x/100), height * (y/100)

    def keepInsideBorder(self, x, y):
        border = self.config["mouseBorder"]
        width, height = self.monitor.getScreenSize()
        xOff, yOff = self.monitor.getScreenOffset()
        if x < border + xOff:
            x = border + xOff
        if x > width - border + xOff:
            x = width - border + xOff
        if y < border + yOff:
            y = border + yOff
        if y > height - border + yOff:
            y = height - border + yOff

        return x, y

    # Move mouse to location on screen
    def moveMouse(self, x, y):
        x, y = self.percentageToPixel(float(x), float(y))
        x, y = self.keepInsideBorder(x, y)
        pg.moveTo(x, y, 0.5, pg.easeInOutQuad)

    # Move mouse relatively
    def relMouse(self, x, y):
        x, y = self.relPercentageToPixel(float(x), float(y))
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
        x, y = self.relPercentageToPixel(float(x), float(y))
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

