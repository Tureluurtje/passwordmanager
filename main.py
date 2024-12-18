from core import logup, verifyArgs, passwordmanage
class Main:
    def startLogup(account_owner, username, password, masterpass=False):
        def login(username, password, masterpass=False):
            loggedIn, masterPassword, log, userId = logup.login(username, password)
            if log == True:
                if loggedIn:
                    logup.log(username, 1, "login")
                    if masterPassword:
                        return (True, '600', masterPassword, userId)
                    else:
                        return (True, '600', userId)
                else: 
                    logup.log(username, 0, "login")
                    if masterPassword:
                        return (False, '700', masterPassword, userId)
                    else:
                        return (False, '700', userId)
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
    def startPassword(method, username, password, accountname='', accountusername='', accountpassword='', accountnotes=''):
        Verify, code, masterpassword, userId = Main.startLogup(account_owner=True, username=username, password=password)

        if method == "add":
            if code == "600":
                result = passwordmanage.addpass(userId, masterpassword, accountname, accountusername, accountpassword, accountnotes)
                if result[0] == True:
                    logup.log(username, 1, "addpassword")
                    return (True, '200')
                else:
                    logup.log(username, 0, "addpassword")
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
            return (False, '702')
def start(method, username, password, account_owner='', accountname='', accountusername='', accountpassword='', accountnotes='', passwordmethod=''):
    if method == "authenticate":
        args = Main.startLogup(account_owner, username, password)
        if isinstance(args, tuple):
            return verifyArgs('http', args)
        return args
    elif method == "password":
        args = Main.startPassword(passwordmethod, username, password, accountname, accountusername, accountpassword, accountnotes)