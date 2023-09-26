import time
import json
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from model.Employee import BasePay, Period, Employee, Address
from pathlib import Path
import datetime

class Utils:
    def __init__(self):
        pass

    @staticmethod
    def check_text(driver: WebDriver, text: str):
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        answer = bool(soup.findAll(string=text))
        return answer

    @staticmethod
    def get_user_id(soup):
        user_id_element = soup.find('div', {'data-test': 'userId'})
        return Utils.format_string(user_id_element.get_text()) if user_id_element is not None else ""

    @staticmethod
    def get_full_name(soup):
        user_name_element = soup.find('div', {'data-test': 'userName'})
        full_name = Utils.format_string(user_name_element.get_text()) if user_name_element is not None else ""
        first_name, last_name = full_name.split(" ") if " " in full_name else (full_name, "")
        return full_name, first_name, last_name

    @staticmethod
    def get_email(soup, meta_data):
        if meta_data is not None:
            json_meta_data = json.loads(meta_data)
            email = json_meta_data["auth/user/setLoginName"]
        else:
            email_element = soup.find('div', {'data-test': 'userEmail'})
            email = Utils.format_string(email_element.get_text()) if email_element is not None else ""
        return email

    @staticmethod
    def get_phone(soup):
        phone_element = soup.find('div', {'data-test': 'phone'})
        return Utils.format_string(phone_element.get_text()) if phone_element is not None else ""

    @staticmethod
    def get_address(soup):
        address_dict = {}
        address_object = soup.find('div', {'data-test': 'address'})
        if address_object is not None:
            address_dict = {
                'street1': Utils.format_string(address_object.find('span', {'data-test': 'addressStreet'}).get_text()),
                'street2': Utils.format_string(address_object.find('span', {'data-test': 'addressStreet2'}).get_text()),
                'city': Utils.format_string(address_object.find('span', {'data-test': 'addressCity'}).get_text()),
                'state': Utils.format_string(address_object.find('span', {'data-test': 'addressState'}).get_text()),
                'zipCode': Utils.format_string(address_object.find('span', {'data-test': 'addressZip'}).get_text()),
                'country': Utils.format_string(address_object.find('span', {'data-test': 'addressCountry'}).get_text())
            }
        return address_dict

    @staticmethod
    def get_job_info(soup):
        job_div = soup.find('div', {'class': 'row d-flex'})
        job_title = job_div.find('h2').get_text().strip() if job_div is not None else ""
        salary = job_div.find("h3").get_text().strip() if job_div is not None else ""
        return job_title, salary

    @staticmethod
    def format_string(string: str):
        return " ".join(string.replace("\n", "").split())

    @staticmethod
    def save_data(employee: Employee):
        if "*" not in employee.email:
            file_path = Path("./employees/" + employee.email + ".json")
        else:
            file_path = Path("./employees/" + employee.full_name.strip() + ".json")
        file_path.touch(exist_ok=True)
        with open(file_path, "w") as file:
            file.write(employee.model_dump_json(indent=4))
            print(employee.model_dump_json(indent=4))
    @staticmethod
    def format_data(userid: str, firstname: str, lastname: str, fullname: str, email: str,
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
        return employee
