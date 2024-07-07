import boto3


def update_service(cluster, service, desired_count):
    client = boto3.client('ecs')

    response = client.update_service(
        cluster=cluster,
        service=service,
        desiredCount=desired_count
    )

    return response


def add_argparser(name, subparsers):
    parser = subparsers.add_parser(name, help='Cloud services management tool')
    parser.add_argument('--cluster', help='ECS cluster name', default='FeintDemo')
    parser.add_argument('--revision', help='Revision number', default='feint-demo-service')
    parser.add_argument('--start', help='Start service', action='store_true')
    parser.add_argument('--stop', help='Stop service', action='store_true')


def main(args):
    if args.start:
        update_service(args.cluster, args.revision, 1)
        return

    if args.stop:
        update_service(args.cluster, args.revision, 0)
        return

    raise UserWarning('No action specified (--start or --stop)')
