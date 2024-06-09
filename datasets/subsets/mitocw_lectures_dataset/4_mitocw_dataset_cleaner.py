# since the MIT OpenCourseWare dataset is a bit dirty, we'll clean it of courses that:
# 1. have less than 5 lectures
# 2. don't have all lectures with a video, description, and transcript
# 3. have all lectures with the same description
# 4. have all lectures with a description at least 2 sentences long (too restrictive)
#    --> with an average description at least 1.5 sentences long
# 5. have all lectures with a description at least 10 words long (too restrictive)
#    --> with an average description at least 10 words long
# 6. TODO have a transcript length to description length in words ratio lower than some threshold

# some courses have the same description for pairs of lectures, with at the end "Part one|two of two."
# TODO: split the description manually

from common import *

import json
import importlib
import re

from tqdm import tqdm
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
nltk.download("punkt")
# Python doesn't allow easy import from files starting with a number
# to make the following line work, we also need to have an __init__.py file to signal we are in a package
run_dataset_analysis = importlib.import_module("3_mitocw_dataset_analysis").main

# some lectures start with the professor name (e.g. CASEY RODRIGUEZ: ... or PROFESSOR: ...), also AUDIENCE: ... and [INAUDIBLE].
# this means: either three or two groups of 1 or 2 digits separated by :, with optional parentheses
duration_regex = re.compile(r"\(?(?:\d{1,2}:)?\d{1,2}:\d{1,2}\)?")
# this means: any character followed by a size in bytes symbol between parentheses or square brackets (shortest group)
# https://stackoverflow.com/a/28652616
file_sizes_regex = re.compile(r"(?:\(|\[)(?:(?!\(|\[).)*?(?:TB|GB|MB|KB|B)(?:\)|\])", re.IGNORECASE)
# matches Description: | description\n etc. at the beginning of the line
section_title_regex = re.compile(r"^(?:video |track )?(?:descriptions?|summary|summaries)(?::? ?)", re.IGNORECASE)
# matches any line starting with the name of the speaker/instructor
speaker_instructor_regex = re.compile(r"^(?:instructors?|instructors?/speakers?|speakers?/instructors?|speakers?): ", re.IGNORECASE)
handouts_regex = re.compile(r"(?:see handout \d+|there is no handout)", re.IGNORECASE)
note_related_regex = re.compile(r"(?:Note: To report potential content errors, please use this form|"
                                r"Note: The slides used in this lecture can be found at the Lecture Slides tab|"
                                r"Note: There is no video|"
                                r"Note: Lecture \d+ was an exam session|"
                                r"Note: This video lecture was recorded|"
                                r"Note: Lecture \d+ was a lab session|"
                                r"Note: No video is available for Lecture \d+|"
                                r"video is.*cut off)", re.IGNORECASE)
related_matlab_code_regex = re.compile(r"related matlab code files.*downloaded.*", re.IGNORECASE)
video_player_available_regex = re.compile(r"a video player with synced slides and lecture notes is available", re.IGNORECASE)
ith_of_n_lectures_regex = re.compile(r"this is the .* of .* lectures on .*", re.IGNORECASE)
video_index_tab_regex = re.compile(r"^See the Video Index tab", re.IGNORECASE)
gilbert_lectures_book_regex = re.compile(r"These video lectures of Professor Gilbert Strang teaching 18.06 were "
                                         r"recorded in Fall 1999 and do not correspond precisely to the current "
                                         r"edition of the textbook", re.IGNORECASE)
slides_used_regex = re.compile(r"(?:Slides Used in this Video:|lecture \d+:.*slides|Related sections? in textbook:)", re.IGNORECASE)
see_also_lecture_regex = re.compile(r"See also Lecture \d+", re.IGNORECASE)
covid19_regex = re.compile(r".*COVID-?19.*", re.IGNORECASE)
weird_html_regex = re.compile(r"p.p1 \{margin: 0.0px 0.0px 0.0px 0.0px; font: 8.0px Verdana\} span.s1 "
                              r"\{font-kerning: none} span.s2 \{font: 11.0px Verdana; font-kerning: none\}", re.IGNORECASE)
viewing_recommendation_regex = re.compile(r"(?:^viewing recommendation$|If you are using a laptop or desktop computer)", re.IGNORECASE)
class_version_regex = re.compile(r"This video is from (?:the )?(?:Spring|Summer|Fall|Winter|IAP) \d{4}", re.IGNORECASE)
url_regex = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", re.IGNORECASE)

