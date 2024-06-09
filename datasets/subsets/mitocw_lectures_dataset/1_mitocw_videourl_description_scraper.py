# from MIT OpenCourseWare:
# 1. get all courses with video lectures from their search API (233 as of 2022-09-09)
# 2. go to their page (based on the slug), get course title and description
# 3. based on navigation links text and URL pattern matching, navigate recursively until we hit a page with a video
#    player
# 4. if left navigation menu has "Lecture Notes" entry, for each note get the PDF URL

# the hard part is the scraping, as frequently the structure of the course page is left to the professor and is thus
# not uniform for all courses

from common import *

import os
import json
import re

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from tqdm import tqdm

site_url = "https://ocw.mit.edu"
search_url = f"{site_url}/search/?f=Lecture%20Videos&s=-runs.best_start_date"

# gotten by monitoring the browser's Network inspection tool while searching courses
# api_url = "https://open.mit.edu/api/v0"
# api_search_url = f"{api_url}/search"
# api_request_body_file = "mitocw_api_search_courseswithvideolectures_requestbody.json"


def get_courses_with_videolectures(driver):
    # the API is not public and always returns HTTP 500
    # request_body = json.load(open(api_request_body_file, "r"))
    # res = requests.post(
    #     api_search_url,
    #     data=request_body,
    #     headers={
    #         'Accept': "application/json",
    #         'Content-Type': "application/json",
    #         # 'Origin': site_url,
    #         # 'Host': "open.mit.edu",
    #         # 'Referer': site_url,
    #         # 'Accept-Encoding': "gzip, deflate, br",
    #         # 'Connection': "keep-alive",
    #     },
    # )
    # return res.json()
    driver.get(search_url)
    expected_course_cards = int(driver.find_element(by=By.CSS_SELECTOR, value=".results-total-number").text)
    course_cards = []
    while len(course_cards) < expected_course_cards:
        # scroll to bottom of page to trigger load of other items
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        course_cards = driver.find_elements(by=By.CSS_SELECTOR, value="section > article")

    # avoid StaleElementReferenceException
    course_titles = [course_card.find_element(by=By.CSS_SELECTOR, value=".course-title").text
                     for course_card in course_cards]
    course_urls = [course_card.find_element(by=By.CSS_SELECTOR, value=".course-title a").get_attribute("href")
                   for course_card in course_cards]
    courses = []
    for course_card, course_title, course_url in tqdm(zip(course_cards, course_titles, course_urls),
                                                      desc="Scraping courses info",
                                                      total=len(course_cards)):
        driver.get(course_url)
        course_info_table = driver.find_elements(by=By.CSS_SELECTOR, value="#course-info-table td")
        courses.append({
            'title': course_title,
            'url': course_url,
            'description': driver.find_element(by=By.CSS_SELECTOR, value="#course-description").text,
            'professors': [prof.text
                           for prof in driver.find_elements(by=By.CSS_SELECTOR,
                                                            value="#course-info-table .course-info-instructor")
                           if prof.text],
            'departments': [dep.text
                            for dep in driver.find_elements(by=By.CSS_SELECTOR,
                                                            value="#course-info-table .course-info-department")
                            if dep.text],
            'categories': list(set(cat.text
                                   for cat in driver.find_elements(by=By.CSS_SELECTOR,
                                                                   value="#course-info-table .course-info-topic")
                                   if cat.text)),
            # check if the previous td is "Course Number:"
            'codes': [li.text
                      for i, td in enumerate(course_info_table[1:])
                      if "course number" in course_info_table[i].text.lower()
                      for li in td.find_elements(by=By.CSS_SELECTOR, value="li")
                      if li.text],
            'levels': [level.text
                       for level in driver.find_elements(by=By.CSS_SELECTOR,
                                                         value="#course-info-table .course-info-level")
                       if level.text],
        })
    return courses


def _scrape_content_from_web_elements(main_content, video_player, get_title=True, get_description=True):
    result = {}
    if get_title:
        try:
            title = main_content.find_element(by=By.CSS_SELECTOR, value="#course-title").text
        except NoSuchElementException:
            title = None
        result['title'] = title
    if get_description:
        try:
            description = main_content.find_element(by=By.CSS_SELECTOR, value=".description").text
        except NoSuchElementException:
            description = None
        result['description'] = description
    try:
        video_url = video_player.find_element(by=By.CSS_SELECTOR, value=".video-js").get_attribute("data-downloadlink")
        if not video_url.startswith("http"):
            video_url = f"{site_url}/{video_url}".replace("//", "/")
    except NoSuchElementException:
        video_url = None
    result['video_url'] = video_url
    transcript_urls = [el.get_attribute("src")
                       for el in video_player.find_elements(by=By.CSS_SELECTOR, value="track")
                       if el.get_attribute("srclang") == "en"]
    transcript_url = transcript_urls[0] if transcript_urls else None
    result['transcript_url'] = transcript_url
    return result


