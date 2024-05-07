import logging as lg
from argparse import ArgumentParser

import fvc.rms as rms
import fvc.srv as srv


subsystems = {
    'rms': rms,
    'srv': srv
}


def main():
    try:
        parser = ArgumentParser()

        parser.add_argument(
            '-v', '--verbose', action='store_true', help='sets logging level to debug')

        parser.add_argument(
            '--output-format', choices=['json'], default='json',
            help='output format (default: json)')

        subparsers = parser.add_subparsers(dest='subsystem')

        for subsystem in subsystems.items():
            name, module = subsystem
            module.add_argparser(name, subparsers)

        args = parser.parse_args()
        lg.basicConfig(level=lg.DEBUG if args.verbose else lg.INFO)

        if handler := subsystems.get(args.subsystem).main:  # type: ignore
            handler(args)
        else:
            raise UserWarning(f'Unknown subsystem: {args.subsystem}')

    except UserWarning as e:
        lg.error(e)


if __name__ == '__main__':
    main()
