import json
import os
import re
root_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(root_dir, '..', 'config/config.json')
codes = json.load(open(config_path))
def respondHttp(code):
    return codes["httpCodes"].get(code, 'Invalid code')
def respondReturn(code):
    return codes["returnCodes"].get(code, 'Invalid code')

def verifyArgs(method, arg):
    if method == 'http':
        if arg == None:
            code = ''
        else:
            code = respondHttp(arg)
        return code
    if method == 'return':
        if arg == None:
            code = ''
        else:
            code = respondReturn(arg)
        return code	
