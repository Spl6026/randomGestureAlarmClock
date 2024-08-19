import sys
from PyQt5.QtMultimedia import QMediaPlaylist, QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QListWidgetItem
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, QTime, QDate, QUrl
from UI.mainUI import Ui_Main
from UI.editFunc import AlarmDialog


class Alarm:
    def __init__(self, time, days):
        self.time = time
        self.days = days


class AlarmApp(QWidget, Ui_Main):
    def addAlarm(self):
        dialog = AlarmDialog(self)
        if dialog.exec_():
            time = dialog.timeEdit.time()
            days = [dialog.checkBoxes[i].isChecked() for i in range(7)]
            alarm = Alarm(time, days)
            alarm.ring = False
            self.alarms.append(alarm)
            self.updateAlarmList()

    def editAlarm(self, item: QListWidgetItem):
        index = self.alarmList.row(item)
        alarm = self.alarms[index]
        dialog = AlarmDialog(self, alarm.time, alarm.days)
        if dialog.exec_():
            alarm.time = dialog.timeEdit.time()
            alarm.days = [dialog.checkBoxes[i].isChecked() for i in range(7)]
            self.updateAlarmList()
        else:
            reply = QMessageBox.question(self, '刪除鬧鐘', '確定要刪除這個鬧鐘嗎？', QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.alarms.pop(index)
                self.updateAlarmList()

    def updateAlarmList(self):
        self.alarmList.clear()
        for alarm in self.alarms:
            days_str = ''.join(['一二三四五六日'[i] if alarm.days[i] else '' for i in range(7)])
            self.alarmList.addItem(f'{alarm.time.toString("HH:mm")} - {days_str}')

    def checkAlarms(self):
        update = (QDate.currentDate().dayOfWeek() - 1) % 7  # mon = 1, sun = 7 -> day - 1
        uptime = QTime.currentTime()
        for alarm in self.alarms:
            alarmtime = alarm.time
            if alarm.ring and (
                    uptime.minute() > alarmtime.minute() or (uptime.minute() == 0 and alarmtime.minute() == 59)):
                alarm.ring = False

            if (uptime.hour(), uptime.minute()) == (alarmtime.hour(), alarmtime.minute()) and alarm.days[
                update] and not alarm.ring:
                self.ringAlarm(alarm)

    def ringAlarm(self, alarm):
        alarm.ring = True
        alarmBox = QMessageBox(self)
        player = QMediaPlayer()
        playlist = QMediaPlaylist(player)
        playlist.addMedia(QMediaContent(QUrl.fromLocalFile("./Sound/siri_end.mp3")))
        playlist.setPlaybackMode(QMediaPlaylist.Loop)
        player.setPlaylist(playlist)
        player.setVolume(100)  # 設定音量
        player.play()  # 播放音檔

        alarmBox.setWindowTitle('鬧鐘響鈴中')
        alarmBox.setText('時間到了！')
        alarmBox.setStandardButtons(QMessageBox.Ok)
        alarmBox.exec_()
        player.stop()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.alarms = []

        # 設定按鈕和清單的事件處理
        self.addButton.clicked.connect(self.addAlarm)
        self.alarmList.itemDoubleClicked.connect(self.editAlarm)

        # 設定定時器來檢查鬧鐘
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.checkAlarms)
        self.timer.start(1000)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AlarmApp()
    ex.show()
    sys.exit(app.exec_())
