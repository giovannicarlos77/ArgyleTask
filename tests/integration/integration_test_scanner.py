import pytest
import os
import time
from scanner.scanner import Scanner, save_data_and_print


@pytest.fixture
def scanner_with_valid_credentials():
    scanner = Scanner("https://www.upwork.com/ab/account-security/login")
    scanner.mail = "recruitment+scanners+task@argyle.com"
    scanner.password = "ArgyleAwesome!@"
    scanner.secret = "TheDude"

    yield scanner


import pytest
import os
import time
from scanner.scanner import Scanner

@pytest.fixture
def scanner_with_valid_credentials():
    scanner = Scanner("https://www.upwork.com/ab/account-security/login")
    scanner.mail = "recruitment+scanners+task@argyle.com"
    scanner.password = "ArgyleAwesome!@"
    scanner.secret = "TheDude"
    yield scanner
    # Clean up cookies after each test
    cleanup_cookies(scanner)

def cleanup_cookies(scanner):
    cookie_filename = f"{scanner.mail}_cookies.pkl"
    cookie_path = os.path.join("cookies", cookie_filename)
    if os.path.exists(cookie_path):
        os.remove(cookie_path)

def test_scanner_without_cookies(scanner_with_valid_credentials):
    scanner = scanner_with_valid_credentials
    cleanup_cookies(scanner)

    scanner.start(scanner.mail, scanner.password, scanner.secret)

    dynamic_filename = f"{scanner.mail}.json"
    file_path = os.path.join("employees", dynamic_filename)
    assert os.path.exists(file_path)
    os.remove(file_path)
    time.sleep(3)

def test_scanner_with_cookies(scanner_with_valid_credentials):
    scanner = scanner_with_valid_credentials
    scanner.start(scanner.mail, scanner.password, scanner.secret)

    json_files = [f for f in os.listdir("employees") if f.endswith(".json")]

    assert len(json_files) > 0

    for json_file in json_files:
        json_file_path = os.path.join("employees", json_file)
        os.remove(json_file_path)

    time.sleep(3)

def test_scanner_invalid_password(scanner_with_valid_credentials):
    scanner = scanner_with_valid_credentials
    cleanup_cookies(scanner)
    scanner.password = "invalid"

    with pytest.raises(Exception) as exc:
        scanner.start(scanner.mail, scanner.password, scanner.secret)

    assert str(exc.value) == "Invalid Password!"

# def test_scanner_invalid_secret(scanner_with_valid_credentials):
#     scanner = scanner_with_valid_credentials
#     # Remove cookies if they exist
#     cookie_filename = f"{scanner.mail}_cookies.pkl"
#     cookie_path = os.path.join("cookies", cookie_filename)
#     if os.path.exists(cookie_path):
#         os.remove(cookie_path)
#
#     scanner.secret = "invalid"
#
#     with pytest.raises(Exception) as exc:
#         scanner.start(scanner.mail, scanner.password, scanner.secret)
#     assert str(exc.value) == "Invalid Security Answer!"


