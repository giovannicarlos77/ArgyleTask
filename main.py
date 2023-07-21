import argparse
from scanner import Scanner

parser = argparse.ArgumentParser(description='Extract data of employee')
parser.add_argument('-mail', type=str, required=True)
parser.add_argument('-password', type=str, required=True)
parser.add_argument('-secret', type=str, required=True)
args = parser.parse_args()

if __name__ == "__main__":
    scanner = Scanner('https://www.upwork.com/ab/account-security/login')
    scanner.start(args.mail, args.password, args.secret)
