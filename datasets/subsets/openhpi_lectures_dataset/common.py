import sys
import os
import string

from selenium import webdriver
from selenium.webdriver.common.by import By

GET_CURRENT_LIST_OF_COURSES = True
OVERWRITE = False

prefix = "./data"
slides_dir = f"{prefix}/slides"
slide_images_dir = f"{prefix}/slide_images"
audios_dir = f"{prefix}/audios"
videos_dir = f"{prefix}/videos"
transcripts_dir = f"{prefix}/transcripts"

courses_file_name = f"{prefix.replace('/data', '')}/openhpi_api_courses.json"
courses_self_file_name = f"{prefix.replace('/data', '')}/openhpi_api_courses_self.json"
course_download_urls_file = f"{prefix.replace('/data', '')}/openhpi_courses_download_urls.json"
dataset_file = f"{prefix.replace('/data', '')}/openhpi_lectures_dataset.json"

base_url = "https://open.hpi.de"
api_base_url = f"{base_url}/api/v2"

email = "YOUR EMAIL"
password = "YOUR PASSWORD"


def sanitize_lecture_name(name: str) -> str:
    """given the title for a lecture, return a sanitized version that is filesystem friendly"""
    result = ""
    for character in name:
        if character in string.ascii_letters or character in string.digits:
            result += character
        elif character == "&":
            result += "and"
        elif character in "()[]{}":
            result += "+"
        else:
            result += "-"
    return result


def get_webdriver():
    # https://github.com/mozilla/geckodriver/issues/2010
    if sys.platform.startswith("linux"):
        tmpdir = "./.tmpdir_for_geckodriver_because_firefox_is_installed_with_snap"
        os.makedirs(tmpdir, exist_ok=True)
        os.environ['TMPDIR'] = tmpdir
    driver = webdriver.Firefox()
    driver.implicitly_wait(2)  # seconds
    return driver


def log_into_openhpi(driver):
    """log into the OpenHPI account"""
    driver.get("https://open.hpi.de/sessions/new")
    email_field = driver.find_element(by=By.CSS_SELECTOR, value="#login_email")
    email_field.send_keys(email)
    password_field = driver.find_element(by=By.CSS_SELECTOR, value="#login_password")
    password_field.send_keys(password)
    login_button = driver.find_element(by=By.CSS_SELECTOR, value="#login")
    login_button.click()
