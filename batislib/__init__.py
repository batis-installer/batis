import sys

def main(argv=None):
    if argv is None:
        argv = sys.argv

    if len(argv) < 2:
        print('No subcommand specified')
        sys.exit(1)

    subcmd = argv[1]
    if subcmd == 'verify':
        from .verify import main
        main(argv[2:])

    elif subcmd == 'unpack':
        from .tarball import unpack_app_tarball
        dir = unpack_app_tarball(argv[2])
        print('dir: {!r}'.format(dir))

    elif subcmd == 'backend-install':
        from .install import main
        main(argv[2:])

    elif subcmd == 'gui-install-tarball':
        from gui.app import main
        main(argv[2:])

    else:
        print('Unknown subcommand: {!r}'.format(subcmd))
        sys.exit(1)
