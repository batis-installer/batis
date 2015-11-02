import pytest
pytestmark = pytest.mark.selfinstall

from testpath import MockCommand, assert_calls
from batislib import distro

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

def test_find_distro_name():
    # Smoketest
    distro.find_distro_name()

def test_find_package_manager_command():
    with MockCommand('apt-get'):
        assert distro.find_package_manager_command() == 'apt-get'

def test_install_packages():
    expected_args = ['--yes', 'install', 'pkg1', 'pkg2']
    with assert_calls('apt-get', expected_args), patch('os.getuid', return_value=0):
        distro.install_packages(['pkg1', 'pkg2'])