webvtt_ignore_lines_regex = re.compile(r"(?:WEBVTT|"
                                       r"Kind: captions|"
                                       r"Language: en|"
                                       r"\[SQUEAKING\]|"
                                       r"\[RUSTLING\]|"
                                       r"\[CLICKING\]|"
                                       r"\[CLICK\])", re.IGNORECASE)
webvtt_timecode_regex = re.compile(r"\d{2}:\d{2}:\d{2}\.\d{3}")
mit_disclaimer_regex = re.compile(r"(?:NARRATOR: )?"
                                  r"The following content is provided under a Creative Commons license\. "
                                  r"(?:Your|B) support will help MIT Open ?Course[Ww]are continue to offer "
                                  r"high[ -]quality,? (?:quality )?educational resources for free\. To make a "
                                  r"donation,? or (?:to )?view additional materials from (?:hundreds|100(?:'s|s)?) of "
                                  r"MIT courses, visit (?:MIT|mit) ?[Oo]pen ?[Cc]ourse[Ww]are(?: at |@)(?:NCAA )?"
                                  r"(?:[Oo][Ccs][Ww]|fsae)[.@](?:MIT|mit)\.edu\.?",
                                  re.IGNORECASE)

timecode_align_regex = re.compile(r"\d{2}:\d{2}:\d{2}\.\d{3} -> \d{2}:\d{2}:\d{2}\.\d{3} align:middle line:90%")
funding_regex = re.compile(r"Funding for the publication of this video was provided by (?:the )?Gabriell[ae] and Paul "
                           r"Rosenbaum [Ff]oundation\. Help OCW continue to provide free and open access to MIT courses"
                           r" by making a donation at (?:MIT )?ocw\.mit\.edu/donate\.", re.IGNORECASE)

# course categories to avoid -- e.g. Language because we want to focus on English-only transcripts
discarded_categories = ["Language"]


def _remove_file_info_section_title_and_urls(sent):
    """Removes durations like (01:10:23), file sizes like (PDF - 2.8MB), section titles like Description:, and URLs."""
    durations = duration_regex.findall(sent)
    for duration in durations:
        sent = sent.replace(duration, "")
    file_sizes = file_sizes_regex.findall(sent)
    for file_size in file_sizes:
        sent = sent.replace(file_size, "")
    section_titles = section_title_regex.findall(sent)
    for section_title in section_titles:
        sent = sent.replace(section_title, "")
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
    return re.sub(mit_disclaimer_regex, "", text).strip()


def filter_courses(courses):
    filtered_courses = [
        c for c in courses
        if not any(cat in discarded_categories for cat in c['categories'])
        and len(c['lectures']) >= 5
        and all(l['video_url'] for l in c['lectures'])
        and all(l['description'] for l in c['lectures'])
        and all(os.path.isfile(f"""{transcripts_dir}/{sanitize_lecture_name(f"{c['title']}-{l['title']}")}.vtt""") for l in c['lectures'])
        and not all(l['description'] == other['description'] for i, l in enumerate(c['lectures']) for other in c['lectures'][i + 1:])
        and avg([len(sent_tokenize(l['description'])) for l in c['lectures']]) >= 1.5
        and avg([len(word_tokenize(l['description'])) for l in c['lectures']]) >= 10
        # and all(len(sent_tokenize(l['description'])) >= 2 for l in c['lectures'])
        # and all(len(word_tokenize(l['description'])) >= 10 for l in c['lectures'])
    ]
    # remove duplicate courses such as "A 2020 Vision of Linear Algebra" and "Discrete Stochastic Processes"
    course_titles_to_add = set(c['title'] for c in filtered_courses)
    res = []
    for course in filtered_courses:
        if course['title'] in course_titles_to_add:
            res.append(course)
            course_titles_to_add.remove(course['title'])
    return res


