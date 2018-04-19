import logging
import base64
import json
import pickle
import concurrent

import boto3
import cloudpickle
from dask.local import get_async

logger = logging.getLogger(__name__)
executor = None


def invoke_remote_lambda(
        func,
        lambda_client=boto3.client('lambda'),
        ):
    logger.debug(f'invoking lambda {func}')
    lambda_pickled = cloudpickle.dumps(func)
    lambda_base64 = base64.encodebytes(lambda_pickled)
    lambda_str = lambda_base64.decode('utf-8')
    lambda_json = json.dumps(lambda_str)
    response = lambda_client.invoke(
          FunctionName='sprite',
          Payload=lambda_json,
    )
    response_bytes = response['Payload'].read()
    response_str = response_bytes.decode('utf-8')
    response_json = json.loads(response_str)
    result_bytes = response_json.encode('utf8')
    result_pkl = base64.decodebytes(result_bytes)
    result = pickle.loads(result_pkl)
    logger.debug(f'receiving result {result}')
    return result


def apply_async_lambda(func, args=(), kwds={}, callback=None):
    def doit():
        res = invoke_remote_lambda(lambda: func(*args, **kwds))
        if callback is not None:
            callback(res)
    executor.submit(doit)


def get(dsk, keys, **kwargs):
    global executor
    num_workers = kwargs.get('num_workers', 1000)
    if not executor:
        executor = concurrent.futures.ThreadPoolExecutor(num_workers)
    return get_async(apply_async_lambda, num_workers, dsk, keys, **kwargs)
