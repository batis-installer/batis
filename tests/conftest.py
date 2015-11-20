import os, sys

# Tests for the code involved in self installation (./install.sh). These
# need to be run under Python 2.
self_install_tests = {'test_install.py', 'test_distro.py'}

if sys.version_info[0] < 3:
    collect_ignore = [f for f in os.listdir(os.path.dirname(__file__))
                    if f.startswith('test_') and (f not in self_install_tests)]

del self_install_tests
