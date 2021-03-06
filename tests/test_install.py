import json
import os
from os.path import dirname, join as pjoin
import testpath
from testpath.tempdir import TemporaryDirectory
from unittest import TestCase

try:
    from unittest import mock  # Python 3
except ImportError:
    import mock  # Python 2

from batislib import install

batis_root = dirname(dirname(__file__))

class InstallerTests(TestCase):
    def setUp(self):
        sampleapp = pjoin(batis_root, 'sampleapp')
        td = TemporaryDirectory()
        self.addCleanup(td.cleanup)
        self.addCleanup(testpath.make_env_restorer())
        self.td = os.environ['XDG_DATA_HOME'] = td.name
        self.installer = install.ApplicationInstaller(sampleapp,
                              install.get_install_scheme('user'))

    def test_copy_application(self):
        self.installer.copy_application()
        d = pjoin(self.td, 'installed-applications', 'sampleapp')
        testpath.assert_isdir(d)
        testpath.assert_isfile(pjoin(d, 'run.sh'))

    def test_install_system_packages(self):
        with testpath.assert_calls('sudo', ['apt-get', '--yes', 'install',
                                            'python3', 'python3-pyqt4']):
            self.installer.install_system_packages(backend=False)

    def test_install_commands(self):
        self.installer.copy_application()
        d = pjoin(self.td, 'installed-applications', 'sampleapp')
        self.installer.scheme['commands'] = pjoin(self.td, 'bin')
        self.installer.install_commands()
        testpath.assert_islink(pjoin(self.td, 'bin', 'launch-sampleapp'),
                               pjoin(d, 'run.sh'))

    def test_install_desktop_files(self):
        self.installer.install_desktop_files()
        d = pjoin(self.td, 'applications')
        install_dir = pjoin(self.td, 'installed-applications', 'sampleapp')
        testpath.assert_isfile(pjoin(d, 'fooview.desktop'))
        testpath.assert_isfile(pjoin(d, 'script_in_install_dir.desktop'))

        with open(pjoin(d, 'script_in_install_dir.desktop')) as f:
            checked_lines = 0
            for line in f:
                if line.startswith('Exec='):
                    assert pjoin(install_dir, 'bin', 'fooview') in line
                    checked_lines += 1
                elif line.startswith('Icon='):
                    assert pjoin(install_dir, 'fooview.png') in line
                    checked_lines += 1

        assert checked_lines == 2

    def test_uninstall_previous(self):
        d = pjoin(self.td, 'installed-applications', 'sampleapp')
        foobar_script = pjoin(self.td, 'bin', 'foobar')
        
        # Mock up an existing application installed in the destination
        os.makedirs(pjoin(d, 'batis_info'))
        os.makedirs(pjoin(self.td, 'bin'))
        with open(foobar_script, 'w'):
            pass  # Just opening to create it
        with open(pjoin(d, 'batis_info', 'installed_files.json'), 'w') as f:
            json.dump([{'path': foobar_script, 'type': 'file'}], f)
        
        testpath.assert_path_exists(foobar_script)
        self.installer.copy_application()
        testpath.assert_not_path_exists(foobar_script)

    def test_ensure_path_env(self):
        def mock_expanduser(p):
            return p.replace('~', self.td)

        with mock.patch('os.path.expanduser', mock_expanduser), \
             testpath.modified_env({'PATH': '/bin'}):

            self.installer.ensure_path_env()

        profile_file = pjoin(self.td, '.profile')
        testpath.assert_isfile(profile_file)

        with open(profile_file, 'r') as f:
            contents = f.read()
        assert self.installer.scheme['commands']+':$PATH' in contents
