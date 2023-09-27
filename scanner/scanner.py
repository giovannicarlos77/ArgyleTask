import time
import pickle
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from model.Employee import Employee, Address, BasePay, Period
from pathlib import Path
from get_chrome_driver import GetChromeDriver
from utils.driver_utils import DriverUtils
from utils.utils import Utils

def save_data_and_print(employee: Employee):
    Utils.save_data(employee)
    print(employee.model_dump_json(indent=4))


def save_cookies(cookies, mail):
    with open(f'cookies/{mail}_cookies.pkl', 'wb') as cookie_file:
        pickle.dump(cookies, cookie_file)


def load_cookies(mail):
    if Path(f'cookies/{mail}_cookies.pkl').is_file():
        with open(f'cookies/{mail}_cookies.pkl', 'rb') as cookie_file:
            return pickle.load(cookie_file)
    return None

def set_cookies(driver, cookies):
    try:
        driver.delete_all_cookies()
        for cookie in cookies:
            driver.add_cookie(cookie)
    except Exception as e:
        print(f"Failed to set cookies: {e}")
class Scanner:
    def __init__(self, login_url: str):
        self.options = webdriver.ChromeOptions()
        self.prefs = {'profile.default_content_setting_values': {'images': 2}}
        self._configure_chrome_options()
        self.LOGIN_URL = login_url
        self.PROFILE_URL = "https://www.upwork.com/freelancers/settings/contactInfo"
        self.mail = ""
        self.password = ""
        self.secret = ""
        self.driver = None
        self.retried = False

    def _configure_chrome_options(self):
        # Configure ChromeOptions as needed
        self.options.add_argument("--disable-blink-features")
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation", "disable-infobars"])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_experimental_option('prefs', self.prefs)
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--headless")
        self.options.add_argument("window-size=1920,1080")
        self.options.add_argument('--no-first-run')
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--disable-client-side-phishing-detection')
        self.options.add_argument('--allow-running-insecure-content')
        self.options.add_argument('--disable-web-security')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        # Remove warnings or some logging
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])

    def _initialize_driver(self):
        self.driver = webdriver.Chrome(options=self.options)

    def _reopen_driver(self, timer: int):
        self.driver.close()
        time.sleep(timer)
        self._initialize_driver()

    def _retry_on_exceptions(self, func, max_attempts=3, sleep_time=5):
        attempts = 0
        while attempts < max_attempts:
            try:
                return func()
            except (NoSuchElementException, TimeoutException, WebDriverException) as e:
                print(f"Caught exception: {e}")
                print(f"Retrying... (Attempt {attempts + 1}/{max_attempts})")
                self._reopen_driver(sleep_time)
                attempts += 1
        raise Exception(f"Max retry attempts ({max_attempts}) reached.")

    def _submit_credentials(self):
        def _submit():
            try:
                self.driver.get(self.LOGIN_URL)
                cookies = load_cookies(self.mail)
                if cookies:
                    set_cookies(self.driver, cookies)
                    self._extract_data()
                else:
                    self._login()
            except Exception:
                raise

        self._retry_on_exceptions(_submit)

    def _login(self):
        try:
            self.driver.find_element(By.XPATH, '//*[@id="login_username"]').send_keys(self.mail)
            DriverUtils.wait_and_click(self.driver, By.XPATH, '//*[@id="login_password_continue"]', 5)
            time.sleep(2)

            if Utils.check_text(self.driver, "Oops! Username is incorrect."):
                raise Exception("Invalid Username!")

            DriverUtils.wait_and_click(self.driver, By.XPATH, '//*[@id="login_password"]', 5)
            self.driver.find_element(By.XPATH, '//*[@id="login_password"]').send_keys(self.password)
            DriverUtils.wait_and_click(self.driver, By.XPATH, '//*[@id="login_control_continue"]', 10)
            time.sleep(2)

            if Utils.check_text(self.driver, "Oops! Password is incorrect."):
                raise Exception("Invalid Password!")

            self._handle_security_question()
            self._extract_data()
        except Exception:
            raise

    def _handle_security_question(self):
        if DriverUtils.search_element(self.driver, By.XPATH, '//*[@id="login_answer"]'):
            DriverUtils.wait_and_click(self.driver, By.XPATH, '//*[@id="login_answer"]', 10)
            self.driver.find_element(By.XPATH, '//*[@id="login_answer"]').send_keys(self.secret)
            DriverUtils.wait_and_click(self.driver, By.XPATH, '//*[@id="login_control_continue"]', 5)
            time.sleep(3)

            if (Utils.check_text(self.driver, "Oops! Answer is incorrect.") or
                    Utils.check_text(self.driver, "Help is on the way!") or
                    Utils.check_text(self.driver, "Incorrect answer.")):
                raise Exception("Invalid Security Answer!")
            elif Utils.check_text(self.driver, "You've reached the maximum number of tries."):
                raise Exception("Security answer maximum attempts!")

    def _save_cookies(self):
        cookies = self.driver.get_cookies()
        save_cookies(cookies, self.mail)
        time.sleep(1)

    def _extract_data(self):
        time.sleep(2)
        meta_data = DriverUtils.get_local_storage(self.driver, 'auth-store-data')
        self.driver.get(self.PROFILE_URL)
        time.sleep(1)

        self._handle_device_auth()
        self._save_cookies()
        user_id, full_name, first_name, last_name, email, phone, address_dict = self._get_user_info(meta_data)
        time.sleep(1)
        base_pay, job_title = self._get_job_info()

        employee = Utils.format_data(user_id, first_name, last_name, full_name, email, job_title, phone, base_pay, **address_dict)
        save_data_and_print(employee)
        return employee

    def _handle_device_auth(self):
        if DriverUtils.search_element(self.driver, By.XPATH, '//*[@id="deviceAuth_answer"]'):
            DriverUtils.wait_and_click(self.driver, By.XPATH, '//*[@id="deviceAuth_answer"]', 10)
            self.driver.find_element(By.XPATH, '//*[@id="deviceAuth_answer"]').send_keys(self.secret)
            DriverUtils.wait_and_click(self.driver, By.XPATH, '//*[@id="control_save"]', 5)
            time.sleep(3)
            if (Utils.check_text(self.driver, "Oops! Answer is incorrect.") or
                Utils.check_text(self.driver, "Help is on the way!") or
                Utils.check_text(self.driver, "Incorrect answer.")):
                    raise Exception("Invalid Security Answer!")
            elif Utils.check_text(self.driver, "You've reached the maximum number of tries."):
                    raise Exception("Security answer maximum attempts!")

    def _get_job_info(self):
        # Navigate to MyProfile tab and create a new soup object because driver_page_source content was changed
        DriverUtils.wait_and_click(self.driver, By.XPATH, '//*[@id="main"]/div[2]/div[4]/div[1]/div/nav/div/div[2]/ul/li[5]/a/span', 5)
        time.sleep(3)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        job_title, salary = Utils.get_job_info(soup)
        base_pay = BasePay(amount=salary, currency="$", period=Period("hourly"))
        return base_pay, job_title

    def _get_user_info(self, meta_data):
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        user_id = Utils.get_user_id(soup)
        full_name, first_name, last_name = Utils.get_full_name(soup)
        email = Utils.get_email(soup, meta_data)
        phone = Utils.get_phone(soup)
        address_dict = Utils.get_address(soup)
        return user_id, full_name, first_name, last_name, email, phone, address_dict

    def start(self, mail: str, password: str, secret: str):
        self.mail = mail
        self.password = password
        self.secret = secret
        self._initialize_driver()
        self._submit_credentials()


# Install the driver:
# Downloads ChromeDriver for the installed Chrome version on the machine
# Adds the downloaded ChromeDriver to path
get_driver = GetChromeDriver()
get_driver.install()
