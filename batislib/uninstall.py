import argparse
import errno
import json
import logging
import os
import shutil
from subprocess import call

from .install import get_install_scheme
from .log import enable_colourful_output
from .util import compress_user

pjoin = os.path.join

log = logging.getLogger(__name__)

class UnknownApplication(ValueError):
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return 'Application {!r} was not found.'.format(self.name)

def find_installed_application(name, scheme_search_order=('user', 'system')):
    for schemename in scheme_search_order:
        scheme = get_install_scheme(schemename)
        appdir = pjoin(scheme['application'], name)
        if os.path.isdir(appdir):
            return appdir, scheme

    raise UnknownApplication(name)

class ApplicationUninstaller(object):
    def __init__(self, appdir, scheme):
        self.appdir = appdir
        self.scheme = scheme
        self.desktop_files = False
        self.mime_files = False
        self.icon_themes = set()
    
    def remove_files(self):
        """Remove files copied or linked outside the main application directory"""
        with open(pjoin(self.appdir, 'batis_info', 'installed_files.json')) as f:
            manifest = json.load(f)
        
        for info in manifest:
            # TODO: check that files have not been modified since installation?
            path = info['path']
            try:
                os.unlink(path)
            except OSError as e:
                if e.errno == errno.ENOENT:
                    continue
                else:
                    raise

            if path.startswith(self.scheme['desktop']):
                self.desktop_files = True
            elif path.startswith(self.scheme['mimetypes']):
                self.mime_files = True
            elif path.startswith(self.scheme['icons']):
                theme = path[len(self.scheme['icons']):].lstrip('/').split('/')[0]
                self.icon_themes.add(theme)
        
    def run_triggers(self):
        """Run external commands to rebuild caches affected by files we remove"""
        if self.desktop_files:
            call(['update-desktop-database', self.scheme['desktop']])
        if self.mime_files:
            call(['update-mime-database', self.scheme['mimetypes']])
        for theme in self.icon_themes:
            call(['xdg-icon-resource', 'forceupdate', '--theme', theme])
    
    def remove_appdir(self):
        """Remove the main application directory"""
        shutil.rmtree(self.appdir)
    
    def run(self):
        self.remove_files()
        self.run_triggers()
        self.remove_appdir()
        log.info('Uninstalled %s', compress_user(self.appdir))

def main(argv=None):
    ap = argparse.ArgumentParser(prog='batis uninstall')
    ap.add_argument('name', help='The application name to uninstall')
    args = ap.parse_args(argv)
    enable_colourful_output(level=logging.INFO)
    appdir, scheme = find_installed_application(args.name)
    ApplicationUninstaller(appdir, scheme).run()
