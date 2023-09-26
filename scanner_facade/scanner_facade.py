from scanner.scanner import Scanner

class ScannerFacade:
    def __init__(self, login_url: str):
        self.scanner = Scanner(login_url)

    def scan(self, mail: str, password: str, secret: str):
        self.scanner.start(mail, password, secret)