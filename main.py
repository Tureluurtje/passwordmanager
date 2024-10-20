from core import logup

class Main:
    def start(account_owner, username, password, code):
        if account_owner:
            return Main.login(username, password, code)
        else: 
            return Main.register(username, password, code)

    def login(username, password, code):
        loggedIn, masterPassword, log = logup.login(username, password, code)
        if log == True:
            if loggedIn:
                logup.log(username, 1, "login")
                return '600'
            else: 
                logup.log(username, 0, "login")
                return '700'
        else:
            return log

    def register(account_owner, username, password, code):
        logup.register(username, password)
        return Main.login(username, password, code)

def startAuthenticate(account_owner, username, password, code):
    return Main.start(account_owner, username, password, int(code))
if __name__ == '__main__':
    x = startAuthenticate("True", "username", "password", "000000")
    print(x)