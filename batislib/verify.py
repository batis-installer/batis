import argparse
import json
import os
import re
import tarfile
from xml.etree import ElementTree
import sys
from .tarball import unpack_app_tarball

from xdg.DesktopEntry import DesktopEntry
from xdg import IniFile

pjoin = os.path.join

class UnpackedDirVerifier(object):
    def __init__(self, directory):
        self.directory = directory

    def _relative(self, *path):
        return os.path.join(self.directory, *path)

    def verify_batis_info_subdir(self, problems):
        if not os.path.isdir(self._relative('batis_info')):
            problems.append('No batis_info subdirectory')

    def verify_metadata(self, problems):
        pa = problems.append

        metadata_file = self._relative('batis_info', 'metadata.json')
        if not os.path.isfile(metadata_file):
            problems.append('No file batis_info/metadata.json')
            return

        with open(metadata_file, 'r') as f:
            try:
                metadata = json.load(f)
            except ValueError as e:
                pa('batis_info/metadata.json is not valid JSON: %s' % e)
                return

        if 'name' in metadata:
            if not isinstance(metadata['name'], str):
                pa('name field in metadata is not a string: %r' % metadata['name'])
        else:
            pa('Missing name field in metadata')

        if 'byline' in metadata:
            if not isinstance(metadata['byline'], str):
                pa('byline field in metadata is not a string: %r' % metadata['byline'])
        else:
            pa('Missing byline field in metadata')

        if 'icon' in metadata:
            if isinstance(metadata['icon'], str):
                if not os.path.isfile(self._relative(metadata['icon'])):
                    pa('Icon file specified in metadata does not exist: %s' % metadata['icon'])
            else:
                pa('icon field in metadata is not a string: %r' % metadata['icon'])
        else:
            pa('Missing icon field in metadata')

        if 'index_url' in metadata:
            if isinstance(metadata['index_url'], str):
                if not metadata['index_url'].startswith('https://'):
                    pa('Index url in metadata is not https: %s' % metadata['index_url'])
            else:
                pa('index_url field in metadata is not a string: %r' % metadata['index_url'])
        else:
            pa('Missing index_url field in metadata (optional but recommended)')

        for cmd_info in metadata.get('commands', []):
            if not isinstance(cmd_info, dict):
                pa('Non-dictionary in commands list: %r' % cmd_info)
                continue

            if 'target' not in cmd_info:
                pa('No target field in command info: %r' % cmd_info)

            if 'name' not in cmd_info:
                pa('No name field in command info: %r' % cmd_info)

            if not os.path.isfile(self._relative(cmd_info['target'])):
                pa('Command target does not exist in package: %r' % cmd_info['target'])


    def verify_dependencies(self, problems):
        pa = problems.append
        
        deps_file = self._relative('batis_info', 'dependencies.json')
        if not os.path.isfile(deps_file):
            # This is optional
            return
        
        with open(deps_file, 'r') as f:
            try:
                d = deps = json.load(f)
            except ValueError as e:
                problems.append('batis_info/dependencies.json is not valid JSON: %s' % e)
                return
        
        if 'system_packages' not in d:
            pa('No system_packages field in dependencies.json. '
               'If the package really has no requirements, delete that file.')
        elif isinstance(d['system_packages'], list):
            system_packages = d['system_packages']
            if len(system_packages) == 0:
                pa("system_packages should not be an empty list. "
                   'If the package really has no requirements, delete dependencies.json')

            for spec in system_packages:
                if not isinstance(spec, dict):
                    pa("Package spec is not a dictionary: %r" % spec)

                if ('package_manager' not in spec) and ('distro_name' not in spec):
                    pa("Package spec needs at least one of package_manager, distro_name: %r"
                        % spec)

                if 'packages' not in spec:
                    pa("Package spec needs packages field: %r" % spec)

                elif not isinstance(spec['packages'], list):
                    pa("Package spec packages field is not a list: %r" % spec['packages'])

        else:
            pa('system_packages is not a list: %r' % deps['system_packages'])

        if 'description' not in d:
            pa('description field missing from dependencies.json')
        elif not isinstance(d['description'], str):
            pa('dependencies.json description is not a string: %r' %
                d['description'])

    def verify_desktop_files(self, problems):
        desktop_dir = self._relative('batis_info', 'desktop')
        if not os.path.exists(desktop_dir):
            # This is fine, it's optional
            return

        if not os.path.isdir(desktop_dir):
            problems.append('batis_info/desktop should be a directory')
            return

        for name in os.listdir(desktop_dir):
            if os.path.splitext(name)[1] != '.desktop':
                problems.append('Non .desktop file in batis_info/desktop: %r' % name)
            else:
                path = os.path.join(desktop_dir, name)
                try:
                    de = DesktopEntry(path)
                    de.validate()
                except (IniFile.ParsingError, IniFile.ValidationError) as e:
                    problems.append('Invalid desktop entry file (%s):\n%s'
                                        % (path, e))

    def verify_mimetypes(self, problems):
        mime_dir = self._relative('batis_info', 'mime')
        if not os.path.exists(mime_dir):
            # This is fine, it's optional
            return

        if not os.path.isdir(mime_dir):
            problems.append('batis_info/mime should be a directory')
            return

        for name in os.listdir(mime_dir):
            if os.path.splitext(name)[1] != '.xml':
                problems.append('Non .xml file in batis_info/mime: %r' % name)
            else:
                if not re.match(r'[a-zA-Z]+-\w+', os.path.splitext(name)[0]):
                    problems.append(
                        'Mime file should have vendor prefix (e.g. myorg-foo.xml): %r'
                                % name)
                path = os.path.join(mime_dir, name)
                try:
                    et = ElementTree.parse(path)
                except ElementTree.ParseError as e:
                    problems.append('Invalid XML in mime file (%s):\n%s'
                                        % (path, e))

        # Todo: verify that the XML contains mimetype data

    def verify_icons(self, problems):
        pa = problems.append
        icondir = self._relative('batis_info', 'icons')
        if not os.path.exists(icondir):
            # This is fine, it's optional
            return

        if not os.path.isdir(icondir):
            pa('batis_info/icons should be a directory')
            return

        themes = os.listdir(icondir)
        if themes and ('hicolor' not in themes):
            pa('Icon themes do not include hicolor, the default theme: %r' % themes)
        for theme in themes:
            themedir = os.path.join(icondir, theme)
            if not os.path.isdir(themedir):
                pa('batis_info/icons should only contain theme directories. '
                    '%s is not a directory' % themedir)
                continue

            for sizestr in os.listdir(themedir):
                sizedir = os.path.join(themedir, sizestr)
                if not os.path.isdir(sizedir):
                    pa('Icon theme directories should only contain size directories. '
                       '%s is not a directory' % sizedir)
                    continue
                m = re.match(r'(\d+)x\1', sizestr)
                if not m:
                    problems.append('Icon size directory does not match pattern NxN: %r' % sizestr)
                    continue

                for context in os.listdir(sizedir):
                    contextdir = os.path.join(sizedir, context)
                    if not os.path.isdir(contextdir):
                        pa('Icon size directories should only contain context directories. '
                           '%s is not a directory.' % contextdir)
                        continue

                    for basename in os.listdir(contextdir):
                        file = os.path.join(contextdir, basename)
                        if not os.path.isfile(file):
                            pa('Icon context directories should contain icon files. '
                               '%s is not a file.' % file)


    def verify(self):
        problems = []
        self.verify_batis_info_subdir(problems)
        self.verify_metadata(problems)
        self.verify_dependencies(problems)
        self.verify_desktop_files(problems)
        self.verify_mimetypes(problems)
        self.verify_icons(problems)
        return problems

def verify_tarball(path):
    if not tarfile.is_tarfile(path):
        return ['%s is not a tar file']
    return UnpackedDirVerifier(unpack_app_tarball(path)).verify()

def verify_tarball_or_directory(path):
    if os.path.isdir(path):
        return UnpackedDirVerifier(path).verify()
    else:
        return verify_tarball(path)

def main(argv=None):
    ap = argparse.ArgumentParser('batis verify')
    ap.add_argument('path', help="Path of a .app.tar.gz tarball, or of a directory")
    args = ap.parse_args(argv)
    problems = verify_tarball_or_directory(args.path)

    if problems:
        for problem in problems:
            print(problem)

        print()
        print(len(problems), "problems found in", args.path)
        sys.exit(1)

    else:
        print("No problems found in", args.path)
