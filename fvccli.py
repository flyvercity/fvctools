import logging as lg
from argparse import ArgumentParser

import fvc.rms as rms
import fvc.srv as srv
import fvc.conv as conv


subsystems = {
    'rms': rms,
    'srv': srv,
    'conv': conv
}


def main():
    try:
        parser = ArgumentParser()

        parser.add_argument(
            '-v', '--verbose', action='store_true', help='sets logging level to debug')

        parser.add_argument(
            '--json', action='store_true',
            help='Make JSON default output format instead free form'
        )

        subparsers = parser.add_subparsers(
            dest='subsystem',
            description='select a specific tool to run',
            required=True
        )

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
