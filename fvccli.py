import logging as lg
from argparse import ArgumentParser

import fvc.tools.rms as rms


subsystems = {
    'rms': rms.main
}


def main():
    try:
        parser = ArgumentParser()
        parser.add_argument('-v', '--verbose', action='store_true', help='sets logging level to debug')
        subparsers = parser.add_subparsers(dest='subsystem')
        rms.add_argparser(subparsers)
        args = parser.parse_args()
        lg.basicConfig(level=lg.DEBUG if args.verbose else lg.INFO)

        if handler := subsystems.get(args.subsystem):
            handler(args)
        else:
            raise UserWarning(f'Unknown subsystem: {args.subsystem}')

    except UserWarning as e:
        lg.error(e)


if __name__ == '__main__':
    main()
