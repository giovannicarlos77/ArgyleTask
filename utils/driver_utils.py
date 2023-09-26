import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
class DriverUtils:
    def __init__(self):
        pass

    @staticmethod
    def wait_and_click(driver, by, locator, timeout):
        element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, locator)))
        element.click()

    @staticmethod
    def search_element(driver, by, locator):
        try:
            driver.find_element(by, locator)
        except NoSuchElementException:
            return False
        return True

    @staticmethod
    def refresh_driver(driver, timer: int):
        time.sleep(timer)
        driver.refresh()

    @staticmethod
    def get_local_storage(driver, key):
        return driver.execute_script("return window.localStorage.getItem(arguments[0]);", key)