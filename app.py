from typing import Dict
from typing import Any
from typing import Optional
import base64
import pickle
import logging
import os

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

logger = logging.getLogger()
logger.setLevel(getattr(logging, LOG_LEVEL))


def hello(event: Optional[Dict], context: Any):
    greeting = 'hello world3'
    logger.debug(f"returning: {greeting}")
    return greeting


def sprite_cp(event: Dict, context: Any):
    function_bytes = event['function'].encode('utf8')
    function_pkl = base64.decodebytes(function_bytes)
    function = pickle.loads(function_pkl)
    result = function()
    logger.debug(f"returning: {result}")
    return result


if __name__ == "__main__":
    print(hello(None, None))
