import json
import os
import pdb

from botocore.exceptions import ClientError
from halo import Halo
from docker.errors import BuildError
import click
import boto3
import docker


client_cf = boto3.client('cloudformation')


def get_yaml():
    file_name = os.path.dirname(__file__)
    file_name = os.path.join(file_name, '../config/cloudformation.yaml')
    file_name = os.path.abspath(file_name)
    return file_name


def get_aws_requirements():
    file_name = os.path.dirname(__file__)
    file_name = os.path.join(file_name, '../requirements-aws.txt')
    file_name = os.path.abspath(file_name)
    return file_name


def get_docker_path():
    file_name = os.path.dirname(__file__)
    file_name = os.path.join(file_name, '../')
    file_name = os.path.abspath(file_name)
    return file_name


def _create(
        cloud_formation_yaml_file,
        aws_requirements_file,
        docker_path=get_docker_path(),
        ):
    spinner = Halo(text='creating cloudformation template', spinner='dots')
    spinner.start()
    os.path.basename(__file__)
    try:
        client_cf.create_stack(
            StackName='sprite',
            TemplateBody=open(cloud_formation_yaml_file, 'r').read(),
            Capabilities=['CAPABILITY_IAM'],
        )
    except ClientError as e:
        if e.response['Error']['Code'] != 'AlreadyExistsException':
            raise

    spinner.succeed('created lambda skeleton')
    spinner.start()
    spinner.text = 'building docker'

    # docker build
    # - creates new zip
    # - updates remote aws lambda code
    try:
        docker_client = docker.from_env()
        image, events = docker_client.images.build(
            path=docker_path,
            forcerm=True,
            tag='sprite:latest')
        aws_session = boto3.session.Session()
        spinner.succeed('built docker')
        pdb.set_trace()
        spinner.start()
        spinner.text = 'deploying function code'
        aws_creds = aws_session.get_credentials()
        requirements = (open('./requirements-aws.txt', 'r').read().replace('\n', ' '))  # noqa
        print('requirements: ', requirements)
        aws_response = docker_client.containers.run(
                image='sprite:latest',
                command='sprite',
                environment={
                    'AWS_ACCESS_KEY_ID': aws_creds.access_key,
                    'AWS_SECRET_ACCESS_KEY': aws_creds.secret_key,
                    'AWS_DEFAULT_REGION': aws_session.region_name,
                    'REQUIREMENTS': requirements,
                    }
                )
        aws_response = aws_response.decode('utf8')
        aws_response = json.loads(aws_response)
        spinner.succeed('code deployed')
    except BuildError as e:
        spinner.fail(str(e))


class BadStatusException(Exception):
    pass


def _delete(stack_name):
    spinner = Halo(text='deleting', spinner='dots')
    spinner.start()
    client_cf = boto3.client('cloudformation')
    try:
        while True:
            client_cf.delete_stack(StackName='sprite')
            aws_response = client_cf.describe_stacks(StackName='sprite')
            spinner.text = 'checking delete status'
            status = aws_response['Stacks'][0]['StackStatus']
            if status != 'DELETE_IN_PROGRESS':
                raise BadStatusException(status)
    except BadStatusException as e:
        print(f"received bad status: {status}")
    except ClientError as e:
        if 'does not exist' in str(e):
            spinner.succeed('complete')
        else:
            raise e
    finally:
        spinner.stop()


@click.group()
def cli():
    pass


@cli.command('create')
@click.option(
    '--template-file',
    prompt=True,
    default=get_yaml(),
    )
@click.option(
    '--aws-requirements-file',
    prompt=True,
    default=get_aws_requirements(),
    )
def create(template_file, aws_requirements_file):
    _create(template_file, aws_requirements_file)


@cli.command('delete')
@click.option(
    '--stack-name',
    default='sprite',
    )
def delete(stack_name):
    _delete(stack_name)
