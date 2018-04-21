from typing import Any
import logging
import json
import boto3

from sprite2.utils import str_encode
from sprite2.utils import str_decode
from sprite2.utils import byte_fmt

logger = logging.getLogger(__name__)
lambda_client = None


class AwsHttpError(Exception):
    pass


class AwsError(Exception):
    pass


def local(lambda_name, lambda_str):
    response = executor(lambda_str, None)
    return response['result']


def remote(lambda_name, lambda_str):
    global lambda_client
    lambda_json = json.dumps(lambda_str)
    lambda_client = lambda_client or boto3.client('lambda')
    response = lambda_client.invoke(
          FunctionName=lambda_name,
          Payload=lambda_json,
    )
    if response['StatusCode'] != 200:
        raise AwsHttpError(f"invalid http response: {response}")
    response = response['Payload'].read()
    response = response.decode('utf-8')
    response = json.loads(response)
    if 'result' not in response:
        raise AwsError(f"invalid response: {response}")
    result = response['result']
    return result


def invoke_lambda(
        func,
        lambda_name: str='sprite',
        lambda_client=None,
        invoker=None,
        ):
    invoker = invoker or remote
    lambda_str = str_encode(func)
    logger.debug(f'({func}) sending {byte_fmt(len(lambda_str))}')
    result = invoker(lambda_name, lambda_str)
    logger.debug(f'({func}) received {byte_fmt(len(result))}: {str(result)[:100]}')  # noqa
    result = str_decode(result)
    return result


def executor(event: str, context: Any):
    function = str_decode(event)
    result = function()
    result_str = str_encode(result)
    return {"result": result_str}
