import argparse
import glob
import json
import os
import re
import shutil
from subprocess import check_call

install_schemes = {
    'system': {
        'application': '/opt',
        'commands': '/usr/local/bin',
        'desktop': '/usr/local/share/applications',
        'icons': '/usr/local/share/icons',
        'mimetypes': '/usr/local/share/mime/packages',
    },
    'user': {
        'application': '{XDG_DATA_HOME}/installed-applications',
        'commands': '~/.local/bin',
        'desktop': '{XDG_DATA_HOME}/applications',
        'icons': '{XDG_DATA_HOME}/icons',
        'mimetypes': '{XDG_DATA_HOME}/mime/packages',
    }
}


class ApplicationInstaller(object):
    def __init__(self, directory, scheme):
        self.directory = directory
        self.scheme = install_schemes[scheme]
        with open(self._relative('batis_info', 'metadata.json')) as f:
            self.metadata = json.load(f)

    def _relative(self, *path):
        return os.path.join(self.directory, *path)

    def destination(self, component):
        XDG_DATA_HOME = os.environ.get('XDG_DATA_HOME') or "~/.local/share"
        path = os.path.expanduser(self.scheme[component].format(XDG_DATA_HOME=XDG_DATA_HOME))
        os.makedirs(path, mode=0o755)
        return path

    def copy_application(self):
        shutil.copytree(self.directory, os.path.join(self.destination('application'),
                                                     os.name))

    def install_commands(self):
        for command_info in self.metadata.get('commands', []):
            source = os.path.join(self.destination('application'), command_info['target'])
            link = os.path.join(self.destination('commands'), command_info['name'])
            os.symlink(source, link)

    def install_icons(self):
        for theme in os.listdir(self._relative('batis_info', 'icons')):
            themedir = self._relative('batis_info', 'icons', theme)
            for sizestr in os.listdir(themedir):
                m = re.match(r'(\d+)x\1', sizestr)
                if not m:
                    continue
                size = m.group(1)
                sizedir = os.path.join(themedir, sizestr)
                for context in os.listdir(sizedir):
                    contextdir = os.path.join(sizedir, context)
                    for basename in os.listdir(contextdir):
                        file = os.path.join(contextdir, basename)
                        check_call(['xdg-icon-resource', 'install', '--noupdate',
                              '--theme', theme, '--size', size,
                              '--context', context, file])

            check_call(['xdg-icon-resource', 'forceupdate', '--theme', theme])

    def install_mimetypes(self):
        for file in glob.glob(self._relative('batis_info', 'mime', '*.xml')):
            check_call(['xdg-mime', 'install', file])

    def install_desktop_files(self):
        files = glob.glob(self._relative('batis_info', 'desktop', '*.desktop'))
        check_call(['desktop-file-install', '--rebuild-mime-info-cache'] + files)

    def install(self):
        self.copy_application()
        self.install_commands()
        self.install_icons()
        self.install_mimetypes()
        self.install_desktop_files()

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--system', action='store_true',
            help='Install systemwide, instead of for the user')
    ap.add_argument('directory', help='The unpacked application tarball')
    args = ap.parse_args(argv)
    ai = ApplicationInstaller(args.directory, 'system' if args.system else 'user')
    ai.install()

if __name__ == '__main__':
    main()
