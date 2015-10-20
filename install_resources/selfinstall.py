"""Called by install.sh in the application root directory.

Expects the application directory to install as the first argument.
"""
import logging
import sys
from batislib.install import ApplicationInstaller, get_install_scheme

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    scheme = get_install_scheme('user')
    ApplicationInstaller(sys.argv[1], scheme).install()
