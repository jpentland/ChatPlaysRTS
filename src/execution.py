import pyautogui as pg
import re

pg.PAUSE = 0
pg.FAILSAFE=False

class Execution():
    def __init__(self, config):
        self.config = config["execution"]
        self.commands = self.compileCommands(defaultCommands)
        self.screenWidth, self.screenHeight = pg.size()
        self.reEval = re.compile("^\s*{(.*)}\s*$")

        self.operations = {
            "movemouse" : Execution.moveMouse,
            "click" : Execution.click,
            "relmouse" : Execution.relMouse,
            "box" : Execution.box,
        }

    # Process an incoming command at runtime
    def processCommand(self, message):
        message = message.lower()
        for command in self.commands:
            match = command[0].match(message)
            if match != None:
                print("Matched message: %s" % message)
                operation = self.parse_operation(command[1])
                kwargs = self.processArgs(command[2], match)
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
            t[0] = re.compile("^%s\s*$" % t[0])

        return commands

    # Negate incoming parameter
    def negate(self, a):
        return -float(a)

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

    # Return same value that was passed in (no effect)
    def unary(self, x):
        return x

    # Call pg.click directly
    def click(self, *args, **kwargs):
        pg.click(*args, **kwargs)

    # Parse function call and parameters as defined in command config
    def parse_operation(self, fstring):
        return self.operations[fstring.strip().lower()]

defaultCommands = [
        ["!(?:movemouse|mouse) ([0-9\.]+) ([0-9\.]+)",      "moveMouse",        {"x" : "{group[0]}", "y" : "{group[1]}"}],
        ["!box (-?[0-9\.]+) (-?[0-9\.]+)",                  "box",              {"x" : "{group[0]}", "y" : "{group[1]}"}],
        ["!(?:click|leftclick)",                            "click",            {}],
        ["!rightclick",                                     "click",            {"button" : "right"}],
        ["!middleclick",                                    "click",            {"button" : "middle"}],
        ["!doubleclick",                                    "click",            {"clicks" : 2}],
        ["!mouseup",                                        "relMouse",         {"x" : 0, "y" : "{-config['defaultDistance']}"}],
        ["!mouseup ([0-9\.]+)",                             "relMouse",         {"x" : 0, "y" : "{-group[0]}"}],
        ["!mousedown",                                      "relMouse",         {"x" : 0, "y" : "{config['defaultDistance']}"}],
        ["!mousedown ([0-9\.]+)",                           "relMouse",         {"x" : 0, "y" : "{group[0]}"}],
        ["!mouseleft",                                      "relMouse",         {"x" : "{-config['defaultDistance']}", "y" : 0}],
        ["!mouseleft ([0-9\.]+)",                           "relMouse",         {"x" : "{-group[0]}", "y" : 0}],
        ["!mouseright",                                     "relMouse",         {"x" : "{config['defaultDistance']}", "y" : 0}],
        ["!mouseright ([0-9\.]+)",                          "relMouse",         {"x" : "{group[0]}", "y" : 0}],
        ["!mouseupleft",                                    "relMouse",         {"x" : "{-config['defaultDistance']}", "y" : "{-config['defaultDistance']}"}],
        ["!mouseupleft ([0-9\.]+)",                         "relMouse",         {"x" : "{-group[0]}", "y" : "{-group[0]}"}],
        ["!mouseupright",                                   "relMouse",         {"x" : "{config['defaultDistance']}", "y" : "{-config['defaultDistance']}"}],
        ["!mouseupright ([0-9\.]+)",                        "relMouse",         {"x" : "{group[0]}", "y" : "{-group[0]}"}],
        ["!mousedownleft",                                  "relMouse",         {"x" : "{-config['defaultDistance']}", "y" : "{config['defaultDistance']}"}],
        ["!mousedownleft ([0-9\.]+)",                       "relMouse",         {"x" : "{-group[0]}", "y" : "{group[0]}"}],
        ["!mousedownright",                                 "relMouse",         {"x" : "{config['defaultDistance']}", "y" : "{config['defaultDistance']}"}],
        ["!mousedownright ([0-9\.]+)",                      "relMouse",         {"x" : "{group[0]}", "y" : "{group[0]}"}],
        ["!boxupleft",                                      "box",              {"x" : "{-config['defaultDistance']}", "y" : "{-config['defaultDistance']}"}],
        ["!boxupleft ([0-9\.]+)",                           "box",              {"x" : "{-group[0]}", "y" : "{-group[0]}"}],
        ["!boxupright",                                     "box",              {"x" : "{config['defaultDistance']}", "y" : "{-config['defaultDistance']}"}],
        ["!boxupright ([0-9\.]+)",                          "box",              {"x" : "{group[0]}", "y" : "{-group[0]}"}],
        ["!boxdownleft",                                    "box",              {"x" : "{-config['defaultDistance']}", "y" : "{config['defaultDistance']}"}],
        ["!boxdownleft ([0-9\.]+)",                         "box",              {"x" : "{-group[0]}", "y" : "{group[0]}"}],
        ["!boxdownright",                                   "box",              {"x" : "{config['defaultDistance']}", "y" : "{config['defaultDistance']}"}],
        ["!boxdownright ([0-9\.]+)",                        "box",              {"x" : "{group[0]}", "y" : "{group[0]}"}],
]

