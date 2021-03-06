# -*- coding: utf-8 -*-
import argparse
import hashlib
import logging
import os.path
import requests
from shutil import rmtree
from tempfile import mkdtemp
from urllib.parse import urlparse, urlunparse

from .install import ApplicationInstaller, get_install_scheme
from .log import enable_colourful_output
from . import select_build

INDEX_FORMAT_MAJOR = 1
INDEX_FORMAT_MINOR = 0

class FutureIndexFormat(Exception):
    def __init__(self, major_version):
        self.major_version = major_version

    def __str__(self):
        return ("The index format is version {}, "
                "but this version of Batis only understands version {}. "
                "Please upgrade Batis to install this package."
                ).format(self.major_version, INDEX_FORMAT_MAJOR)

class NullProgress(object):
    def start(self, max_value=None):
        pass
    
    def update(self, value=None):
        pass
    
    def finish(self):
        pass

def download(url, target, progress=None, hashobj=None):
    """Download a file using requests.
    
    This is like urllib.request.urlretrieve, but requests validates SSL
    certificates by default.
    """
    if progress is None:
        progress = NullProgress()

    from . import __version__
    headers = {'user-agent': 'Batis/'+__version__}
    r = requests.get(url, headers=headers, stream=True)
    r.raise_for_status()

    # Start the progress tracker
    max_value = None
    if 'content-length' in r.headers:
        max_value = int(r.headers['content-length'])
    progress.start(max_value=max_value)
    recvd = 0

    with open(target, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                if hashobj is not None:
                    hashobj.update(chunk)
                recvd += len(chunk)
                try:
                    progress.update(recvd)
                except ValueError:
                    # Probably the HTTP headers lied.
                    pass

    progress.finish()

def prepare_index_url(url):
    if '//' not in url:
        url = 'https://' + url
    
    parsed = urlparse(url)
    if parsed.scheme not in {'http', 'https', 'batis'}:
        raise ValueError('Unknown URL scheme %s' % parsed.scheme)

    return urlunparse(('https',) + parsed[1:])

def install(url, scheme, confirm=False, backend=False):
    url = prepare_index_url(url)
    r = requests.get(url)
    index = r.json()
    
    if index['format_version'][0] > INDEX_FORMAT_MAJOR:
        raise FutureIndexFormat(index['format_version'][0])

    print('Installing from', urlparse(url).netloc, ':')
    print('--', index['name'], '--')
    print(index['byline'])
    print()
    if confirm:
        res = input('Continue installation? [y]/n >')
        if res and (res[0].lower() != 'y'):
            print('Not installing')
            return
    
    build = select_build.select_latest(
                select_build.filter_eligible(index['builds']))
    
    if 'sha512' in build:
        hashobj = hashlib.sha512()
    elif not build['url'].startswith('https:'):
        raise KeyError("'sha512' field is required for HTTP downloads")
    else:
        hashobj = None

    td = mkdtemp()
    tarball = os.path.join(td, 'app.tar.gz')
    
    from progressbar import DataTransferBar
    try:
        download(build['url'], tarball, progress=DataTransferBar(),
                 hashobj=hashobj)
        if hashobj is not None:
            if hashobj.hexdigest() != build['sha512']:
                # TODO: Automatic retrying?
                raise ValueError("Download was corrupted - hash didn't match")
        ai = ApplicationInstaller(tarball, scheme)
        ai.install(backend=backend)
    finally:
        rmtree(td)


def main(argv=None):
    ap = argparse.ArgumentParser(prog='batis install')
    ap.add_argument('--confirm', action='store_true',
            help='Prompt for confirmation before installing')
    ap.add_argument('--prompt-before-exit', action='store_true',
            help=argparse.SUPPRESS)
    ap.add_argument('--system', action='store_true',
            help='Install systemwide, instead of for the user')
    ap.add_argument('url', help='The URL from which to install')
    args = ap.parse_args(argv)
    
    enable_colourful_output(level=logging.INFO)

    exitcode = 0

    try:
        scheme = get_install_scheme('system' if args.system else 'user')
        install(args.url, scheme, confirm=args.confirm)
    except:
        import traceback
        traceback.print_exc()
        exitcode = 1

    if args.prompt_before_exit:
        input('Press ENTER to close')

    return exitcode
