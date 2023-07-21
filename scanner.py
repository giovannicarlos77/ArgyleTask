import time
import json
import datetime
import chromedriver_autoinstaller
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from model.Employee import Employee, Address, BasePay, Period
from pathlib import Path
from selenium.webdriver.chrome.service import Service as ChromeService

chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists


# and if it doesn't exist, download it automatically,
# then add chromedriver to path

def checkInvalidUsername(html: str):
    soup = BeautifulSoup(html, 'html.parser')
    answer = bool(soup.findAll(string="Oops! Username is incorrect."))
    if answer:
        # print(json.dumps({'status': 'ERROR', 'responseText': 'Invalid username!'}))
        raise Exception("Invalid Username!")
    else:
        return


def checkInvalidCredentials(html: str):
    soup = BeautifulSoup(html, 'html.parser')
    answer = (bool(soup.findAll(string="Oops! Password is incorrect.")))
    if answer:
        # print(json.dumps({'status': 'ERROR', 'responseText': 'Invalid password!'}))
        raise Exception("Invalid Credentials!")
    else:
        return


def checkInvalidSecurityAnswer(html: str):
    soup = BeautifulSoup(html, 'html.parser')
    answer = (bool(soup.findAll(string="Oops! Answer is incorrect.")) or bool(
        soup.findAll(string="Help is on the way!")))
    if answer:
        # print(json.dumps({'status': 'ERROR', 'responseText': 'Invalid Security Answer!'}))
        raise Exception("Invalid Security Answer!")
    else:
        return


def saveData(employee: Employee):
    filePath = Path("./employees/" + employee.full_name + ".json")
    filePath.touch(exist_ok=True)
    file = open(filePath, "w")
    file.write(employee.model_dump_json(indent=4))
    print(employee.model_dump_json(indent=4))


def formatString(string: str):
    return " ".join(string.replace("\n", "").split())


def formatData(userid: str, firstname: str, lastname: str, fullname: str, email: str,
               jobtitle: str, phone: str, basepay: BasePay, **address):
    employee = Employee(account=userid,
                        first_name=firstname,
                        last_name=lastname,
                        email=email,
                        full_name=fullname,
                        job_title=jobtitle,
                        base_pay=basepay,
                        phone_number=phone,
                        address=Address.model_validate(address),
                        created_at=str(datetime.datetime.now()),
                        update_at=str(datetime.datetime.now()))
    saveData(employee)


