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
            match = command["regex"].match(message)
            if match != None:
                print("Matched message: %s" % message)
                operation = self.parse_operation(command["command"])
                kwargs = self.processArgs(command["params"], match)
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

    # Parse function call and parameters as defined in command config
    def parse_operation(self, fstring):
        return self.operations[fstring.strip().lower()]

defaultCommands = [
        {"regex" : "!(?:movemouse|mouse) ([0-9\.]+) ([0-9\.]+)",      "command" : "moveMouse",        "params" : {"x" : "{group[0]}", "y" : "{group[1]}"}},
        {"regex" : "!box (-?[0-9\.]+) (-?[0-9\.]+)",                  "command" : "box",              "params" : {"x" : "{group[0]}", "y" : "{group[1]}"}},
        {"regex" : "!(?:click|leftclick)",                            "command" : "click",            "params" : {}},
        {"regex" : "!rightclick",                                     "command" : "click",            "params" : {"button" : "right"}},
        {"regex" : "!middleclick",                                    "command" : "click",            "params" : {"button" : "middle"}},
        {"regex" : "!doubleclick",                                    "command" : "click",            "params" : {"clicks" : 2}},
        {"regex" : "!mouseup",                                        "command" : "relMouse",         "params" : {"x" : 0, "y" : "{-config['defaultDistance']}"}},
        {"regex" : "!mouseup ([0-9\.]+)",                             "command" : "relMouse",         "params" : {"x" : 0, "y" : "{-group[0]}"}},
        {"regex" : "!mousedown",                                      "command" : "relMouse",         "params" : {"x" : 0, "y" : "{config['defaultDistance']}"}},
        {"regex" : "!mousedown ([0-9\.]+)",                           "command" : "relMouse",         "params" : {"x" : 0, "y" : "{group[0]}"}},
        {"regex" : "!mouseleft",                                      "command" : "relMouse",         "params" : {"x" : "{-config['defaultDistance']}", "y" : 0}},
        {"regex" : "!mouseleft ([0-9\.]+)",                           "command" : "relMouse",         "params" : {"x" : "{-group[0]}", "y" : 0}},
        {"regex" : "!mouseright",                                     "command" : "relMouse",         "params" : {"x" : "{config['defaultDistance']}", "y" : 0}},
        {"regex" : "!mouseright ([0-9\.]+)",                          "command" : "relMouse",         "params" : {"x" : "{group[0]}", "y" : 0}},
        {"regex" : "!mouseupleft",                                    "command" : "relMouse",         "params" : {"x" : "{-config['defaultDistance']}", "y" : "{-config['defaultDistance']}"}},
        {"regex" : "!mouseupleft ([0-9\.]+)",                         "command" : "relMouse",         "params" : {"x" : "{-group[0]}", "y" : "{-group[0]}"}},
        {"regex" : "!mouseupright",                                   "command" : "relMouse",         "params" : {"x" : "{config['defaultDistance']}", "y" : "{-config['defaultDistance']}"}},
        {"regex" : "!mouseupright ([0-9\.]+)",                        "command" : "relMouse",         "params" : {"x" : "{group[0]}", "y" : "{-group[0]}"}},
        {"regex" : "!mousedownleft",                                  "command" : "relMouse",         "params" : {"x" : "{-config['defaultDistance']}", "y" : "{config['defaultDistance']}"}},
        {"regex" : "!mousedownleft ([0-9\.]+)",                       "command" : "relMouse",         "params" : {"x" : "{-group[0]}", "y" : "{group[0]}"}},
        {"regex" : "!mousedownright",                                 "command" : "relMouse",         "params" : {"x" : "{config['defaultDistance']}", "y" : "{config['defaultDistance']}"}},
        {"regex" : "!mousedownright ([0-9\.]+)",                      "command" : "relMouse",         "params" : {"x" : "{group[0]}", "y" : "{group[0]}"}},
        {"regex" : "!boxupleft",                                      "command" : "box",              "params" : {"x" : "{-config['defaultDistance']}", "y" : "{-config['defaultDistance']}"}},
        {"regex" : "!boxupleft ([0-9\.]+)",                           "command" : "box",              "params" : {"x" : "{-group[0]}", "y" : "{-group[0]}"}},
        {"regex" : "!boxupright",                                     "command" : "box",              "params" : {"x" : "{config['defaultDistance']}", "y" : "{-config['defaultDistance']}"}},
        {"regex" : "!boxupright ([0-9\.]+)",                          "command" : "box",              "params" : {"x" : "{group[0]}", "y" : "{-group[0]}"}},
        {"regex" : "!boxdownleft",                                    "command" : "box",              "params" : {"x" : "{-config['defaultDistance']}", "y" : "{config['defaultDistance']}"}},
        {"regex" : "!boxdownleft ([0-9\.]+)",                         "command" : "box",              "params" : {"x" : "{-group[0]}", "y" : "{group[0]}"}},
        {"regex" : "!boxdownright",                                   "command" : "box",              "params" : {"x" : "{config['defaultDistance']}", "y" : "{config['defaultDistance']}"}},
        {"regex" : "!boxdownright ([0-9\.]+)",                        "command" : "box",              "params" : {"x" : "{group[0]}", "y" : "{group[0]}"}},
]

