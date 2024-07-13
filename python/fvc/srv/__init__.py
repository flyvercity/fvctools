import click
import boto3


def update_service(cluster, service, desired_count):
    client = boto3.client('ecs')

    response = client.update_service(
        cluster=cluster,
        service=service,
        desiredCount=desired_count
    )

    return response


@click.command()
@click.option('--cluster', help='ECS cluster name', default='FeintDemo')
@click.option('--revision', help='Revision number', default='feint-demo-service')
@click.option('--start', help='Start service', is_flag=True)
@click.option('--stop', help='Stop service', is_flag=True)
def srv(cluster, revision, start, stop):
    if start:
        update_service(cluster, revision, 1)
        return

    if stop:
        update_service(cluster, revision, 0)
        return

    raise UserWarning('No action specified (--start or --stop)')
