import argparse
import glob
import json
import logging
import os
import re
import shutil
from subprocess import check_call, PIPE, STDOUT
import errno

from . import distro, tarball

log = logging.getLogger(__name__)

# These locations are not all used by the code below; it shells out to XDG
# commands like xdg-mime and xdg-icon-resource. They should install
# to these locations, however.
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
    def __init__(self, path, scheme):
        """Class with the main installation logic

        :param path: Application tarball/directory to install
        :param scheme: 'user' or 'system'
        """
        if os.path.isfile(path):
            self.directory = tarball.unpack_app_tarball(path)
        else:
            self.directory = path
        self.directory = self.directory.rstrip('/')
        self.scheme = install_schemes[scheme]
        with open(self._relative('batis_info', 'metadata.json')) as f:
            self.metadata = json.load(f)

    def _relative(self, *path):
        return os.path.join(self.directory, *path)

    def destination(self, component):
        XDG_DATA_HOME = os.environ.get('XDG_DATA_HOME') or "~/.local/share"
        path = os.path.expanduser(self.scheme[component].format(XDG_DATA_HOME=XDG_DATA_HOME))
        try:
            os.makedirs(path, mode=0o755)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        return path

    def install_system_packages(self, backend):
        """Install system packages specified in metadata.

        If this fails, returns a short string representing the reason.
        """
        if self.metadata['system_packages'] is None:
            return

        log.info('Installing system packages')

        spec = distro.select_dependencies_spec(self.metadata['system_packages'])
        if spec is None:
            log.warn(("Couldn't find dependencies for this distro. "
                      "Please ensure these are installed: %s"),
                      self.metadata['dependencies_description'])
            return 'no distro match'

        log.info('Packages to install: %r', spec['packages'])

        kwargs = {}
        if backend:
            kwargs['sudo_cmd'] = 'pkexec'
            kwargs['stdout'] = PIPE
            kwargs['stderr'] = STDOUT
        stdout, stderr, returncode = distro.install_packages(spec['packages'],
                                     sudo_cmd=('pkexec' if backend else 'sudo'))
        if returncode != 0:
            log.warn(("Installing dependencies failed. "
                      "Please ensure these are installed: %s"),
                      self.metadata['dependencies_description'])
            return 'install failed'

    def copy_application(self):
        basename = os.path.basename(self.directory)
        destination = os.path.join(self.destination('application'), basename)
        log.info('Copying application directory to %s', destination)
        if os.path.isdir(destination):
            shutil.rmtree(destination)
        shutil.copytree(self.directory, destination)

    def install_commands(self):
        log.info("Symlinking commands to %s", self.destination('commands'))
        for command_info in self.metadata.get('commands', []):
            source = os.path.join(self.destination('application'),
                                  os.path.basename(self.directory),
                                  command_info['target'])
            link = os.path.join(self.destination('commands'), command_info['name'])
            if os.path.lexists(link):
                log.warn("Replacing file at %s", link)
                os.unlink(link)
            os.symlink(source, link)

    def install_icons(self):
        icon_dir = self._relative('batis_info', 'icons')
        if not os.path.isdir(icon_dir):
            log.info("No icons to install")
            return

        log.info("Installing icons")
        for theme in os.listdir(icon_dir):
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
                              '--novendor', '--theme', theme, '--size', size,
                              '--context', context, file])

            check_call(['xdg-icon-resource', 'forceupdate', '--theme', theme])

    def install_mimetypes(self):
        for file in glob.glob(self._relative('batis_info', 'mime', '*.xml')):
            log.info("Installing mimetype package file %s", file)
            check_call(['xdg-mime', 'install', file])

    def install_desktop_files(self):
        files = glob.glob(self._relative('batis_info', 'desktop', '*.desktop'))
        log.info("Installing desktop files: %r", files)
        if files:
            check_call(['desktop-file-install', '--rebuild-mime-info-cache',
                        '--dir', self.destination('desktop')] + files)

    def install(self, backend=False):
        def emit(msg):
            if backend:
                print(msg)

        emit('step: system_packages')
        failure = self.install_system_packages(backend)
        if failure:
            emit('problem: system_packages: ' + failure)
        emit('step: copy_dir')
        self.copy_application()
        emit('step: install_commands')
        self.install_commands()
        emit('step: install_icons')
        self.install_icons()
        emit('step: install_mimetypes')
        self.install_mimetypes()
        emit('step: install_desktop')
        self.install_desktop_files()
        emit('finished')

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--system', action='store_true',
            help='Install systemwide, instead of for the user')
    ap.add_argument('--backend', action='store_true',
            help='Print steps to stdout to update the GUI installer')
    ap.add_argument('path', help='The application tarball or directory to install')
    args = ap.parse_args(argv)
    if args.backend:
        log.addHandler(logging.NullHandler())
    else:
        logging.basicConfig(level=logging.INFO)
    ai = ApplicationInstaller(args.path, 'system' if args.system else 'user')
    ai.install(args.backend)

if __name__ == '__main__':
    main()
