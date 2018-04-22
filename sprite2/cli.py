import json
from pprint import pprint

import click
import boto3
import docker


@click.group()
def cli():
    pass


@cli.command('update')
def update():
    aws_session = boto3.session.Session()
    aws_creds = aws_session.get_credentials()
    client = docker.from_env()
    with click.progressbar() as bar:
        client.images.build(path='.', forcerm=True)
        aws_response = client.containers.run(
                image='sprite2',
                command='sprite',
                environment={
                    'AWS_ACCESS_KEY_ID': aws_creds.access_key,
                    'AWS_SECRET_ACCESS_KEY': aws_creds.secret_key,
                    'AWS_DEFAULT_REGION': aws_session.region_name
                    }
                )
        aws_response = aws_response.decode('utf8')
        aws_response = json.loads(aws_response)
        pprint(aws_response)


@cli.command('create')
def create():
    client = boto3.client('cloudformation')
    linestring = open('./config/cloudformation.yaml', 'r').read()
    response = client.create_stack(
        StackName='sprite',
        TemplateBody=linestring,
        # TemplateBody='string',
        # TemplateURL='string',
        # Parameters=[
        #     {
        #         'ParameterKey': 'string',
        #         'ParameterValue': 'string',
        #         'UsePreviousValue': True|False,
        #         'ResolvedValue': 'string'
        #     },
        # ],
        # DisableRollback=True|False,
        # RollbackConfiguration={
        #     'RollbackTriggers': [
        #         {
        #             'Arn': 'string',
        #             'Type': 'string'
        #         },
        #     ],
        #     'MonitoringTimeInMinutes': 123
        # },
        # TimeoutInMinutes=123,
        # NotificationARNs=[
        #     'string',
        # ],
        # Capabilities=[
        #     'CAPABILITY_IAM'|'CAPABILITY_NAMED_IAM',
        # ],
        # ResourceTypes=[
        #     'string',
        # ],
        # RoleARN='string',
        # OnFailure='DO_NOTHING'|'ROLLBACK'|'DELETE',
        # StackPolicyBody='string',
        # StackPolicyURL='string',
        # Tags=[
        #     {
        #         'Key': 'string',
        #         'Value': 'string'
        #     },
        # ],
        # ClientRequestToken='string',
        # EnableTerminationProtection=True|False
    )
    print(f'created {response}')
