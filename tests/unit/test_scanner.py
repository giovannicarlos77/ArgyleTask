import pytest
from unittest.mock import Mock, patch
from scanner.scanner import Scanner

@pytest.fixture
def mock_scanner_dependencies(mocker):
    return (
        mocker.patch('scanner.scanner.DriverUtils'),
        mocker.patch('scanner.scanner.BeautifulSoup'),
        mocker.patch('scanner.scanner.Utils'),
        mocker.patch('scanner.scanner.time.sleep'),
        mocker.patch('scanner.scanner.Utils.format_data')
    )

def mock_search_element(driver, by, locator):
    #Just to not enter in condition to save cookies again
    if locator == '//*[@id="sensitiveZone_password"]':
        return False
    else:
        return True

def test_extract_data(mock_scanner_dependencies):
    mock_driver_utils, mock_beautiful_soup, mock_utils, mock_sleep, mock_format_data = mock_scanner_dependencies

    scanner = Scanner("https://www.random_website.com")
    scanner.driver = Mock()

    mock_utils.get_user_id.return_value = "12345"
    mock_utils.get_full_name.return_value = ("John Doe", "John", "Doe")
    mock_utils.get_email.return_value = "john@example.com"
    mock_utils.get_phone.return_value = "123-456-7890"
    mock_utils.get_address.return_value = {"city": "New York", "state": "NY"}
    mock_utils.get_job_info.return_value = ("Software Engineer", "$70")

    mock_formatted_data = Mock()
    mock_formatted_data.model_dump_json.return_value = "some_json_data"
    mock_format_data.return_value = mock_formatted_data

    mock_driver_utils.search_element.side_effect = mock_search_element
    scanner._extract_data()
    assert mock_sleep.call_count == 3
    assert mock_beautiful_soup.call_count == 2

    mock_formatted_data.model_dump_json.assert_called_once_with(indent=4)

def test_invalid_username_exception(mocker):
    scanner = Scanner("https://www.upwork.com/ab/account-security/login")

    scanner.driver = mocker.MagicMock()

    scanner.driver.get.side_effect = Exception("Invalid Username!")

    with pytest.raises(Exception) as username_error:
        scanner._submit_credentials()
    assert str(username_error.value) == "Invalid Username!"

def test_invalid_password_exception(mocker):
    scanner = Scanner("https://www.upwork.com/ab/account-security/login")

    scanner.driver = mocker.MagicMock()

    scanner.driver.get.side_effect = Exception("Invalid Password!")

    with pytest.raises(Exception) as username_error:
        scanner._submit_credentials()
    assert str(username_error.value) == "Invalid Password!"

def test_invalid_secret_exception(mocker):
    scanner = Scanner("https://www.upwork.com/ab/account-security/login")

    scanner.driver = mocker.MagicMock()

    scanner.driver.get.side_effect = Exception("Invalid Secret!")

    with pytest.raises(Exception) as username_error:
        scanner._submit_credentials()
    assert str(username_error.value) == "Invalid Secret!"


