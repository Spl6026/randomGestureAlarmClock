from datetime import datetime
import os
import shutil
import sys

import numpy as np
from PyQt5 import QtWidgets, QtCore

from KKT_Module.ksoc_global import kgl
from KKT_Module.Configs import SettingConfigs
from KKT_Module.SettingProcess.SettingProccess import SettingProc, ConnectDevice, ResetDevice
from KKT_Module.DataReceive.DataReciever import FeatureMapReceiver
from UI.mainFunc import AlarmApp
import time


class AlarmClock(AlarmApp):
    def startDetection(self):
        self.running = True
        self.status.setStyleSheet('background-color: yellow')  # detecting
        self.thread = DetectionThread()
        self.thread.dataSignal.connect(self.updateStatus)
        self.thread.start()

    def stopDetection(self):
        self.running = False
        self.thread.stop()
        self.status.setStyleSheet('background-color: red')  # Not detecting

    def updateStatus(self, total_energy):
        if total_energy > 40000:
            self.status.setStyleSheet('background-color: yellow')  # object detected
            self.handleAlarmBox(1)
        else:
            self.status.setStyleSheet('background-color: green')  # no object
            self.handleAlarmBox(0)

    def handleAlarmBox(self, detected):
        if detected and self.alarmBox:
            self.alarmBox.close()

    def __init__(self):
        super().__init__()
        self.running = False
        self.startDetection()


class DetectionThread(QtCore.QThread):
    dataSignal = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        connect()
        startSetting()
        self.startLoop()

    def stop(self):
        self.running = False

    def startLoop(self):
        R = FeatureMapReceiver(chirps=32)  # Receiver for getting RDI PHD map
        R.trigger(chirps=32)  # Trigger receiver before getting the data
        time.sleep(0.5)

        while self.running:  # 無限循環以獲取數據
            res = R.getResults()  # 獲取接收器數據

            if res is None:
                continue

            power = np.abs(res[0])
            total_energy = np.sum(power)  # 計算總能量

            self.dataSignal.emit(total_energy)


def connect():
    connect = ConnectDevice()
    connect.startUp()  # Connect to the device
    reset = ResetDevice()
    reset.startUp()  # Reset hardware register


def startSetting():
    SettingConfigs.setScriptDir("K60168-Test-00256-008-v0.0.8-20230717_120cm")  # Set the setting folder name
    ksp = SettingProc()  # Object for setting process to setup the Hardware AI and RF before receive data
    ksp.startUp(SettingConfigs)  # Start the setting process


def main():
    kgl.setLib()
    kgl.ksoclib.switchLogMode(False)

    app = QtWidgets.QApplication(sys.argv)
    ex = AlarmClock()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
