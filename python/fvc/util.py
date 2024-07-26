import json

from typing import Any, Dict
from pygments import highlight
from pygments.lexers.jsonnet import JsonnetLexer
from pygments.formatters import TerminalFormatter


JSON = Dict[str, Any]
JSON_INDENT = 2


def json_print(params, data: JSON):
        
    if not params['no_pprint']:
        json_str = json.dumps(data, indent=JSON_INDENT, sort_keys=True)
        print(highlight(json_str, JsonnetLexer(), TerminalFormatter()))
    else:
        print(json.dumps(data))
