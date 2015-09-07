from PyQt4.QtCore import *
from PyQt4.QtGui import *
#import moviedata
import ui_addpointdlg


class AddPointDlg(QDialog,
        ui_addpointdlg.Ui_AddPointDlg):

    def __init__(self, points, point=None, parent=None):
        super(AddPointDlg, self).__init__(parent)
        self.setupUi(self)

        self.points = points
        self.point = point
        if point is not None:
            self.wavelengthSpinBox.setValue(self.point[0])
            self.amplitudeSpinBox.setValue(self.point[1])
            self.buttonBox.button(QDialogButtonBox.Ok).setText(
                    "&Accept")
            self.setWindowTitle("FCU - Edit Point")
##        else:
##            today = QDate.currentDate()
##            self.acquiredDateEdit.setDateRange(today.addDays(-5),
##                                               today)
##            self.acquiredDateEdit.setDate(today)
        #self.on_titleLineEdit_textEdited(QString())


##    @pyqtSignature("QString")
##    def on_titleLineEdit_textEdited(self, text):
##        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(
##                not self.titleLineEdit.text().isEmpty())


    def accept(self):
        wavelength = self.wavelengthSpinBox.value()
        amplitude = self.amplitudeSpinBox.value()
        if self.point is None:
            self.points.append([wavelength,amplitude])
        else:
            self.points.remove(self.point)
            self.points.append([wavelength,amplitude])
        QDialog.accept(self)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    form = AddPointDlg(0)
    form.show()
    app.exec_()
