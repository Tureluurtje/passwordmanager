def respond(code):
    return codes.gbet(code, 'Invalid code')

def verifyArgs(*args):
    for arg in args:
        if arg == None:
            