from common import *

import requests
import os
import json

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from tqdm import tqdm


def scrape_videolectures(driver, course_overview_url):
    """
    For a given overview URL of a course, it returns a dictionary containing the downloadable material URLs available
    for each lecture, including the transcript.
    """
    course_slug = course_overview_url.split('/')[-2]
    driver.get(course_overview_url)

    # enroll in the course to access all the videolectures (some are only available after enrollment) and the downloads
    try:
        enroll_banner = driver.find_element(by=By.CSS_SELECTOR, value=".callout")
        # https://open.hpi.de/enrollments?course_id=sustainablesoftware2022
        driver.get(f"{base_url}/enrollments?course_id={course_slug}")
        driver.get(course_overview_url)
    except NoSuchElementException:  # already enrolled
        pass

    full_overview = driver.find_element(by=By.CSS_SELECTOR, value=".course-area-main")
    videolecture_urls = [
        el.get_attribute("href")
        for el in full_overview.find_elements(by=By.CSS_SELECTOR, value="a.course-overview-item.video")
    ]

    result = {}
    for url in videolecture_urls:
        driver.get(url)
        try:
            lecture_title = driver.find_element(by=By.CSS_SELECTOR, value=".item-title").text
        except NoSuchElementException:
            lecture_title = None
        try:
            download_urls = [el.get_attribute("href") for el in
                             driver.find_elements(by=By.CSS_SELECTOR, value="table > tbody > tr > td.text-right a")]
        except NoSuchElementException:
            download_urls = None
        try:
            # make sure to get the English transcript and not the German one
            transcript_urls = [
                el.get_attribute('src')
                for el in driver.find_elements(by=By.CSS_SELECTOR, value="xm-text-track")
                if el.get_attribute('language') == "en"
            ]
            transcript_url = f"{base_url}{transcript_urls[0]}" if len(transcript_urls) > 0 else None
        except NoSuchElementException:
            transcript_url = None
        result[lecture_title] = {
            'lecture': url,  # to get the slide images in the downloader
            'material': download_urls,
            'transcript': transcript_url,
        }

    return result


def main():
    if not os.path.isfile(courses_file_name) or GET_CURRENT_LIST_OF_COURSES:
        courses = requests.get(f"{api_base_url}/courses").json()['data']
        with open(courses_file_name, "w") as f:
            json.dump(courses, f)
    else:
        courses = json.load(open(courses_file_name, "r"))

    courses_accessible = [c for c in courses
                          if c['attributes']['accessible'] and
                          c['attributes']['enrollable'] and
                          c['attributes']['status'] == "self-paced" and
                          not c['attributes']['hidden'] and
                          not c['attributes']['external']]
    courses_english = [c for c in courses_accessible if c['attributes']['language'] == "en"]

    # this only contains the teaser stream urls more than courses_english
    # if not os.path.isfile(courses_self_file_name):
    #     courses_english_self = {
    #         c['id']: requests.get(f"{api_base_url}/{c['links']['self'].replace('/api/v2', '')}").json()
    #         for c in courses_english
    #     }
    #     with open(courses_self_file_name, "w") as f:
    #         json.dump(courses_english_self, f)
    # else:
    #     courses_english_self = json.load(open(courses_self_file_name, "r"))

    courses_english_overview_urls = {
        c['attributes']['slug']: f"{base_url}/courses/{c['attributes']['slug']}/overview"
        for c in courses_english
    }

    print(f"All courses: {len(courses)}, "
          f"of which accessible: {len(courses_accessible)}, "
          f"of which in English: {len(courses_english)}")

    driver = get_webdriver()
    log_into_openhpi(driver)

    courses_download_urls = json.load(open(course_download_urls_file, "r")) if os.path.isfile(course_download_urls_file) else {}
    for i, (course_slug, course_overview_url) in enumerate(tqdm(courses_english_overview_urls.items(), desc=f"Scraping URLs of downloadable material to {course_download_urls_file}")):
        # if i < 35:  # useful to continue at a later time
        #     continue
        if not courses_download_urls.get(course_slug) or \
                (courses_download_urls.get(course_slug) and "null" in courses_download_urls[course_slug]) or \
                OVERWRITE:
            courses_download_urls[course_slug] = scrape_videolectures(driver, course_overview_url)
            # save after each course
            with open(course_download_urls_file, "w") as f:
                json.dump(courses_download_urls, f, indent=4, ensure_ascii=False)

    driver.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nQuitting...")
        exit()
