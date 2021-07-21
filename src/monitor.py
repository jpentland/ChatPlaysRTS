import screeninfo
import pyautogui as pg

class Monitor():
    def __init__(self, config, log):
        self.config = config
        self.log = log
        self.refresh()

    # Refresh monitors
    def refresh(self):
        self.monitors = screeninfo.get_monitors()
        for monitor in self.monitors:
            monitor.full_name = "%s (%dx%d)" % (monitor.name, monitor.width, monitor.height)
        self.full_width, self.full_height = pg.size()

        self.index = 0
        self.updateMonitorList()
        self.setMonitorFromConfig()

    # Set monitor from config
    def setMonitorFromConfig(self):
        configMonitor = self.config["monitor"]["monitor"]
        if configMonitor == "ALL":
            self.selectMonitor(0)
            return

        for i, monitor in zip(range(len(self.monitors)), self.monitors):
            if monitor.name == configMonitor:
                self.selectMonitor(i + 1)
                return

        self.selectMonitor(0)
        self.log.log("Monitor %s not found, selecting all moniotors" % configMonitor)

    # Set monitor in config
    def setMonitorInConfig(self):
        if self.index == 0:
            self.config["monitor"]["monitor"] = "ALL"
        else:
            self.config["monitor"]["monitor"] = self.monitors[self.index - 1].name
        self.config.write()

    # Update list of monitor names
    def updateMonitorList(self):
        self.monitorList = []
        self.monitorList.append("All Monitors")
        for monitor in self.monitors:
            self.monitorList.append(monitor.full_name)

    # Get list of monitor names
    def listMonitors(self):
        return self.monitorList

    # Set selected monitor by index (0 = all monitors)
    def selectMonitor(self, index):
        self.log.log("Selecting monitor: %s" % self.monitorList[index])
        self.index = index
        self.setMonitorInConfig()

    # Get currently selected monitor
    def getSelectedMonitor(self):
        return self.index

    # Get screen size
    def getScreenSize(self):
        if self.index == 0:
            return self.full_width, self.full_height
        else:
            monitor = self.monitors[self.index - 1]
            return monitor.width, monitor.height

    # Get screen offset
    def getScreenOffset(self):
        if self.index == 0:
            return 0, 0
        else:
            monitor = self.monitors[self.index - 1]
            return monitor.x, monitor.y
