from core import logup, verifyArgs, passwordmanage
from api import start_server
class Main:
    def startLogup(account_owner, username, password, code):
        def login(username, password, code, masterpass=False):
            loggedIn, masterPassword, log = logup.login(username, password, code)
            if log == True:
                if loggedIn:
                    logup.log(username, 1, "login")
                    if masterPassword:
                        return (True, '600', masterPassword)
                    else:
                        return (True, '600')
                else: 
                    logup.log(username, 0, "login")
                    if masterPassword:
                        return (False, '700', masterPassword)
                    else:
                        return (False, '700')
            else:
                return log

        def register(username, password, code):
            logup.register(username, password)
            return login(username, password, code)

        if account_owner:
            return login(username, password, code)
        else: 
            return register(username, password, code)
    def startPassword(method, username, password, code, accountname='', accountpassword=''):
        Verify, masterpassword, code = Main.startLogup.login(username, password, code, masterpass=True)
        if method == "add":
            if code == "600":
                passwordmanage.addpass(username, masterpassword, accountname, accountpassword)
        elif method == "get":
            return logup.getpass(username, password, code)
        elif method == "delete":
            return logup.deletepass(username, password, code)
        elif method == "update":
            return logup.updatepass(username, password, code)
        else:
            return "Invalid method"
def start(method, account_owner, username, password, code):
    if method == "authenticate":
        args = Main.startLogup(account_owner, username, password, int(code))
        translated_args = verifyArgs('return', args)
        return translated_args
    elif method == "password":
        args = Main.startPassword(method, username, password, code)

if __name__ == '__main__':
    start_server()