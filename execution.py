import pyautogui as pg
import re

pg.PAUSE = 0
pg.FAILSAFE=False

class Execution():
    def __init__(self, config):
        self.config = config["execution"]
        self.commands = self.compileCommands(defaultCommands)
        self.screenWidth, self.screenHeight = pg.size()

    # Process an incoming command at runtime
    def processCommand(self, message):
        for command in self.commands:
            match = command[0].match(message)
            if match != None:
                print("Matched message: %s" % message)
                args = self.processArgs(command[2], match)
                command[1](self, *args, **command[3])

    # Process args for execution of an incoming command at runtime
    def processArgs(self, args, match):
        newArgs = []
        for arg in args:
            # All params use f, because f defaults to unary
            if type(arg) is ReParam:
                newArgs.append(arg.f(self, match.group(arg.index)))
            elif type(arg) is ConfigParam:
                newArgs.append(arg.f(self, self.config[arg.name]))
            else:
                newArgs.append(arg)

        return newArgs

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

class ReParam:
    # Parameter is a regex group, with index i, goes through function f
    def __init__(self, index, f = Execution.unary):
        self.index = index
        self.f = f

class ConfigParam:
    # Parameter is a config option, with index i, goes through function f
    def __init__(self, name, f = Execution.unary):
        self.name = name
        self.f = f

defaultCommands = [
        ["!(?:movemouse|mouse) ([0-9\.]+) ([0-9\.]+)", Execution.moveMouse, [ReParam(1), ReParam(2)], {}],
        ["!box (-?[0-9\.]+) (-?[0-9\.]+)", Execution.box, [ReParam(1), ReParam(2)], {}],
        ["!(?:click|leftclick)",  Execution.click, [], {}],
        ["!rightclick", Execution.click, [], {"button" : "right"}],
        ["!middleclick", Execution.click, [], {"button" : "middle"}],
        ["!doubleclick", Execution.click, [], {"clicks" : 2}],
        ["!mouseup", Execution.relMouse, [0, ConfigParam("defaultDistance", f = Execution.negate)], {}],
        ["!mouseup ([0-9\.]+)", Execution.relMouse, [0, ReParam(1, f = Execution.negate)], {}],
        ["!mousedown", Execution.relMouse, [0, ConfigParam("defaultDistance")], {}],
        ["!mousedown ([0-9\.]+)", Execution.relMouse, [0, ReParam(1)], {}],
        ["!mouseleft", Execution.relMouse, [ConfigParam("defaultDistance", f = Execution.negate), 0], {}],
        ["!mouseleft ([0-9\.]+)", Execution.relMouse, [ReParam(1, f = Execution.negate), 0], {}],
        ["!mouseright", Execution.relMouse, [ConfigParam("defaultDistance"), 0], {}],
        ["!mouseright ([0-9\.]+)", Execution.relMouse, [ReParam(1), 0], {}],
        ["!mouseupleft", Execution.relMouse, [ConfigParam("defaultDistance", f = Execution.negate), ConfigParam("defaultDistance", f = Execution.negate)], {}],
        ["!mouseupleft ([0-9\.]+)", Execution.relMouse, [ReParam(1, f = Execution.negate), ReParam(1, f = Execution.negate)], {}],
        ["!mouseupright", Execution.relMouse, [ConfigParam("defaultDistance"), ConfigParam("defaultDistance", f = Execution.negate)], {}],
        ["!mouseupright ([0-9\.]+)", Execution.relMouse, [ReParam(1), ReParam(1, f = Execution.negate)], {}],
        ["!mousedownleft", Execution.relMouse, [ConfigParam("defaultDistance", f = Execution.negate), ConfigParam("defaultDistance")], {}],
        ["!mousedownleft ([0-9\.]+)", Execution.relMouse, [ReParam(1, f = Execution.negate), ReParam(1)], {}],
        ["!mousedownright", Execution.relMouse, [ConfigParam("defaultDistance"), ConfigParam("defaultDistance")], {}],
        ["!mousedownright ([0-9\.]+)", Execution.relMouse, [ReParam(1), ReParam(1)], {}],
        ["!boxupleft", Execution.box, [ConfigParam("defaultDistance", f = Execution.negate), ConfigParam("defaultDistance", f = Execution.negate)], {}],
        ["!boxupleft ([0-9\.]+)", Execution.box, [ReParam(1, f = Execution.negate), ReParam(1, f = Execution.negate)], {}],
        ["!boxupright", Execution.box, [ConfigParam("defaultDistance"), ConfigParam("defaultDistance", f = Execution.negate)], {}],
        ["!boxupright ([0-9\.]+)", Execution.box, [ReParam(1), ReParam(1, f = Execution.negate)], {}],
        ["!boxdownleft", Execution.box, [ConfigParam("defaultDistance", f = Execution.negate), ConfigParam("defaultDistance")], {}],
        ["!boxdownleft ([0-9\.]+)", Execution.box, [ReParam(1, f = Execution.negate), ReParam(1)], {}],
        ["!boxdownright", Execution.box, [ConfigParam("defaultDistance"), ConfigParam("defaultDistance")], {}],
        ["!boxdownright ([0-9\.]+)", Execution.box, [ReParam(1), ReParam(1)], {}],
    ]

