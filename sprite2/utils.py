import base64
import pickle

import cloudpickle


def str_encode(o):
    o_pkl = cloudpickle.dumps(o)
    o_base64 = base64.encodebytes(o_pkl)
    o_str = o_base64.decode('utf-8')
    return o_str


def str_decode(s):
    s_bytes = s.encode('utf8')
    s_pkl = base64.decodebytes(s_bytes)
    return pickle.loads(s_pkl)


def byte_fmt(num):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
