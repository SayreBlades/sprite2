from typing import Any
import logging
import json
import boto3
import base64
import threading

from sprite2.utils import str_encode
from sprite2.utils import str_decode
from sprite2.utils import byte_fmt

logger = logging.getLogger(__name__)


class AwsHttpError(Exception):
    pass


class AwsError(Exception):
    pass


def local(lambda_str, request_id=None, lambda_name=None):
    response = executor(lambda_str, None)
    return response['result']


def remote(lambda_str, request_id=None, lambda_name=None, lambda_client=None):
    lambda_json = json.dumps(lambda_str)
    if lambda_client is None:
        thread_local = threading.local()
        lambda_client = getattr(thread_local, 'lambda_client', None)
        if lambda_client is None:
            session = boto3.session.Session()
            lambda_client = session.client('lambda')
            thread_local.lambda_client = lambda_client
    lambda_name = lambda_name or "sprite"
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

    logger.debug(f'{request_id}sending {byte_fmt(len(lambda_str))}')
    lambda_response = lambda_client.invoke(**kwds)
    content_len = int(
        lambda_response['ResponseMetadata']['HTTPHeaders']['content-length'])
    logger.debug(f'{request_id}received {byte_fmt(content_len)}')

    if lambda_response['StatusCode'] != 200:
        raise AwsHttpError(f"invalid http response: {lambda_response}")
    response = lambda_response['Payload'].read()
    lambda_response['Payload'].close()
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
            invoker=remote,
            request_id=None,
            ):
        self.request_id = request_id
        self.func = func
        self.invoker = invoker

    def __call__(self, *args, **kwds):
        lambda_str = str_encode(lambda: self.func(*args, **kwds))
        result = self.invoker(lambda_str, self.request_id)
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
