from os.path import dirname, join as pjoin
import testpath
from testpath.tempdir import TemporaryDirectory
from unittest import TestCase

from batislib import install

batis_root = dirname(dirname(__file__))

class InstallerTests(TestCase):
    def setUp(self):
        sampleapp = pjoin(batis_root, 'sampleapp')
        self.installer = install.ApplicationInstaller(sampleapp, 'user')

    def test_copy_application(self):
        with TemporaryDirectory() as td:
            with testpath.modified_env({'XDG_DATA_HOME': td}):
                self.installer.copy_application()
                d = pjoin(td, 'installed-applications', 'sampleapp')
                testpath.assert_isdir(d)
                testpath.assert_isfile(pjoin(d, 'run.sh'))

    def test_install_commands(self):
        with TemporaryDirectory() as td:
            with testpath.modified_env({'XDG_DATA_HOME': td}):
                self.installer.copy_application()
                d = pjoin(td, 'installed-applications', 'sampleapp')
                _saved_cmd_target = install.install_schemes['user']['commands']
                install.install_schemes['user']['commands'] = pjoin(td, 'bin')
                try:
                    self.installer.install_commands()
                    testpath.assert_islink(pjoin(td, 'bin', 'launch-sampleapp'),
                                           pjoin(d, 'run.sh'))
                finally:
                    install.install_schemes['user']['commands'] = _saved_cmd_target
