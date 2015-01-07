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

if __name__ == '__main__':
    main()