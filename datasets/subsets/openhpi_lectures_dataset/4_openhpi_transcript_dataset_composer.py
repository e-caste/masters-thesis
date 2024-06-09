from common import *

import os
import json
import re

from tqdm import tqdm


webvtt_ignore_lines_regex = re.compile(r"(?:WEBVTT|Kind: captions|Language: en|^\d+$)", re.MULTILINE)
webvtt_timecode_regex = re.compile(r"\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}")

newline = "\n"


def convert_webvtt_to_text(webvtt_text):
    # replace HTML to match timecode regex
    webvtt_text = webvtt_text.replace("&lt;", "<").replace("&gt;", ">")
    for regex in (webvtt_timecode_regex, webvtt_ignore_lines_regex):
        matches = re.finditer(regex, webvtt_text)
        for match in matches:
            # replace matched characters with newlines which will be removed at the following step
            # replace instead of remove so that the following match span indices are still valid
            start, end = match.span()
            webvtt_text = f"{webvtt_text[:start]}{newline * (end - start)}{webvtt_text[end:]}"
    transcript_text = " ".join([line.strip()
                                for line in webvtt_text.split("\n")
                                if line and not all(c == " " for c in line)])
    return transcript_text.strip()


def main():
    material_urls = json.load(open(course_download_urls_file, "r"))

    courses = []
    for course_title in tqdm(material_urls, desc="Getting course transcripts"):
        lectures = []
        for lecture_title in material_urls[course_title]:
            transcript_file_name = f"{transcripts_dir}/{course_title}_{sanitize_lecture_name(lecture_title)}.txt"
            if os.path.isfile(transcript_file_name):
                lecture = {
                    'title': lecture_title,
                    'url': material_urls[course_title][lecture_title]['lecture'],
                    'transcript': convert_webvtt_to_text(open(transcript_file_name, "r").read()),
                }
                lectures.append(lecture)

        course = {
            'title': course_title,
            'url': f"{base_url}/courses/{course_title}",
            'lectures': lectures,
        }
        courses.append(course)

    # remove duplicate courses (same year e.g. 2022 and 2021 with exact same transcripts)
    different_titles = set(c['title'][:-4] if c['title'][-4:].isdigit() else c['title'] for c in courses)
    tmp = courses
    courses = []
    for course in tmp:
        title = course['title'][:-4] if course['title'][-4:].isdigit() else course['title']
        if title in different_titles and len(course['lectures']) > 0:
            courses.append(course)
            different_titles.remove(title)

    lectures_with_transcript = sum(1 for c in courses for l in c['lectures'] if len(l['transcript']) > 0)
    print(f"Total lectures with a transcript: {lectures_with_transcript}.")

    with open(dataset_file, "w") as f:
        json.dump(courses, f, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nQuitting...")
        exit()
