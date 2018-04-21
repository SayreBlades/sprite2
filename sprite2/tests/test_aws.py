from sprite2 import aws
from sprite2 import utils


def test_executor():
    l = lambda: "hello world"  # noqa
    o = utils.str_encode(l)
    result = aws.executor(o, None)
    result = result['result']
    result = utils.str_decode(result)
    assert result == "hello world"
