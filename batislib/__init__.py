import sys

__version__ = '0.1'

def main(argv=None):
    if argv is None:
        argv = sys.argv

    if len(argv) < 2:
        print('No subcommand specified')
        print('Available commands: verify, install, urlinstall, uninstall, unpack, pack')
        sys.exit(1)

    subcmd = argv[1]
    if subcmd == 'verify':
        from .verify import main
        main(argv[2:])

    elif subcmd == 'unpack':
        from .tarball import unpack_app_tarball
        dir = unpack_app_tarball(argv[2])
        print('dir: {!r}'.format(dir))
    
    elif subcmd == 'pack':
        from .tarball import pack_main
        pack_main(argv[2:])

    elif subcmd == 'install':
        from .install import main
        main(argv[2:])
    
    elif subcmd == 'urlinstall':
        from .urlinstall import main
        main(argv[2:])
    
    elif subcmd == 'uninstall':
        from .uninstall import main
        main(argv[2:])

    else:
        print('Unknown subcommand: {!r}'.format(subcmd))
        sys.exit(1)
