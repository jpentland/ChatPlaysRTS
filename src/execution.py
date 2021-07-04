import pyautogui as pg
import re

pg.PAUSE = 0
pg.FAILSAFE=False

class Execution():
    def __init__(self, config, commands):
        self.config = config["execution"]
        self.commands = self.compileCommands(commands)
        self.screenWidth, self.screenHeight = pg.size()
        self.reEval = re.compile("^\s*{(.*)}\s*$")

        self.operations = {
            "movemouse" : Execution.moveMouse,
            "click" : Execution.click,
            "relmouse" : Execution.relMouse,
            "box" : Execution.box,
            "presskey" : Execution.pressKey
        }

    # Process an incoming command at runtime
    def processCommand(self, message):
        message = message.lower()
        for command in self.commands:
            match = command["regex"].match(message)
            if match != None:
                print("Matched message: %s" % message)
                operation = self.parse_operation(command["operation"])
                try:
                    kwargs = self.processArgs(command["params"], match)
                except KeyError:
                    kwargs = {}
                operation(self, **kwargs)

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
                newkwArgs[k] = arg

        return newkwArgs

    # Compile regex for all commands before main program start
    def compileCommands(self, commands):
        for t in commands:
            # Surround regex with ^ and \s$ to sanitize
            t["regex"] = re.compile("^%s\s*$" % t["regex"])

        return commands

    # Parse function call and parameters as defined in command config
    def parse_operation(self, fstring):
        return self.operations[fstring.strip().lower()]

    # Convert percentage coordinatre system to actual screen position
    def percentageToPixel(self, x, y):
        return self.screenWidth * (x/100), self.screenHeight * (y/100)

    # Move mouse to location on screen
    def moveMouse(self, x, y):
        x, y = self.percentageToPixel(float(x), float(y))
        pg.moveTo(x, y, 0.5, pg.easeInOutQuad)

    # Move mouse relatively
    def relMouse(self, x, y):
        x, y = self.percentageToPixel(float(x), float(y))
        pg.moveRel(x, y, 0.5, pg.easeInOutQuad)

    # Draw a box relatively
    def box(self, x, y):
        x, y = self.percentageToPixel(float(x), float(y))
        pg.dragRel(x, y, 0.5, pg.easeInOutQuad)

    # Call pg.click directly
    def click(self, *args, **kwargs):
        pg.click(*args, **kwargs)

    # Allow pressing a key
    def pressKey(self, key, shift = False, ctrl = False, alt = False):
        mods = zip([ctrl, alt, shift], ["ctrl", "alt","shift"])
        for on, mod in mods:
            if on:
                print("Keydown %s" % mod)
                pg.keyDown(mod)

        print("presskey %s" % key)
        pg.press(key)

        for on, mod in mods:
            if on:
                print("Keyup %s" % mod)
                pg.keyUp(mod)

