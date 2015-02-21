import logging
from os.path import abspath, dirname
from batislib.install import ApplicationInstaller

def main():
    batis_dir = dirname(abspath(__file__))
    logging.basicConfig(level=logging.INFO)
    ai = ApplicationInstaller(batis_dir, 'system')
    ai.install_system_packages(backend=False)
    ai.install_commands()
    ai.install_icons()
    ai.install_mimetypes()
    ai.install_desktop_files()

if __name__ == '__main__':
    main()