def _scrape_lectures_data_recursive(driver, lectures, link, course_link, current_depth, max_depth):
    """
    Build the course['lectures'] dict with all the data relative to a lecture, such as video URL, transcript URL,
    title, and description. We deliberately ignore the transcripts provided as PDFs, since they are not in WEBVTT format
    and do not contain timecodes.
    """
    # termination condition for recursion
    if current_depth == max_depth or site_url not in link:
        return []

    try:
        driver.get(link)
    except TimeoutException:
        return []
    try:
        main_content = driver.find_element(by=By.CSS_SELECTOR, value="#main-content")
    except NoSuchElementException:
        return []

    video_players = main_content.find_elements(by=By.CSS_SELECTOR, value=".video-container")
    if video_players:
        if len(video_players) == 1:
            video_player = video_players[0]
            new_lecture = _scrape_content_from_web_elements(main_content, video_player)
            lectures.append(new_lecture)
        else:
            # we have multiple video players i.e. lectures, we scrape the content in between for titles and descriptions
            course_content_section_children = main_content.find_elements(by=By.XPATH, value="./*")
            lecture_details = [{'title': "", 'description': ""} for _ in range(len(video_players))]
            i = 0
            for child in course_content_section_children:
                if i == len(video_players):
                    break
                if child == video_players[i]:
                    i += 1
                if child.tag_name in ("h1", "h2", "h3", "h4", "h5", "h6"):
                    lecture_details[i]['title'] += f" {child.text}"
                elif child.tag_name in ("p", "span"):
                    lecture_details[i]['description'] += f" {child.text}"

            for i, video_player in enumerate(video_players):
                scraped_urls = _scrape_content_from_web_elements(main_content, video_player,
                                                                 get_title=False, get_description=False)
                lectures.append({
                    'title': lecture_details[i]['title'],
                    'description': lecture_details[i]['description'],
                    'video_url': scraped_urls['video_url'],
                    'transcript_url': scraped_urls['transcript_url'],
                })
        return lectures

    else:
        links = [a.get_attribute("href")
                 for a in main_content.find_elements(by=By.CSS_SELECTOR, value="a")
                 if a.get_attribute("href") and
                    a.get_attribute("href").startswith(course_link) and not
                    "previous" in a.text.lower() and not
                    "next" in a.text.lower() and not
                    a.get_attribute("href").endswith(".html") and not
                    a.get_attribute("href").endswith(".pdf") and not
                    a.get_attribute("href").endswith(".xls") and not
                    a.get_attribute("href").endswith(".xlsx") and not
                    a.get_attribute("href").endswith(".doc") and not
                    a.get_attribute("href").endswith(".docx")]
        if links:
            for link in links:
                lectures.extend(
                    _scrape_lectures_data_recursive(driver, [], link, course_link, current_depth + 1, max_depth)
                )
            return lectures
        else:
            return []


def add_transcripts_and_video_urls(driver, courses):
    # some links do not contain the keyword "video", but are listed by week or class (e.g. Week 1: some stuff)
    # the second part of the regex matches titles like "1: some stuff"
    # the third part matches "1 Some stuff"
    roman_numerals_regex = r"(?=[MDCLXVI])M*(C[MD]|D?C{0,3})(X[CL]|L?X{0,3})(I[XV]|V?I{0,3})"
    nav_link_regex = re.compile(pattern=rf"((class|lecture|week|module|part|chapter|puzzle|unit|session|lesson) (\d+|{roman_numerals_regex})|(\d+|{roman_numerals_regex}:? ))",
                                flags=re.IGNORECASE)

    for course in tqdm(courses, desc="Scraping courses data"):
        if course.get('lectures') and not OVERWRITE:
            continue

        driver.get(course['url'])
        _navigation_links = [l.get_attribute("href")
                             for l in driver.find_elements(by=By.CSS_SELECTOR,
                                                           value=".desktop-nav #course-nav .course-nav-list-item a")
                             if "video_lecture" in l.get_attribute("href").lower() or
                                "video_galler" in l.get_attribute("href").lower() or
                                "video-lecture" in l.get_attribute("href").lower() or
                                "video-galler" in l.get_attribute("href").lower() or
                                "video" in l.text or
                                l.text.lower() == course['title'].lower() or
                                nav_link_regex.match(l.text)]
        # remove links contained in other links to avoid unnecessary recursion steps
        navigation_links = []
        for i, _ in enumerate(_navigation_links):
            for j, _ in enumerate(_navigation_links):
                if i != j and \
                    (_navigation_links[i] in _navigation_links[j] and
                     len(_navigation_links[i]) < len(_navigation_links[j])):
                    break
            else:
                navigation_links.append(_navigation_links[i])

        course['lectures'] = []
        for nav_link in navigation_links:
            course['lectures'].extend(
                _scrape_lectures_data_recursive(
                    driver=driver,
                    lectures=[],
                    link=nav_link,
                    course_link=course['url'],
                    current_depth=0,
                    max_depth=3,
                )
            )
        update_dataset_file(courses)

    for course in tqdm(courses, desc="Removing duplicate lectures"):
        lectures = []
        for i, lecture in enumerate(course['lectures']):
            # lookbehind (from 0 to i - 1) instead of lookahead to preserve lecture order
            for other in (course['lectures'][i - 1::-1] if i > 0 else []):
                if lecture == other:
                    break
            else:
                lectures.append(lecture)
        course['lectures'] = lectures

    return courses


def main():
    driver = get_webdriver()

    if not os.path.isfile(dataset_file) or OVERWRITE:
        courses = get_courses_with_videolectures(driver)
        update_dataset_file(courses)
    else:
        courses = json.load(open(dataset_file, "r"))

    courses = add_transcripts_and_video_urls(driver, courses)
    update_dataset_file(courses)

    driver.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nQuitting...")
        exit()
