import json
import string
import sys
import os

from selenium import webdriver

OVERWRITE = False

dataset_file = "mitocw_lectures_dataset.json"
clean_dataset_file = "mitocw_lectures_dataset_clean.json"
transcripts_only_dataset_file = "mitocw_lectures_dataset_transcripts_only.json"
data_dir = "./data"
videos_dir = f"{data_dir}/videos"
transcripts_dir = f"{data_dir}/transcripts"


def update_dataset_file(contents, clean=False, transcripts_only=False):
    if clean:
        output_file = clean_dataset_file
    elif transcripts_only:
        output_file = transcripts_only_dataset_file
    else:
        output_file = dataset_file
    with open(output_file, "w") as f:
        json.dump(contents, f, indent=4, ensure_ascii=False)


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


def avg(lst):
    return sum(lst) / len(lst) if len(lst) > 0 else 0
