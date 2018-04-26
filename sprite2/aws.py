from typing import Any
import logging
import json
import boto3
import base64

from sprite2.utils import str_encode
from sprite2.utils import str_decode
from sprite2.utils import byte_fmt

logger = logging.getLogger(__name__)
lambda_client = None


class AwsHttpError(Exception):
    pass


class AwsError(Exception):
    pass


def local(lambda_name, lambda_str, request_id=None):
    response = executor(lambda_str, None)
    return response['result']


def remote(lambda_name, lambda_str, request_id=None):
    global lambda_client
    lambda_json = json.dumps(lambda_str)
    lambda_client = lambda_client or boto3.client('lambda')
    kwds = {
        "FunctionName": lambda_name,
        "Payload": lambda_json,
    }
    if request_id:
        cxt = json.dumps({'custom': {'request_id': request_id}})
        cxt = cxt.encode('utf8')
        cxt = base64.b64encode(cxt)
        cxt = cxt.decode('utf8')
        kwds["ClientContext"] = cxt
        request_id = str(request_id) + " "
    else:
        request_id = ""

    try:
        logger.debug(f'{request_id}sending {byte_fmt(len(lambda_str))}')
        response = lambda_client.invoke(**kwds)
        content_len = int(
            response['ResponseMetadata']['HTTPHeaders']['content-length'])
        logger.debug(f'{request_id}received {byte_fmt(content_len)}')
    except Exception as e:
        logger.error(e)
        raise e
    if response['StatusCode'] != 200:
        raise AwsHttpError(f"invalid http response: {response}")
    response = response['Payload'].read()
    response = response.decode('utf-8')
    response = json.loads(response)
    if 'result' not in response:
        err_str = f"invalid response: {response}"
        logger.error(err_str)
        raise AwsError(err_str)
    result = response['result']
    return result


class remote_invoke:
    def __init__(
            self,
            func,
            lambda_name='sprite',
            invoker=remote,
            request_id=None,
            ):
        self.request_id = request_id
        self.func = func
        self.lambda_name = lambda_name
        self.invoker = invoker

    def __call__(self, *args, **kwds):
        lambda_str = str_encode(lambda: self.func(*args, **kwds))
        result = self.invoker(self.lambda_name, lambda_str, self.request_id)
        result = str_decode(result)
        return result


def executor(event: str, context: Any):
    custom = context.client_context and context.client_context.custom
    custom = custom or {}
    requst_id = custom.get('request_id')
    if requst_id:
        print(f"processing request {requst_id}")
    function = str_decode(event)
    result = function()
    result_str = str_encode(result)
    return {"result": result_str}
