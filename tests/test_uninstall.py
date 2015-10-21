import json
import os.path
import testpath
from testpath.tempdir import TemporaryDirectory
from unittest import TestCase

pjoin = os.path.join
dirname = os.path.dirname

from batislib import install, uninstall

batis_root = dirname(dirname(__file__))

class InstallerTests(TestCase):
    def setUp(self):
        sampleapp = pjoin(batis_root, 'sampleapp')
        td = TemporaryDirectory()
        self.addCleanup(td.cleanup)
        self.addCleanup(testpath.make_env_restorer())
        self.td = os.environ['XDG_DATA_HOME'] = td.name

        # Install the application
        scheme = install.get_install_scheme('user')
        scheme['commands'] = pjoin(self.td, 'bin')
        install.ApplicationInstaller(sampleapp, scheme).install()

        self.appdir = pjoin(self.td, 'installed-applications', 'sampleapp')
        self.uninstaller = uninstall.ApplicationUninstaller(self.appdir, scheme)

    def test_remove_files(self):
        files = [
            pjoin(self.td, 'applications', 'fooview.desktop'),
            pjoin(self.td, 'icons', 'hicolor', '48x48', 'apps', 'tango-calculator.png'),
            pjoin(self.td, 'mime', 'packages', 'example-diff.xml'),
        ]
        script = pjoin(self.td, 'bin', 'launch-sampleapp')

        for file in files:
            testpath.assert_isfile(file)
        testpath.assert_islink(script)

        self.uninstaller.remove_files()

        for path in files + [script]:
            testpath.assert_not_path_exists(path)

    def test_remove_file_missing(self):
        with open(pjoin(self.appdir, 'batis_info', 'installed_files.json'), 'w') as f:
            json.dump([{'path': pjoin(self.td, 'bin', 'foo'), 'type': 'link'}], f)

        self.uninstaller.remove_files()

    def test_run_triggers(self):
        self.uninstaller.remove_files()

        with testpath.assert_calls('update-desktop-database'), \
             testpath.assert_calls('update-mime-database'), \
             testpath.assert_calls('xdg-icon-resource'):
            self.uninstaller.run_triggers()

    def test_remove_appdir(self):
        testpath.assert_isdir(self.appdir)
        self.uninstaller.remove_appdir()
        testpath.assert_not_path_exists(self.appdir)
