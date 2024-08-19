from datetime import datetime
import os
import shutil
import sys

import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui

from KKT_Module.ksoc_global import kgl
from KKT_Module.Configs import SettingConfigs
from KKT_Module.SettingProcess.SettingProccess import SettingProc, ConnectDevice, ResetDevice
from KKT_Module.DataReceive.DataReciever import FeatureMapReceiver
from UI.mainFunc import AlarmApp
import time


class AlarmClock(AlarmApp):
    def startDetection(self):
        self.running = True
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.statusButton.setText('Detecting...')
        self.statusButton.setStyleSheet('background-color: yellow')

        self.thread = DetectionThread()
        self.thread.data_signal.connect(self.updateStatus)
        self.thread.start()

    def stopDetection(self):
        self.running = False
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.thread.stop()
        self.statusButton.setText('Status: Not detecting')
        self.statusButton.setStyleSheet('background-color: red')

    def updateStatus(self, total_energy):
        if total_energy > 40000:
            self.statusButton.setStyleSheet('background-color: yellow')
            self.statusButton.setText('Status: Object Detected')
            self.handleAlarmBox(1)
        else:
            self.statusButton.setStyleSheet('background-color: red')
            self.statusButton.setText('Status: No Object')
            self.handleAlarmBox(0)

    def handleAlarmBox(self, detected):
        if detected and self.alarmBox:
            self.alarmBox.close()

    def __init__(self):
        super().__init__()
        self.running = False
        self.startButton.clicked.connect(self.startDetection)
        self.stopButton.clicked.connect(self.stopDetection)
        self.stopButton.setEnabled(False)


class DetectionThread(QtCore.QThread):
    data_signal = QtCore.pyqtSignal(int)

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

            self.data_signal.emit(total_energy)


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
