from PyQt5 import QtCore,  QtWidgets
import sys

from .ui_main import Ui_MainWindow
from .ui_install_prompt import Ui_Form

class Main(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()