from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTimeEdit, QCheckBox, QPushButton)


class AlarmDialog(QDialog):
    def __init__(self, parent=None, time=None, days=None):
        super().__init__(parent)
        self.setWindowTitle('設定鬧鐘')

        self.layout = QVBoxLayout()

        self.timeEdit = QTimeEdit()
        if time:
            self.timeEdit.setTime(time)
        self.timeEdit.setDisplayFormat('HH:mm')
        self.layout.addWidget(self.timeEdit)

        self.checkBoxes = []
        days_of_week = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
        for i, day in enumerate(days_of_week):
            cb = QCheckBox(day)
            if days and days[i]:
                cb.setChecked(True)
            self.layout.addWidget(cb)
            self.checkBoxes.append(cb)

        self.saveButton = QPushButton('儲存')
        self.saveButton.clicked.connect(self.accept)
        self.layout.addWidget(self.saveButton)

        self.setLayout(self.layout)