from core import logup

class Main:
    def __init__(self, account_owner, username, password, code):
        if account_owner:
            self.login(username, password, code)
        else: 
            self.register(username, password)

    def login(self, username, password, code):
        loggedIn, masterPassword, log = logup.login(username, password, code)
        if log:
            if loggedIn:
                logup.log(username, 1, "login")
                print("Logged in!")
            else: 
                logup.log(username, 0, "login")
        else:
            pass

    def register(self, username, password):
        logup.register(username, password)
        self.login(username, password)


if __name__ == "__main__":
     Main(account_owner=True, username="tureluurtje", password="Tuinhek12!", code="118309")
