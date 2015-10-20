import argparse
import json
import logging
import os
import shutil
from subprocess import call

from .install import get_install_scheme

pjoin = os.path.join

scheme_search_order = [
   'user',
   'system',
]

class UnknownApplication(ValueError):
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return 'Application {!r} was not found.'.format(self.name)

class ApplicationUninstaller(object):
    def __init__(self, name):
        self.name = name
        self.desktop_files = False
        self.mime_files = False
        self.icon_themes = set()

        for schemename in scheme_search_order:
            scheme = get_install_scheme(schemename)
            appdir = pjoin(scheme['application'], name)
            if os.path.isdir(appdir):
                self.appdir = appdir
                self.scheme = scheme
                break
        else:
            raise UnknownApplication(name)
    
    def remove_files(self):
        """Remove files copied or linked outside the main application directory"""
        with open(pjoin(self.appdir, 'batis_info', 'installed_files.json')) as f:
            manifest = json.load(f)
        
        for info in manifest:
            # TODO: check that files have not been modified since installation?
            path = info['path']
            os.unlink(info['path'])
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

def main(argv=None):
    ap = argparse.ArgumentParser(prog='batis uninstall')
    ap.add_argument('name', help='The application name to uninstall')
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO)
    ApplicationUninstaller(args.name).run()