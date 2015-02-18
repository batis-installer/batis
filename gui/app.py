from PyQt5 import QtCore, QtGui, QtWidgets
import ast
import json
import os
import shutil
import sys

from .ui_main import Ui_MainWindow
from .ui_install_prompt import Ui_Form
from .ui_install_progress import Ui_ProgressWidget

batis_dir = os.path.dirname(os.path.dirname(__file__))

class Main(QtWidgets.QMainWindow):
    tmpdir = None

    def __init__(self, app):
        QtWidgets.QMainWindow.__init__(self)
        self.app = app
        self.metadata = {}
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    @property
    def app_name(self):
        return self.metadata.get('name', 'application')

    def start(self, argv):
        self.unpack(argv[0])

    def unpack(self, tarball_path):
        self.subp = QtCore.QProcess(self)
        self.subp.finished.connect(self.unpack_finished)
        self.subp.start(os.path.join(batis_dir, 'batis'),['unpack', tarball_path])

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
        self.form.app_name.setText(self.app_name)
        self.form.app_byline.setText(self.metadata['byline'])
        if 'icon' in self.metadata:
            iconpath = os.path.join(self.tmpdir, self.metadata['icon'])
            self.form.app_icon.setPixmap(QtGui.QPixmap(iconpath))

        self.form.user_install_button.clicked.connect(self.user_install)
        self.form.system_install_button.clicked.connect(self.system_install)
        self.form.cancel_button.clicked.connect(self.close)

        self.setCentralWidget(newwidget)

    def cleanup_tmpdir(self):
        if self.tmpdir:
            shutil.rmtree(self.tmpdir)

    def launch_and_hide(self):
        self.hide()
        self.app_process = QtCore.QProcess(self)
        def app_finished(exitcode, exitstatus):
            self.close()
        self.app_process.finished.connect(app_finished)
        argv = self.metadata['launch']
        self.app_process.start(argv[0], argv[1:])

    def do_install(self, argv):
        self.show_install_progress()
        self.subp = QtCore.QProcess(self)

        step_descriptions = {'copy_dir': 'Copying files',
                             'install_commands': 'Installing commands',
                             'install_icons': 'Installing icons',
                             'install_mimetypes': 'Installing MIME types',
                             'install_desktop': 'Installing shortcuts'}

        def process_output_line(line):
            if line == 'finished':
                self.progress.progressBar.hide()
                self.progress.status.hide()
                self.progress.installing_app.setText('Installed {}'.format(self.app_name))
                if 'launch' in self.metadata:
                    launchButton = QtWidgets.QPushButton('Launch')
                    launchButton.clicked.connect(self.launch_and_hide)
                    self.progress.buttonBox.addButton(launchButton, QtWidgets.QDialogButtonBox.ActionRole)
                closeButton = QtWidgets.QPushButton('Close')
                closeButton.clicked.connect(self.close)
                self.progress.buttonBox.addButton(closeButton, QtWidgets.QDialogButtonBox.ActionRole)
                self.progress.buttonBox.show()
                self.adjustSize()
            if line.startswith('step: '):
                text = step_descriptions.get(line[6:], '')
                self.progress.status.setText(text)

        self.output_buffer = b''
        def read_stdout():
            new = bytes(self.subp.readAllStandardOutput())
            self.output_buffer += new
            if b'\n' in self.output_buffer:
                lines = self.output_buffer.splitlines()
                if self.output_buffer.endswith(b'\n'):
                    self.output_buffer = b''
                else:
                    self.output_buffer = lines[-1]
                    lines = lines[:-1]
                for line in lines:
                    process_output_line(line.decode('utf-8'))

        def read_stderr():
            print('E->', repr(bytes(self.subp.readAllStandardError())))

        self.subp.readyReadStandardOutput.connect(read_stdout)
        self.subp.readyReadStandardError.connect(read_stderr)
        self.subp.start(argv[0], argv[1:])

    def user_install(self):
        self.do_install([os.path.join(batis_dir, 'batis'), 'backend-install',
                                         '--backend', self.tmpdir])

    def system_install(self):
        _root_install = os.path.join(batis_dir, '_root_install.py')
        argv = ['pkexec', sys.executable, _root_install,
                '--backend', '--system', self.tmpdir]
        self.do_install(argv,)

    def show_install_progress(self):
        newwidget = QtWidgets.QWidget()
        self.progress = Ui_ProgressWidget()
        self.progress.setupUi(newwidget)
        self.progress.installing_app.setText("Installing {}...".format(self.app_name))

        self.progress.buttonBox.hide()
        self.progress.problem.hide()

        self.setCentralWidget(newwidget)
        self.adjustSize()


def main(argv):
    app = QtWidgets.QApplication(['batis-gui'] + argv)
    window = Main(app)
    window.show()
    window.start(argv)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main(sys.argv[1:])
