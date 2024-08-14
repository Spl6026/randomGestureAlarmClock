from PyQt5.QtWidgets import QDialog
from editUI import Ui_Edit


class AlarmDialog(QDialog, Ui_Edit):
    def __init__(self, parent=None, time=None, days=None):
        super().__init__(parent)
        self.setupUi(self)

        self.checkBoxes = [
            self.mon, self.tue, self.wed, self.thu, self.fri, self.sat, self.sun
        ]

        if time:
            self.timeEdit.setTime(time)

        if days:
            for i in range(7):
                self.checkBoxes[i].setChecked(days[i])

        self.saveButton.clicked.connect(self.accept)
