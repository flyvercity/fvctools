''' Requirement Management System (RMS) tool. '''

from pathlib import Path
import tomllib
import logging as lg


def add_argparser(subparsers):
    parser = subparsers.add_parser('rms', help='Requirement Management System (RMS) tool.')
    parser.add_argument('--config', help='Configuration file', default='rms.toml')
    parser.add_argument('--revision', help='Revision number', default='HEAD')


class Config:
    def __init__(self, args):
        try:
            self._revision = args.revision
            config_file = Path(args.config).resolve()
            lg.debug(f'Using configuration file: {config_file}')
            self._base_dir = config_file.parent
            config = tomllib.loads(config_file.read_text())

            if config.get('version') != 1:
                raise UserWarning('Unknown configuration file version (expected 1)')

        except Exception as exc:
            lg.error(f'Error during configuration: {exc}')
            raise UserWarning('Bad configuration file')


def main(args):
    Config(args)
    print('RMS main')
