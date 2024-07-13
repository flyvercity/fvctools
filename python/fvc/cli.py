import click
import logging as lg
from argparse import ArgumentParser
import traceback

import fvc.rms
import fvc.srv
import fvc.df


@click.group()
@click.pass_context
@click.option('-v', '--verbose', is_flag=True, help='sets logging level to debug')
@click.option('--json', is_flag=True, help='Make JSON default output format instead free form')
def cli(ctx, verbose, json):
    ctx.ensure_object(dict)
    ctx.obj['Verbose'] = verbose
    lg.basicConfig(level=lg.DEBUG if verbose else lg.INFO)
    lg.debug('Verbose mode is on')
    ctx.obj['Json'] = json
    lg.debug(f'JSON mode is {"on" if json else "off"}')


cli.add_command(fvc.srv.srv)
cli.add_command(fvc.rms.rms)


def main():
    try:
        cli()
        return 0

    except UserWarning as e:
        lg.error(e)
        return 1

    except Exception as e:
        lg.error(f'Exception occurred: {e}')

        argparse = ArgumentParser()
        argparse.add_argument('-v', '--verbose', action='store_true')
        args, _ = argparse.parse_known_args()

        if args.verbose:
            lg.error(traceback.format_exc())

        return 2


if __name__ == '__main__':
    exit(main())
