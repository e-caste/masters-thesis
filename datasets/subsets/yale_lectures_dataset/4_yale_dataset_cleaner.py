# we'll clean the Yale dataset of courses that:
# 1. have less than 5 lectures
# 2. don't have all lectures with a video, description, and transcript
# 3. have all lectures with the same description
# 4. have all lectures with a description at least 2 sentences long (too restricting)
#    --> with an average description at least 1.5 sentences long
# 5. have all lectures with a description at least 10 words long (too restricting)
#    --> with an average description at least 10 words long
# 6. TODO have a transcript length to description length in words ratio lower than some threshold

from common import *

import os
import json
import importlib
import re

from tqdm import tqdm
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
nltk.download("punkt")
# Python doesn't allow easy import from files starting with a number
# to make the following line work, we also need to have an __init__.py file to signal we are in a package
run_dataset_analysis = importlib.import_module("3_yale_dataset_analysis").main

# TODO: some trancripts contain pieces similar to closed captions such as (music), (chiming music), (gentle music),
#  (students clapping), [Student], [Reporter], [inaudible] and "quote".
#  Do these interfere with language models or are they helpful?
# TODO: sometimes sentences start with the speaker (e.g. Professor Holloway: sentence or Prof: sentence).
#  Is this helpful or harmful?
url_regex = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", re.IGNORECASE)
class_readings_regex = re.compile(r"Class Readings:? ?", re.IGNORECASE)
timecodes_regex = re.compile(r"\(?(?:\d{1,2}[:.])?\d{1,2}[:.]\d{1,2}\)?")
course_materials_regex = re.compile(r"Complete course materials are available (?:at the .*Yale .*site)?", re.IGNORECASE)
course_website_regex = re.compile(r"Courses website:?", re.IGNORECASE)
course_recorded_regex = re.compile(r"This course was recorded in (?:Spring|Summer|Fall|Winter) \d{4}", re.IGNORECASE)
warning_regex = re.compile(r"Warning:? ?", re.IGNORECASE)
# these titles are contained in descriptions but are not exactly the title of the YouTube playlist and need to be
# handled specifically
course_titles_regex = re.compile(r"(?:The Early Middle Ages, 284--1000 \(HIST 210\)|"
                                 r"Foundations of Modern Social Thought \(SOCY 151\)|"
                                 r"Moral Foundations of Politics \(PLSC 118\)|"
                                 r"Fundamentals of Physics, II \(PHYS 201\)|"
                                 r"European Civilization, 1648-1945 \(HIST 202\)|"
                                 r"Principles of Evolution, Ecology and Behavior \(EEB 122\)|"
                                 r"Financial Markets \(ECON 252\))", re.IGNORECASE)
shankar_book_regex = re.compile(r"For more information about Professor Shankar's book", re.IGNORECASE)

webvtt_ignore_lines_regex = re.compile(r"(?:WEBVTT|Kind: captions|Language: en)", re.IGNORECASE)
webvtt_timecode_regex = re.compile(r"\d{2}:\d{2}:\d{2}\.\d{3}")


def _remove_urls(sent):
    urls = url_regex.findall(sent)
    for url in urls:
        sent = sent.replace(url, "")
    return sent


def _remove_substring_iter(sent, substring, replacement=None):
    while substring in sent:
        sent = sent.replace(substring, replacement if replacement else "")
    return sent


def clean_text(text, remove_newlines=False):
    for seq, replacement in zip(
            [2 * " ", 2 * "-", "\n" if remove_newlines else 2 * "\n", "\r\n" if remove_newlines else 2 * "\r\n"],
            [" ", "-", " " if remove_newlines else "\n", " " if remove_newlines else "\r\n"]
    ):
        text = _remove_substring_iter(text, seq, replacement)
    return text.strip()


def filter_courses(courses):
    return [
        c for c in courses
        if len(c['lectures']) >= 5
        and all(l['video_url'] for l in c['lectures'])
        and all(l['description'] for l in c['lectures'])
        and all(os.path.isfile(f"""{transcripts_dir}/{sanitize_lecture_name(f"{c['title']}-{l['title']}")}.en.vtt""") for l in c['lectures'])
        and not all(l['description'] == other['description'] for i, l in enumerate(c['lectures']) for other in c['lectures'][i + 1:])
        and avg([len(sent_tokenize(l['description'])) for l in c['lectures']]) >= 1.5
        and avg([len(word_tokenize(l['description'])) for l in c['lectures']]) >= 10
        # and all(len(sent_tokenize(l['description'])) >= 2 for l in c['lectures'])
        # and all(len(word_tokenize(l['description'])) >= 10 for l in c['lectures'])
    ]


