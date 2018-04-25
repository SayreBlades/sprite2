from functools import partial
import logging
import concurrent

from dask.local import get_async

import sprite2


logger = logging.getLogger(__name__)


def apply_sync_lambda(
        func,
        args=(),
        kwds={},
        callback=None,
        invoker=sprite2.aws.remote,
        lambda_name='sprite',
        ):
    key, task_info, dumps, loads, get_id, pack_exception = args
    func_wrapper = sprite2.aws.remote_invoke(
        func=func,
        lambda_name=lambda_name,
        invoker=invoker,
        request_id=key)
    res = func_wrapper(*args, **kwds)
    if callback is not None:
        callback(res)


def apply_async_lambda(
        func,
        args=(),
        kwds={},
        callback=None,
        executor=None,
        invoker=sprite2.aws.remote,
        lambda_name='sprite',
        ):
    key, task_info, dumps, loads, get_id, pack_exception = args
    task = lambda: apply_sync_lambda(func, args, kwds, callback, invoker, lambda_name)  # noqa
    executor.submit(task)


def get(dsk, keys, **kwargs):
    num_workers = kwargs.pop('num_workers', 1000)
    lambda_name = kwargs.pop('lambda_name', 'sprite')
    invoker = kwargs.pop('invoker', sprite2.aws.remote)
    if num_workers and num_workers > 1:
        executor = concurrent.futures.ThreadPoolExecutor(num_workers)
        apply = partial(
            apply_async_lambda,
            executor=executor,
            invoker=invoker,
            lambda_name=lambda_name,
            )
    else:
        apply = partial(
            apply_sync_lambda,
            invoker=invoker,
            lambda_name=lambda_name,
            )
    return get_async(apply, num_workers, dsk, keys, **kwargs)
