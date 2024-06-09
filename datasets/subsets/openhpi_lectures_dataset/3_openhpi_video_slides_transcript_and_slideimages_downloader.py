# you may have to run this script a couple of times, since for various reasons the download of a few files may get
# interrupted -- but don't worry, just re-running the script is enough, as it checks for a local file of size equal to
# the one of the file to download (so partially downloaded files get automatically overwritten)

from common import *

import requests
import lox
from selenium.common.exceptions import NoSuchElementException

import json
import os
from sys import stderr

global cookies  # set as global so we can use this variable in download_file without constantly passing it
cookies = {}


def set_openhpi_authentication_cookies(driver):
    selenium_cookies = driver.get_cookies()
    for cookie in selenium_cookies:
        cookies[cookie['name']] = cookie['value']


def get_openhpi_login_cookies():
    """we do a miniscule amount of tomfoolery"""
    driver = get_webdriver()
    log_into_openhpi(driver)
    set_openhpi_authentication_cookies(driver)
    driver.close()


@lox.thread(os.cpu_count())
def download_file(details):
    file_name_no_ext = f"{details['dir']}/{details['name']}"
    file_name = f"{file_name_no_ext}.{details['extension']}"

    res = requests.get(details['url'], stream=True, cookies=cookies if details['needs_authentication_cookie'] else None)
    file_size = int(res.headers.get('Content-Length', 0))

    # download not existing files and re-download only partially downloaded files
    if not os.path.isfile(file_name) or \
            (os.path.isfile(file_name) and os.path.getsize(file_name) < file_size) or \
            OVERWRITE:
        with open(file_name, 'wb') as f:
            for data in res:
                f.write(data)

    return file_name


def main(
        download_transcripts=True,
        download_slides=False,
        download_audios=False,
        download_videos=False,
):
    if not any([download_transcripts, download_slides, download_audios, download_videos]):
        print("At least one download variable should be True.", file=stderr)
        exit(-1)

    try:
        with open(course_download_urls_file, "r") as f:
            courses_download_urls = json.load(f)
    except FileNotFoundError:
        print("Please run 1_openhpi_video_slides_and_transcript_urls_scraper.py first.", file=stderr)
        exit(-1)

    # create needed directories
    for dir_name in (prefix, slides_dir, slide_images_dir, audios_dir, videos_dir, transcripts_dir):
        os.makedirs(dir_name, exist_ok=True)

    urls = {
        'slides': [],
        'slide_images': [],
        'audios': [],
        'videos': [],
        'transcripts': [],
    }
    stats = {
        'total_download_urls': 0,
        'considered_download_urls': 0,
    }

    for course in courses_download_urls:
        for lecture in courses_download_urls[course]:
            lecture_url = courses_download_urls[course][lecture]['lecture']
            material_urls = courses_download_urls[course][lecture]['material']
            transcript_url = courses_download_urls[course][lecture]['transcript']
            stats['total_download_urls'] += (1 if lecture_url is not None else 0) + \
                                            (1 if transcript_url is not None else 0) + \
                                            len(material_urls)

            if lecture_url is not None:
                # urls['slide_images'].append({
                #     'url': lecture_url,
                #     'dir': slide_images_dir,
                #     'name': f"{course}_{sanitize_lecture_name(lecture)}_",  # where the image number will be appended
                #     'extension': "png",
                #     'needs_authentication_cookie': False,
                # })
                stats['considered_download_urls'] += 1
            if transcript_url is not None:
                urls['transcripts'].append({
                    'url': transcript_url,
                    'dir': transcripts_dir,
                    'name': f"{course}_{sanitize_lecture_name(lecture)}",
                    'extension': "txt",
                    'needs_authentication_cookie': False,
                })
                stats['considered_download_urls'] += 1

            for mat_url in material_urls:
                if mat_url.endswith(".pdf"):  # there are no PowerPoint slides on OpenHPI
                    urls['slides'].append({
                        'url': mat_url,
                        'dir': slides_dir,
                        'name': f"{course}_{sanitize_lecture_name(lecture)}",
                        'extension': "pdf",
                        'needs_authentication_cookie': False,
                    })
                    stats['considered_download_urls'] += 1
                elif mat_url.endswith("/hd"):
                    urls['videos'].append({
                        'url': mat_url,
                        'dir': videos_dir,
                        'name': f"{course}_{sanitize_lecture_name(lecture)}_hd",
                        'extension': "mp4",
                        'needs_authentication_cookie': True,
                    })
                    stats['considered_download_urls'] += 1
                elif mat_url.endswith("/sd"):
                    urls['videos'].append({
                        'url': mat_url,
                        'dir': videos_dir,
                        'name': f"{course}_{sanitize_lecture_name(lecture)}_sd",
                        'extension': "mp4",
                        'needs_authentication_cookie': True,
                    })
                    stats['considered_download_urls'] += 1
                elif mat_url.endswith(".mp3"):
                    urls['audios'].append({
                        'url': mat_url,
                        'dir': audios_dir,
                        'name': f"{course}_{sanitize_lecture_name(lecture)}",
                        'extension': "mp3",
                        'needs_authentication_cookie': False,
                    })
                    stats['considered_download_urls'] += 1

    # to re-scrape just one lecture (set OVERWRITE to True):
    # scrape_slide_images("sustainablesoftware2022_1-2-Course-Overview_hd.mp4")
    # exit()

    get_openhpi_login_cookies()

    if download_transcripts:
        for transcript in urls['transcripts']:
            download_file.scatter(transcript)
        print(f"Downloading transcripts to {transcripts_dir}...")
        results = download_file.gather(tqdm=True)

    if download_slides:
        for slides in urls['slides']:
            download_file.scatter(slides)
        print(f"Downloading slides to {slides_dir}...")
        results = download_file.gather(tqdm=True)

    if download_audios:
        for audio in urls['audios']:
            download_file.scatter(audio)
        print(f"Downloading audios to {audios_dir}...")
        results = download_file.gather(tqdm=True)

    if download_videos:
        for video in urls['videos']:
            if video['name'].endswith("hd"):
                download_file.scatter(video)
        print(f"Downloading videos to {videos_dir}...")
        results = download_file.gather(tqdm=True)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nQuitting...")
        exit()
