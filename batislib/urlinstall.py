# -*- coding: utf-8 -*-
import argparse
import os.path
import requests
from shutil import rmtree
from tempfile import mkdtemp

from .install import ApplicationInstaller, get_install_scheme
from . import select_build

class NullProgress(object):
    def start(self, max_value=None):
        pass
    
    def update(self, value=None):
        pass
    
    def finish(self):
        pass

def download(url, target, progress=None):
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
        for chunk in r.iter_content(chunk_size=16384): 
            if chunk:
                f.write(chunk)
                recvd += len(chunk)
                try:
                    progress.update(recvd)
                except ValueError:
                    # Probably the HTTP headers lied.
                    pass

    progress.finish()

def install(url, scheme, backend=False):
    if not url.endswith('.json'):
        url = url.rstrip('/') + '/batis_index.json'
    r = requests.get(url)
    candidates = r.json()['builds']
    
    build = select_build.select_latest(select_build.filter_eligible(candidates))

    td = mkdtemp()
    tarball = os.path.join(td, 'app.tar.gz')
    
    from progressbar import DataTransferBar
    try:
        download(build['url'], tarball, progress=DataTransferBar())
        ai = ApplicationInstaller(tarball, scheme)
        ai.install(backend=backend)
    finally:
        rmtree(td)

def main(argv=None):
    ap = argparse.ArgumentParser(prog='batis install')
    ap.add_argument('--system', action='store_true',
            help='Install systemwide, instead of for the user')
    ap.add_argument('url', help='The URL from which to install')
    args = ap.parse_args(argv)
    
    scheme = get_install_scheme('system' if args.system else 'user')
    install(args.url, scheme)
