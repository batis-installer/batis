import argparse
import errno
import glob
import json
import logging
import os
import re
import shutil
from subprocess import call, PIPE, STDOUT

pjoin = os.path.join
basename = os.path.basename

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
        'mimetypes': '/usr/local/share/mime',
    },
    'user': {
        'application': '{XDG_DATA_HOME}/installed-applications',
        'commands': '~/.local/bin',
        'desktop': '{XDG_DATA_HOME}/applications',
        'icons': '{XDG_DATA_HOME}/icons',
        'mimetypes': '{XDG_DATA_HOME}/mime',
    }
}

def ensure_dir_exists(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

def get_install_scheme(name):
    XDG_DATA_HOME = os.environ.get('XDG_DATA_HOME') or "~/.local/share"
    scheme = install_schemes[name]
    return {k: os.path.expanduser(v.format(XDG_DATA_HOME=XDG_DATA_HOME))
            for (k,v) in scheme.items()}

class ApplicationInstaller(object):
    def __init__(self, path, scheme):
        """Class with the main installation logic

        :param path: Application tarball/directory to install
        :param scheme: dictionary of directories to install into
        """
        if os.path.isfile(path):
            self.directory = tarball.unpack_app_tarball(path)
        else:
            self.directory = path
        self.directory = self.directory.rstrip('/')
        self.scheme = scheme
        with open(self._relative('batis_info', 'metadata.json')) as f:
            self.metadata = json.load(f)
        
        self.installed_files = []

    def install_file(self, src, destination):
        ensure_dir_exists(os.path.dirname(destination))
        if os.path.lexists(destination):
            log.warn("Replacing file at %s", destination)
            os.unlink(destination)
        shutil.copy(src, destination)
        self.installed_files.append({'path': destination, 'type': 'file'})
    
    def install_symlink(self, src, destination):
        ensure_dir_exists(os.path.dirname(destination))
        if os.path.lexists(destination):
            log.warn("Replacing file at %s", destination)
            os.unlink(destination)
        os.symlink(src, destination)
        self.installed_files.append({'path': destination, 'type': 'symlink'})

    def _relative(self, *path):
        return os.path.join(self.directory, *path)

    def install_system_packages(self, backend):
        """Install system packages specified in metadata.

        If this fails, returns a short string representing the reason.
        """
        deps_file = self._relative('batis_info', 'dependencies.json')
        if not os.path.isfile(deps_file):
            log.debug("No dependencies.json; skipping installing system packages")

        with open(deps_file) as f:
            deps = json.load(f)

        log.info('Installing system packages')

        spec = distro.select_dependencies_spec(deps['system_packages'])
        if spec is None:
            log.warn(("Couldn't find dependencies for this distro. "
                      "Please ensure these are installed: %s"),
                      deps['description'])
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
                      deps['description'])
            return 'install failed'

    def copy_application(self):
        basename = os.path.basename(os.path.abspath(self.directory))
        destination = os.path.join(self.scheme['application'], basename)
        if os.path.isdir(destination):
            if os.path.isfile(pjoin(destination, 'batis_info',
                                    'installed_files.json')):
                log.info('Removing previously installed application at %s',
                         destination)
                from .uninstall import ApplicationUninstaller
                ApplicationUninstaller(destination, self.scheme).run()
            else:
                log.warn('Removing existing directory %s', destination)
                shutil.rmtree(destination)
        log.info('Copying application directory to %s', destination)
        shutil.copytree(self.directory, destination)

    def install_commands(self):
        log.info("Symlinking commands to %s", self.scheme['commands'])
        for command_info in self.metadata.get('commands', []):
            source = os.path.join(self.scheme['application'],
                                  os.path.basename(self.directory),
                                  command_info['target'])
            link = os.path.join(self.scheme['commands'], command_info['name'])
            self.install_symlink(source, link)

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
                sizedir = pjoin(themedir, sizestr)
                for context in os.listdir(sizedir):
                    contextdir = os.path.join(sizedir, context)
                    for basename in os.listdir(contextdir):
                        src = pjoin(contextdir, basename)
                        dest = pjoin(self.scheme['icons'],
                                     theme, sizestr, context, basename)
                        self.install_file(src, dest)

            call(['xdg-icon-resource', 'forceupdate', '--theme', theme])

    def install_mimetypes(self):
        source_files = glob.glob(self._relative('batis_info', 'mime', '*.xml')) 
        for file in source_files:
            dest = pjoin(self.scheme['mimetypes'], 'packages', basename(file))
            log.info("Installing mimetype package file %s", file)
            self.install_file(file, dest)
        
        if source_files:
            call(['update-mime-database', self.scheme['mimetypes']])

    def install_desktop_files(self):
        install_dir = pjoin(self.scheme['application'],
                            os.path.basename(self.directory))
        files = glob.glob(self._relative('batis_info', 'desktop', '*.desktop'))
        for file in files:
            dest = pjoin(self.scheme['desktop'], basename(file))
            log.info("Installing desktop file: %r", file)
            self.install_file(file, dest)

            # Rewrite any instances of {{INSTALL_DIR}}
            with open(dest) as f:
                contents = f.read()
            with open(dest, 'w') as f:
                f.write(contents.replace('{{INSTALL_DIR}}', install_dir))
        
        if files:
            call(['update-desktop-database', self.scheme['desktop']])
    
    def write_manifest(self):
        with open(pjoin(self.scheme['application'],
                        os.path.basename(self.directory),
                        'batis_info', 'installed_files.json'), 'w') as f:
            json.dump(self.installed_files, f, indent=2)

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
        emit('step: write_manifest')
        self.write_manifest()
        emit('finished')

def main(argv=None):
    ap = argparse.ArgumentParser(prog='batis installtar')
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
    scheme = get_install_scheme('system' if args.system else 'user')
    ai = ApplicationInstaller(args.path, scheme)
    ai.install(args.backend)

if __name__ == '__main__':
    main()
