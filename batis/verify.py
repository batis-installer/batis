import argparse
import json
import os
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
        metadata_file = self._relative('batis_info', 'metadata.json')
        if not os.path.isfile(metadata_file):
            problems.append('No file batis_info/metadata.json')
            return

        with open(metadata_file, 'r') as f:
            try:
                metadata = json.load(f)
            except ValueError as e:
                problems.append('batis_info/metadata.json is not valid JSON: %s' % e)
                return

        # TODO: Verify the contents of the metadata file

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
                path = os.path.join(mime_dir, name)
                try:
                    et = ElementTree.parse(path)
                except ElementTree.ParseError as e:
                    problems.append('Invalid XML in mime file (%s):\n%s'
                                        % (path, e))

        # Todo: verify that the XML contains mimetype data

    def verify_icons(self, problems):
        pass

    def verify(self):
        problems = []
        self.verify_batis_info_subdir(problems)
        self.verify_metadata(problems)
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
