import argparse
from pathlib import Path
import sys

from .install import get_install_scheme

def iter_installed_applications():
    for schemename in ['user', 'system']:
        appsdir = Path(get_install_scheme(schemename)['application'])
        for d in appsdir.iterdir():
            if (d / 'batis_info').is_dir():
                yield d.absolute()

def display_installed_applications():
    names = sorted(d.name for d in iter_installed_applications())
    for n in names:
        print(n)

def json_installed_applications():
    res = []
    for d in iter_installed_applications():
        res.append({'name': d.name, 'path': str(d)})

    import json
    json.dump(res, sys.stdout, indent=1)

def main(argv=None):
    ap = argparse.ArgumentParser(prog='batis installtar')
    ap.add_argument('--json', action='store_true',
            help='Format output as a machine-readable JSON array')
    args = ap.parse_args(argv)

    if args.json:
        json_installed_applications()
    else:
        display_installed_applications()
