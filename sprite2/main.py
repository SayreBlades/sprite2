from pprint import pprint
import json
import os

import click
import boto3
import docker


def get_yaml():
    file_name = os.path.dirname(__file__)
    file_name = os.path.join(file_name, '../config/cloudformation.yaml')
    file_name = os.path.abspath(file_name)
    return file_name


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


def _create(cf_yaml):
    os.path.basename(__file__)
    print("creating...")
    aws_session = boto3.session.Session()
    aws_creds = aws_session.get_credentials()
    cf_client = boto3.client('cloudformation')
    aws_response = cf_client.create_stack(
        StackName='sprite',
        TemplateBody=open(cf_yaml, 'r').read(),
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
@click.option('--template-file', prompt=True, default=get_yaml())
def create(template_file):
    _create(template_file)


@cli.command('delete')
def delete():
    _delete()
