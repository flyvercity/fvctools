import logging as lg
from argparse import ArgumentParser
import traceback

import boto3
import click

import fvc.tools.rms
import fvc.tools.df


@click.group(help='Flyvercity CLI tools suite')
@click.pass_context
@click.option('--verbose', is_flag=True, help='sets logging level to debug')
@click.option('--json', is_flag=True, help='Make JSON default output format instead free form')
@click.option('--no-pprint', is_flag=True, help='Disable colored pretty printing')
@click.option('--aws-profile', help='AWS profile to use for S3 operations')
def cli(ctx, verbose, json, no_pprint, aws_profile):
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose

    lg.basicConfig(level=lg.DEBUG if verbose else lg.INFO)
    lg.debug(f'Verbose mode is {"on" if verbose else "off"}')

    lg.debug(
        f'JSON mode is {"on" if json else "off"} (pprint: {"off" if no_pprint else "on"})'
    )
    ctx.obj['JSON'] = json
    ctx.obj['no_pprint'] = no_pprint

    if aws_profile:
        lg.debug(f'Using AWS profile: {aws_profile}')
        boto3.setup_default_session(profile_name=aws_profile)


cli.add_command(fvc.tools.rms.rms)
cli.add_command(fvc.tools.df.df)


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
