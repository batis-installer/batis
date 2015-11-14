# -*- coding: utf-8 -*-
import argparse
import hashlib
import logging
import os.path
import requests
from shutil import rmtree
from tempfile import mkdtemp

from .install import ApplicationInstaller, get_install_scheme
from .log import enable_colourful_output
from . import select_build

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
    elif url.startswith('http://'):
        url = 'https' + url[4:]
    
    if not url.endswith('.json'):
        url = url.rstrip('/') + '/batis_index.json'
    return url

def install(url, scheme, backend=False):
    url = prepare_index_url(url)
    r = requests.get(url)
    candidates = r.json()['builds']
    
    build = select_build.select_latest(select_build.filter_eligible(candidates))
    
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
    ap.add_argument('--system', action='store_true',
            help='Install systemwide, instead of for the user')
    ap.add_argument('url', help='The URL from which to install')
    args = ap.parse_args(argv)
    
    enable_colourful_output(level=logging.INFO)

    scheme = get_install_scheme('system' if args.system else 'user')
    install(args.url, scheme)