class Scanner:
    def __init__(self, login_url: str):
        self.options = webdriver.ChromeOptions()
        self.prefs = {'profile.default_content_setting_values': {'images': 2}}
        self.options.add_experimental_option("prefs", self.prefs)  # disable loading pictures
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
        self.LOGIN_URL = login_url
        self.PROFILE_URL = "https://www.upwork.com/freelancers/settings/contactInfo"
        self.mail = ""
        self.password = ""
        self.secret = ""
        self.driver = None
        self.retried = False

    def waitClick(self, type: str, path: str, timer: int):
        WebDriverWait(self.driver, timer).until(EC.element_to_be_clickable((type, path)))

    def waitVisible(self, type: str, path: str, timer: int):
        WebDriverWait(self.driver, timer).until(EC.visibility_of_element_located((type, path)))

    def searchElement(self, type: str, path: str):
        try:
            self.driver.find_element(type, path)
        except NoSuchElementException:
            return False
        return True

    def instantiateDriver(self, driver: webdriver):
        self.driver = driver(options=self.options)

    def start(self, mail: str, password: str, secret: str):
        self.mail = mail
        self.password = password
        self.secret = secret
        self.instantiateDriver(webdriver.Chrome)
        self.submitCredentials()

    def submitCredentials(self):
        try:
            self.driver.get(self.LOGIN_URL)
            self.waitClick(By.XPATH, '//*[@id="login_username"]', 10)
            self.driver.find_element(By.XPATH, '//*[@id="login_username"]').send_keys(self.mail)
            self.waitClick(By.XPATH, '//*[@id="login_password_continue"]', 5)
            self.driver.find_element(By.XPATH, '//*[@id="login_password_continue"]').click()
            time.sleep(2)
            checkInvalidUsername(self.driver.page_source)
            self.waitClick(By.XPATH, '//*[@id="login_password"]', 5)
            self.driver.find_element(By.XPATH, '//*[@id="login_password"]').send_keys(self.password)
            self.waitClick(By.XPATH, '//*[@id="login_control_continue"]', 10)
            self.driver.find_element(By.XPATH, '//*[@id="login_control_continue"]').click()
            time.sleep(2)
            checkInvalidCredentials(self.driver.page_source)
            time.sleep(2)
            if self.searchElement(By.XPATH, '//*[@id="login_answer"]'):
                self.waitClick(By.XPATH, '//*[@id="login_answer"]', 10)
                self.driver.find_element(By.XPATH, '//*[@id="login_answer"]').send_keys(self.secret)
                time.sleep(1)
                self.waitClick(By.XPATH, '//*[@id="login_control_continue"]', 5)
                self.driver.find_element(By.XPATH, '//*[@id="login_control_continue"]').click()
                time.sleep(2)
                checkInvalidSecurityAnswer(self.driver.page_source)
                time.sleep(1)
                self.extractData()
            else:
                time.sleep(1)
                return self.extractData()
        # Timeout Exception
        except TimeoutException:
            if not self.retried:
                self.retried = True
                self.reopenDriver(5)
                self.submitCredentials()
            else:
                raise
        # When not found a element Exception
        except NoSuchElementException:
            if not self.retried:
                self.retried = True
                self.reopenDriver(5)
                self.submitCredentials()
            else:
                raise
        # Commons exceptions in Webdriver, like ERR_INTERNET_DISCONNECTED
        # Timer its bigger because maybe its a network issue
        except WebDriverException:
            if not self.retried:
                self.retried = True
                self.reopenDriver(10)
                self.submitCredentials()
            else:
                raise
        # General Exceptions
        except Exception:
            raise

    def extractData(self):
        # To get email without **, if cannot get the data with the asterisk
        metaData = self.getLocalStorage('auth-store-data')
        self.driver.get(self.PROFILE_URL)
        time.sleep(2)
        if self.searchElement(By.XPATH, '//*[@id="deviceAuth_answer"]'):
            self.driver.find_element(By.XPATH, '//*[@id="deviceAuth_answer"]').send_keys(self.secret)
            self.waitClick(By.XPATH, '//*[@id="control_save"]', 5)
            self.driver.find_element(By.XPATH, '//*[@id="control_save"]').click()

        time.sleep(5)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        try:
            # Some parameters have a particular treatment, upwork website put extra spaces in some fields
            userId = formatString(soup.find('div', {'data-test': 'userId'}).get_text()) if soup.find('div', {
                'data-test': 'userId'}) is not None else ""
            fullName = formatString(soup.find('div', {'data-test': 'userName'}).get_text()) if soup.find('div', {
                'data-test': 'userName'}) is not None else ""
            firstName = fullName.split(" ")[0]
            lastName = fullName.split(" ")[1]
            if metaData is not None:
                jsonMetaData = json.loads(metaData)
                email = jsonMetaData["auth/user/setLoginName"]
            else:
                email = formatString(soup.find('div', {'data-test': 'userEmail'}).get_text()) if soup.find('div', {
                    'data-test': 'userEmail'}) is not None else ""
            phone = formatString(soup.find('div', {'data-test': 'phone'}).get_text()) if soup.find('div', {
                'data-test': 'phone'}) is not None else ""

            addressDict = ""
            addressObject = soup.find('div', {'data-test': 'address'})
            if addressObject is not None:
                street = addressObject.find('span', {'data-test': 'addressStreet'}).get_text() if soup.find('span', {
                    'data-test': 'addressStreet'}) is not None else ""
                street2 = addressObject.find('span', {'data-test': 'addressStreet2'}).get_text() if soup.find('span', {
                    'data-test': 'addressStreet2'}) is not None else ""
                city = addressObject.find('span', {'data-test': 'addressCity'}).get_text() if soup.find('span', {
                    'data-test': 'addressCity'}) is not None else ""
                state = addressObject.find('span', {'data-test': 'addressState'}).get_text() if soup.find('span', {
                    'data-test': 'addressState'}) is not None else ""
                zipCode = addressObject.find('span', {'data-test': 'addressZip'}).get_text() if soup.find('span', {
                    'data-test': 'addressZip'}) is not None else ""
                country = addressObject.find('span', {'data-test': 'addressCountry'}).get_text() if soup.find('span', {
                    'data-test': 'addressCountry'}) is not None else ""
                addressDict = {'street1': street, 'street2': street2, 'city': city, 'state': state, 'zipCode': zipCode,
                               'country': country}

            self.waitClick(By.XPATH, '//*[@id="main"]/div[2]/div[4]/div[1]/div/nav/div/div[2]/ul/li[5]/a/span', 2)
            self.driver.find_element(By.XPATH,
                                     '//*[@id="main"]/div[2]/div[4]/div[1]/div/nav/div/div[2]/ul/li[5]/a/span').click()
            time.sleep(3)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            divJob = soup.find('div', {'class': 'row d-flex'})
            jobTitle = divJob.find('h2').get_text().strip() if divJob is not None else ""
            salary = divJob.find("h3").get_text().strip() if divJob is not None else ""
            basePay = BasePay(amount=salary, currency="$", period=Period("hourly"))
            formatData(userId, firstName, lastName, fullName, email, jobTitle, phone, basePay, **addressDict)
        # Since we stay inside profile page, not need restart all the flow, just refresh and retry
        # to not lose session and waste more time.
        # Timeout Exception
        except TimeoutException:
            if not self.retried:
                self.retried = True
                self.refreshDriver(5)
                self.extractData()
            else:
                raise
        # When not found a element Exception
        except NoSuchElementException:
            if not self.retried:
                self.retried = True
                self.refreshDriver(5)
                self.extractData()
            else:
                raise
        # Commons exceptions in Webdriver, like ERR_INTERNET_DISCONNECTED
        # Timer its bigger because maybe its a network issue
        except WebDriverException:
            if not self.retried:
                self.retried = True
                self.reopenDriver(10)
                self.extractData()
            else:
                raise
        except Exception:
            raise

    def reopenDriver(self, timer: int):
        self.driver.close()
        time.sleep(timer)
        self.driver = webdriver.Chrome(options=self.options)

    def refreshDriver(self, timer: int):
        time.sleep(timer)
        self.driver.refresh()

    def getLocalStorage(self, key):
        return self.driver.execute_script("return window.localStorage.getItem(arguments[0]);", key)
