import logging
import concurrent

from dask.local import get_async

import sprite2

logger = logging.getLogger(__name__)
executor = None
invoker = None


class FuncWrapper:
    def __init__(self, func, name):
        self.func = func
        self.name = name

    def __repr__(self):
        return self.name

    def __call__(self):
        return self.func()


def apply_sync_lambda(func, args=(), kwds={}, callback=None):
    key, task_info, dumps, loads, get_id, pack_exception = args
    func_wrapper = FuncWrapper(
            lambda: func(*args, **kwds),
            name=str(key))
    res = sprite2.aws.invoke_lambda(func_wrapper, invoker=invoker)
    if callback is not None:
        callback(res)


def apply_async_lambda(func, args=(), kwds={}, callback=None):
    executor.submit(lambda: apply_sync_lambda(func, args, kwds, callback))


def get(dsk, keys, **kwargs):
    global executor
    global invoker
    num_workers = kwargs.pop('num_workers', 1000)
    invoker = kwargs.pop('invoker', sprite2.aws.remote)
    apply = apply_sync_lambda
    if num_workers and num_workers > 1:
        if not executor:
            executor = concurrent.futures.ThreadPoolExecutor(num_workers)
        apply = apply_async_lambda
    return get_async(apply, num_workers, dsk, keys, **kwargs)
