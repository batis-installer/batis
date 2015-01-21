from PyQt5 import QtCore, QtGui, QtWidgets
import ast
import json
import os
import shutil
import sys

from .ui_main import Ui_MainWindow
from .ui_install_prompt import Ui_Form
from .ui_install_progress import Ui_ProgressWidget

class Main(QtWidgets.QMainWindow):
    tmpdir = None

    def __init__(self, app):
        QtWidgets.QMainWindow.__init__(self)
        self.app = app
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    def start(self, argv):
        self.unpack(argv[1])

    def unpack(self, tarball_path):
        self.subp = QtCore.QProcess(self)
        self.subp.finished.connect(self.unpack_finished)
        self.subp.start(sys.executable, ['-m', 'batis', 'unpack', tarball_path])

    def unpack_finished(self, exitcode, exitstatus):
        if exitcode == 0:
            output = bytes(self.subp.readAllStandardOutput()).decode('utf-8')
            assert output.startswith('dir: ')
            tmpdir = ast.literal_eval(output[5:].rstrip())
            print(tmpdir)
            self.install_prompt(tmpdir)

    def install_prompt(self, tmpdir):
        self.tmpdir = tmpdir
        self.app.lastWindowClosed.connect(self.cleanup_tmpdir)
        with open(os.path.join(self.tmpdir, 'batis_info', 'metadata.json')) as f:
            self.metadata = json.load(f)
        newwidget = QtWidgets.QWidget(self)
        self.form = Ui_Form()
        self.form.setupUi(newwidget)
        self.form.app_name.setText(self.metadata['name'])
        self.form.app_byline.setText(self.metadata['byline'])
        if 'icon' in self.metadata:
            iconpath = os.path.join(self.tmpdir, self.metadata['icon'])
            self.form.app_icon.setPixmap(QtGui.QPixmap(iconpath))

        self.form.user_install_button.clicked.connect(self.show_install_progress)
        self.form.cancel_button.clicked.connect(self.close)

        self.setCentralWidget(newwidget)

    def cleanup_tmpdir(self):
        if self.tmpdir:
            shutil.rmtree(self.tmpdir)

    def show_install_progress(self):
        newwidget = QtWidgets.QWidget()
        self.progress = Ui_ProgressWidget()
        self.progress.setupUi(newwidget)
        self.progress.installing_app.setText("Installing {}...".format(self.metadata['name']))

        self.setCentralWidget(newwidget)
        self.adjustSize()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = Main(app)
    window.show()
    window.start(sys.argv)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()