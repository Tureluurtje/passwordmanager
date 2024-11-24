from core import logup, verifyArgs, passwordmanage
class Main:
    def startLogup(account_owner, username, password, masterpass=False):
        def login(username, password, masterpass=False):
            loggedIn, masterPassword, log = logup.login(username, password)
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

        def register(username, password, code, masterpass=False):
            logup.register(username, password)
            return login(username, password, code)

        if account_owner:
            return login(username, password)
        else: 
            account_owner = True
            return register(username, password, account_owner, masterpass=True)
    def startPassword(method, username, password, accountname='', accountpassword=''):
        Verify, masterpassword, code = Main.startLogup(account_owner=True, username=username, password=password)

        if method == "add":
            if code == "600":
                result = passwordmanage.addpass(username, masterpassword, accountname, accountpassword)
                if result == True:
                    return (True, '200')
                else:
                    return (False, '500')
            else:
                return (False, '700')
        elif method == "get":
            return logup.getpass(username, password, code)
        elif method == "delete":
            return logup.deletepass(username, password, code)
        elif method == "update":
            return logup.updatepass(username, password, code)
        else:
            return "Invalid method"
def start(method, account_owner, username, password, accountname='', accountpassword=''):
    if method == "authenticate":
        args = Main.startLogup(account_owner, username, password)
        if isinstance(args, tuple):
            return verifyArgs('http', args)
        return args
    elif method == "password":
        args = Main.startPassword(method, username, password, accountname, accountpassword)
        translated_args = verifyArgs('return', args)
        return translated_args
