from __future__ import print_function

from importlib import import_module
import sys

__version__ = '0.1'

subcommands = [
    # User focussed
    ('install', '.urlinstall:main',
         'Download and install an application from a URL'),
    ('installtar', '.install:main',
         'Install a tarball that was already downloaded'),
    ('list', '.list:main',
         'List installed applications'),
    ('uninstall', '.uninstall:main',
         'Remove an installed application'),
    # Developer focussed
    ('verify', '.verify:main',
         'Check an application directory or tarball for problems'),
    ('pack', '.tarball:pack_main',
         'Pack an application directory into a tarball'),
    ('verify-index', '.verify_index:main',
         'Check a batis_index.json file for problems'),
]

def _load(entry_point):
    modname, func = entry_point.split(':')
    mod = import_module(modname, 'batislib')
    return getattr(mod, func)

def main(argv=None):
    if argv is None:
        argv = sys.argv

    if len(argv) < 2:
        print('No subcommand specified')
        print('Available subcommands:', *(s[0] for s in subcommands))
        return 2

    subcmd = argv[1]

    if subcmd in {'--help', '-h'}:
        print('Batis - install and distribute desktop applications')
        print('Subcommands:')
        for name, ep, descr in subcommands:
            print('  {:<12} - {}'.format(name, descr))
        return 0
    
    for name, ep, descr in subcommands:
        if subcmd == name:
            sub_main = _load(ep)
            return sub_main(argv[2:])

    print('Unknown subcommand: {!r}'.format(subcmd))
    print('Available subcommands:', *(s[0] for s in subcommands))
    return 2
