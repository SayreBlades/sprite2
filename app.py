from typing import Dict
from typing import Any
from typing import Optional
import base64
import pickle


def hello(event: Optional[Dict], context: Any):
    return 'hello world3'


def sprite_cp(event: Dict, context: Any):
    function_bytes = event['function'].encode('utf8')
    function_pkl = base64.decodebytes(function_bytes)
    function = pickle.loads(function_pkl)
    return function()


if __name__ == "__main__":
    print(hello(None, None))
