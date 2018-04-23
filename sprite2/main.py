import json
from pprint import pprint

import click
import boto3
import docker


def _update():
    print("updating...")
    aws_session = boto3.session.Session()
    aws_creds = aws_session.get_credentials()

    # docker build
    # - creates new zip
    # - updates remote aws lambda code
    docker_client = docker.from_env()
    docker_client.images.build(path='.', forcerm=True)
    aws_response = docker_client.containers.run(
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


def _create():
    print("creating...")
    aws_session = boto3.session.Session()
    aws_creds = aws_session.get_credentials()
    cf_client = boto3.client('cloudformation')
    cf_template_str = open('./config/cloudformation.yaml', 'r').read()
    aws_response = cf_client.create_stack(
        StackName='sprite',
        TemplateBody=cf_template_str,
        Capabilities=['CAPABILITY_IAM'],
    )
    pprint(aws_response)

    # docker build
    # - creates new zip
    # - updates remote aws lambda code
    docker_client = docker.from_env()
    docker_client.images.build(path='.', forcerm=True)
    aws_response = docker_client.containers.run(
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


def _delete():
    cf_client = boto3.client('cloudformation')
    aws_response = cf_client.delete_stack(StackName='sprite')
    pprint(aws_response)


@click.group()
def cli():
    pass


@cli.command('update')
def update():
    _update()


@cli.command('create')
def create():
    _create()


@cli.command('delete')
def delete():
    _delete()