def add_transcript(courses):
    for course in tqdm(courses, desc="Adding transcript to lectures"):
        for lecture in course['lectures']:
            transcript_file_name = f"""{transcripts_dir}/{sanitize_lecture_name(f"{course['title']}-{lecture['title']}")}.en.vtt"""
            if not os.path.isfile(transcript_file_name):
                continue
            with open(transcript_file_name, "r") as f:
                transcript = f.read()
            for line in transcript.split("\n"):
                if webvtt_ignore_lines_regex.match(line) or webvtt_timecode_regex.match(line):
                    transcript = transcript.replace(f"{line}\n", "")
            transcript_text = " ".join([line.strip() for line in transcript.split("\n")])
            transcript_text = clean_text(transcript_text, remove_newlines=True)
            description_length_words = len(word_tokenize(lecture['description']))
            transcript_length_words = len(word_tokenize(transcript_text))
            description_length_sentences = len(sent_tokenize(lecture['description']))
            transcript_length_sentences = len(sent_tokenize(transcript_text))
            lecture['description_to_transcript_length_in_words_ratio'] = description_length_words / transcript_length_words
            lecture['description_to_transcript_length_in_sentences_ratio'] = description_length_sentences / transcript_length_sentences
            # clean transcript
            # first case: < and > used as parentheses (e.g. <<laughter>>)
            # second case: < and > used mathematically
            lecture['transcript'] = transcript_text \
                .replace("�", "") \
                .replace("&lt;&lt;", "(").replace("&gt;&gt;", ")") \
                .replace("&lt;", "<").replace("&gt;", ">")
    return courses


def main(transcripts_only: bool = False):
    courses = json.load(open(dataset_file, "r"))
    clean_courses = courses if transcripts_only else filter_courses(courses)

    # this code is for debugging at which point a course gets filtered out
    # in conclusion, 7 courses are excluded because at least one transcription does not exist for one of their lectures
    # for c in [c for c in courses
    #           if c['title'].startswith("Capital Punishment")
    #           or c['title'].startswith("Atmosphere, Ocean")
    #           or c['title'].startswith("Freshman Organic")
    #           or c['title'].startswith("New Testament")
    #           or c['title'].startswith("France Since")]:
    #     print(f"{c['title']}: "
    #           # f"{len(c['lectures'])} lectures, "  # >= 5
    #           # f"all videos: {all(l['video_url'] for l in c['lectures'])}, "  # True
    #           # f"all descriptions: {all(l['description'] for l in c['lectures'])}, "  # True
    #           f"all transcripts: {any(os.path.isfile(transcripts_dir + '/' + sanitize_lecture_name(c['title'] + '-' + l['title']) + '.en.vtt') for l in c['lectures'])}, "
    #           f"all descriptions are equal: {all(l['description'] == other['description'] for i, l in enumerate(c['lectures']) for other in c['lectures'][i + 1:])}, "
    #           f"average description length in sentences: {avg([len(sent_tokenize(l['description'])) for l in c['lectures']])}, "
    #           f"average description length in words: {avg([len(word_tokenize(l['description'])) for l in c['lectures']])}")
    # exit()

    for course in clean_courses:
        for lecture in course['lectures']:
            # clean description
            tmp = "\n".join([
                _remove_urls(s).strip()
                for s in lecture['description']
                .replace(u"\xa0", " ")  # remove Non-Breaking Space
                .split("\n")
                if s
                and "ISBN" not in s
                and not re.match(rf"{lecture['title'].split('(')[0] if '(' in lecture['title'] else lecture['title']}", s, re.IGNORECASE)
                and not re.match(rf"{course['title'].lower().split('with')[0] if 'with' in course['title'] else course['title'].lower().split('w/')[0]}".strip(), s, re.IGNORECASE)
                and not class_readings_regex.match(s)
                and not timecodes_regex.match(s)
                and not course_materials_regex.search(s)
                and not course_website_regex.match(s)
                and not course_recorded_regex.search(s)
                and not warning_regex.match(s)
                and not course_titles_regex.match(s)
                and not shankar_book_regex.match(s)
            ])
            tmp = clean_text(tmp, remove_newlines=True)
            if course['title'] == "Timothy Snyder: The Making of Modern Ukraine":
                tmp = tmp.replace("Course reading list:", "")\
                    .replace("To see other videos in this course, please click on this playlist link:", "")\
                    .replace("For issues with closed captions, please email guy.ortoleva@yale.edu", "")\
                    .strip()
            lecture['description'] = tmp

    if not transcripts_only:
        clean_courses = filter_courses(clean_courses)

    clean_courses = add_transcript(clean_courses)

    if transcripts_only:
        for course in clean_courses:
            del course['description']
            # keep only lectures with a transcript
            course['lectures'] = [l for l in course['lectures'] if "transcript" in l and len(l['transcript']) > 0]
            # remove data that is not needed for the transcripts only version
            for lecture in course['lectures']:
                for key in (
                        "description",
                        "duration_in_seconds",
                        "description_to_transcript_length_in_words_ratio",
                        "description_to_transcript_length_in_sentences_ratio",
                ):
                    if key in lecture:
                        del lecture[key]
    update_dataset_file(clean_courses, clean=not transcripts_only, transcripts_only=transcripts_only)

    print(f"Total courses in {dataset_file}: {len(courses)}. Filtered courses in {clean_dataset_file}: {len(clean_courses)}.")
    print(f"Total lectures: {sum(len(c['lectures']) for c in clean_courses)}.")
    print(f"Excluded courses: {' | '.join([c['title'] for c in courses if c['title'] not in [c['title'] for c in clean_courses]])}.")
    if not transcripts_only:
        print(f"Running analysis of the clean dataset ({clean_dataset_file})...")
        run_dataset_analysis(clean=True, ratios=True)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nQuitting...")
        exit()
