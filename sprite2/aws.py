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


class remote_invoke:
    def __init__(
            self,
            func,
            lambda_name='sprite',
            invoker=remote,
            ):
        self.func = func
        self.lambda_name = lambda_name
        self.invoker = invoker

    def __call__(self, *args, **kwds):
        lambda_str = str_encode(lambda: self.func(*args, **kwds))
        logger.debug(f'({self.func}) sending {byte_fmt(len(lambda_str))}')
        result = self.invoker(self.lambda_name, lambda_str)
        logger.debug(f'({self.func}) received {byte_fmt(len(result))}: {str(result)[:100]}')  # noqa
        result = str_decode(result)
        return result


def executor(event: str, context: Any):
    function = str_decode(event)
    result = function()
    result_str = str_encode(result)
    return {"result": result_str}