def add_transcript(courses, transcripts_only):
    for course in tqdm(courses, desc="Adding transcript to lectures"):
        for lecture in course['lectures']:
            transcript_file_name = f"""{transcripts_dir}/{sanitize_lecture_name(f"{course['title']}-{lecture['title']}")}.vtt"""
            if not os.path.isfile(transcript_file_name):
                continue
            with open(transcript_file_name, "r") as f:
                transcript = f.read()
            for i, line in enumerate(transcript.split("\n")):
                if webvtt_ignore_lines_regex.match(line) or webvtt_timecode_regex.match(line):
                    transcript = transcript.replace(f"{line}\n", "")
            transcript_text = " ".join([line.strip() for line in transcript.split("\n")])
            transcript_text = clean_text(transcript_text, remove_newlines=True)
            if not transcripts_only:
                description_length_words = len(word_tokenize(lecture['description']))
                transcript_length_words = len(word_tokenize(transcript_text))
                description_length_sentences = len(sent_tokenize(lecture['description']))
                transcript_length_sentences = len(sent_tokenize(transcript_text))
                lecture['description_to_transcript_length_in_words_ratio'] = description_length_words / transcript_length_words
                lecture['description_to_transcript_length_in_sentences_ratio'] = description_length_sentences / transcript_length_sentences
            # clean transcript
            for regex in (mit_disclaimer_regex, funding_regex, timecode_align_regex):
                matches = re.findall(regex, transcript_text)
                for match in matches:
                    transcript_text = re.sub(match, "", transcript_text)
            lecture['transcript'] = transcript_text.strip()
    return courses


def main(transcripts_only: bool = False):
    courses = json.load(open(dataset_file, "r"))
    clean_courses = courses if transcripts_only else filter_courses(courses)

    if not transcripts_only:
        for course in clean_courses:
            for lecture in course['lectures']:
                tmp = "\n".join([
                    _remove_file_info_section_title_and_urls(s)
                    for s in lecture['description'].split("\n")
                    if s not in ("Description", "Description: ", "Summary", "Summary: ")
                    and "ISBN" not in s
                    and not speaker_instructor_regex.match(s)
                    and not handouts_regex.search(s)
                    and not note_related_regex.search(s)
                    and not related_matlab_code_regex.search(s)
                    and not video_player_available_regex.search(s)
                    and not ith_of_n_lectures_regex.search(s)
                    and not video_index_tab_regex.search(s)
                    and not gilbert_lectures_book_regex.search(s)
                    and not slides_used_regex.search(s)
                    and not see_also_lecture_regex.search(s)
                    and not covid19_regex.search(s)
                    and not weird_html_regex.search(s)
                    and not viewing_recommendation_regex.search(s)
                    and not class_version_regex.search(s)
                ])
                tmp = clean_text(tmp, remove_newlines=True)
                lecture['description'] = tmp

        clean_courses = filter_courses(clean_courses)

    clean_courses = add_transcript(clean_courses, transcripts_only=transcripts_only)

    if transcripts_only:
        # keep only lectures with a transcript
        for course in clean_courses:
            course['lectures'] = [l for l in course['lectures'] if "transcript" in l and len(l['transcript']) > 0]
        # keep only courses with at least one transcript
        clean_courses = [c for c in clean_courses if len(c['lectures']) > 0]

        # remove duplicate courses
        different_titles = set(c['title'] for c in clean_courses)
        tmp = clean_courses
        clean_courses = []
        for course in tmp:
            if course['title'] in different_titles:
                clean_courses.append(course)
                different_titles.remove(course['title'])

        # remove duplicate lectures
        for course in clean_courses:
            lectures = course['lectures']
            different_titles = set(l['title'] for l in lectures)
            course['lectures'] = []
            for lecture in lectures:
                if lecture['title'] in different_titles:
                    course['lectures'].append(lecture)
                    different_titles.remove(lecture['title'])

        # remove data that is not needed for the transcripts only version
        for course in clean_courses:
            for key in (
                    "description",
                    "professors",
                    "departments",
                    "categories",
                    "codes",
                    "levels",
            ):
                if key in course:
                    del course[key]
            for lecture in course['lectures']:
                for key in (
                        "description",
                        "duration_in_seconds",
                        "description_to_transcript_length_in_words_ratio",
                        "description_to_transcript_length_in_sentences_ratio",
                        "video_url",
                        "transcript_url",
                ):
                    if key in lecture:
                        del lecture[key]
    update_dataset_file(clean_courses, clean=not transcripts_only, transcripts_only=transcripts_only)

    print(f"Total courses in {dataset_file}: {len(courses)}. Filtered courses in {clean_dataset_file}: {len(clean_courses)}.")
    print(f"Total lectures: {sum(len(c['lectures']) for c in clean_courses)}.")
    if not transcripts_only:
        print(f"Running analysis of the clean dataset ({clean_dataset_file})...")
        run_dataset_analysis(clean=True, ratios=True)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nQuitting...")
        exit()
