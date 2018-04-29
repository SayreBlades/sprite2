from functools import partial
import logging
import concurrent.futures
import sys

from dask.local import get_async
import boto3

import sprite2


logger = logging.getLogger(__name__)


def apply_sync_lambda_factory(
        invoker=sprite2.aws.remote,
        ):
    def inner(
            func,
            args=(),
            kwds={},
            callback=None,
            ):
        key, _, _, _, _, _ = args
        logger.debug(f"executing task: {key}")
        func_wrapper = sprite2.aws.remote_invoke(
            func=func,
            invoker=invoker,
            request_id=key)
        try:
            res = func_wrapper(*args, **kwds)
        except BaseException as e:
            result = e, sys.exc_info()[2]
            failed = True
            res = key, result, failed
        if callback is not None:
            callback(res)
            logger.debug(f'callback with result {str(res)[:100]}')
    return inner


def apply_async_lambda_factory(
        executor=None,
        invoker=sprite2.aws.remote,
        ):
    def inner(
            func,
            args=(),
            kwds={},
            callback=None,
            ):
        key, _, _, _, _, _ = args
        task = lambda: apply_sync_lambda_factory(invoker)(func, args, kwds, callback)  # noqa
        executor.submit(task)
    return inner


def get(dsk, keys, **kwargs):
    num_workers = kwargs.pop('num_workers', 1000)
    lambda_name = kwargs.pop('lambda_name', 'sprite')
    invoker = kwargs.pop('invoker', sprite2.aws.remote)
    invoker = partial(invoker, lambda_name=lambda_name)
    if num_workers and num_workers > 1:
        executor = concurrent.futures.ThreadPoolExecutor(num_workers)
        apply = apply_async_lambda_factory(
            executor=executor,
            invoker=invoker,
            )
    else:
        apply = apply_sync_lambda_factory(
            invoker=invoker,
            )
    return get_async(apply, num_workers, dsk, keys, **kwargs)
