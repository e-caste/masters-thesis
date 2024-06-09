# interesting facts about the dataset:
# 1. total courses
# 2. total lectures
# 3. average+min+max/plot lectures per course
# 4. lectures with transcript
# 5. courses where all lectures have a transcript
# 6. lectures with description
# 7. courses where all lectures have a description
# 8. lectures with transcript+description
# 9. courses where all lectures have transcript+description
# 10. average/plot sentences in a description for all lectures, description sentences / transcript sentences %
# 11. average/plot words in a description for all lectures, description words / transcript words %
# 12. average/plot sentences in a description for lectures of a course, description sentences / transcript sentences %
# 13. average/plot words in a description for lectures of a course, description words / transcript words %
# 14. average+min+max/plot duration of a video lecture for all courses
# 15. average+min+max/plot duration of a video lecture for each course
# 16. average+min+max/plot description length to transcript length in words ratio
# 17. average+min+max/plot description length to transcript length in sentences ratio

from common import *

import os
import json
import requests

from matplotlib import pyplot as plt
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
nltk.download("punkt")


def plot_barh(data, xlabel, ylabel, title=None, decimals=2):
    fig, ax = plt.subplots(figsize=(16, 9))
    plt.barh(list(data.keys()), list(data.values()))
    if title:
        plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    ax.xaxis.set_tick_params(pad=5)
    ax.yaxis.set_tick_params(pad=10)
    ax.xaxis.set_ticks_position('none')
    ax.yaxis.set_ticks_position('none')
    ax.grid(b=True, color='grey', linestyle='-.', linewidth=0.5, alpha=0.2)
    for i in ax.patches:
        plt.text(
            i.get_width() + 0.2,
            i.get_y(),
            str(round((i.get_width()), decimals)),
            fontsize=10,
            fontweight='bold',
            color='grey'
        )
    plt.tight_layout()
    plt.show()


def main(clean=False, ratios=False):
    courses = json.load(open(clean_dataset_file if clean else dataset_file, "r"))

    # 1.
    total_courses = len(courses)
    print(f"Total courses: {total_courses}.")
    # 2.
    total_lectures = sum(len(c['lectures']) for c in courses)
    print(f"Total lectures: {total_lectures}.")
    # 3.
    minimum_lectures_in_a_course = min(len(c['lectures']) for c in courses)
    maximum_lectures_in_a_course = max(len(c['lectures']) for c in courses)
    print(f"Minimum/average/maximum number of lectures per course: "
          f"{minimum_lectures_in_a_course}/{total_lectures / total_courses:.2f}/{maximum_lectures_in_a_course}.")
    data = {c['title']: len(c['lectures']) for c in sorted(courses, key=lambda c: len(c['lectures']))}
    plot_barh(data, xlabel="Lectures per course", ylabel="Courses", title=None)
    # 4.
    lectures_with_transcript = len([
        l
        for c in courses
        for l in c['lectures']
        if os.path.isfile(f"""{transcripts_dir}/{sanitize_lecture_name(f"{c['title']}-{l['title']}")}.en.vtt""")
    ])
    print(f"Total lectures with transcript: {lectures_with_transcript} "
          f"({lectures_with_transcript / total_lectures * 100:.2f}%).")
    # 5.
    courses_with_transcript = len([
        c
        for c in courses
        if all(os.path.isfile(f"""{transcripts_dir}/{sanitize_lecture_name(f"{c['title']}-{l['title']}")}.en.vtt""")
               for l in c['lectures'])
    ])
    print(f"Total courses with transcript: {courses_with_transcript} "
          f"({courses_with_transcript / total_courses * 100:.2f}%).")
    # 6.
    lectures_with_description = len([
        l
        for c in courses
        for l in c['lectures']
        if l['description']
    ])
    print(f"Total lectures with description: {lectures_with_description} "
          f"({lectures_with_description / total_lectures * 100:.2f}%).")
    # 7.
    courses_with_description = len([
        c
        for c in courses
        if all(l['description']
               for l in c['lectures'])
    ])
    print(f"Total courses with description: {courses_with_description} "
          f"({courses_with_description / total_courses * 100:.2f}%).")
    # 8.
    lectures_with_transcript_and_description = len([
        l
        for c in courses
        for l in c['lectures']
        if os.path.isfile(f"""{transcripts_dir}/{sanitize_lecture_name(f"{c['title']}-{l['title']}")}.en.vtt""") and
           l['description']
    ])
    print(f"Total lectures with transcript and description: {lectures_with_transcript_and_description} "
          f"({lectures_with_transcript_and_description / total_lectures * 100:.2f}%).")
    # 9.
    courses_with_transcript_and_description = len([
        c
        for c in courses
        if all(os.path.isfile(f"""{transcripts_dir}/{sanitize_lecture_name(f"{c['title']}-{l['title']}")}.en.vtt""") and
               l['description']
               for l in c['lectures'])
    ])
    print(f"Total courses with transcript and description: {courses_with_transcript_and_description} "
          f"({courses_with_transcript_and_description / total_courses * 100:.2f}%).")
    # 10.
    lectures_sentences_in_description = [
        len(sent_tokenize(l['description']))
        for c in courses
        for l in c['lectures']
        if l['description']
    ]
    print(f"Minimum/average/maximum number of sentences in a lecture description: "
          f"{min(lectures_sentences_in_description)}/"
          f"{sum(lectures_sentences_in_description) / len(lectures_sentences_in_description):.2f}/"
          f"{max(lectures_sentences_in_description)}.")
    data = {
        c['title']: sum(len(sent_tokenize(l['description'])) for l in c['lectures']) / len(c['lectures'])
        for c in sorted(courses, key=lambda c: sum(len(sent_tokenize(l['description']))
                                                   for l in c['lectures']) / len(c['lectures']))
    }
    plot_barh(data, xlabel="Average description length in sentences per course", ylabel="Courses")
    # 11.
    lectures_words_in_description = [
        len(word_tokenize(l['description']))
        for c in courses
        for l in c['lectures']
        if l['description']
    ]
    print(f"Minimum/average/maximum number of words in a lecture description: "
          f"{min(lectures_words_in_description)}/"
          f"{sum(lectures_words_in_description) / len(lectures_words_in_description):.2f}/"
          f"{max(lectures_words_in_description)}.")
    data = {
        c['title']: sum(len(word_tokenize(l['description'])) for l in c['lectures']) / len(c['lectures'])
        for c in
        sorted(courses, key=lambda c: sum(len(word_tokenize(l['description']))
                                          for l in c['lectures']) / len(c['lectures']))
    }
    plot_barh(data, xlabel="Average description length in words per course", ylabel="Courses")
    # 14.

    def _get_duration_variable(duration_string, delimiter):
        var = 0
        if delimiter in duration_string:
            for i, char in enumerate(duration_string):
                if char == delimiter:
                    for j, other in enumerate(duration_string[i + 1:]):
                        if not other.isdigit():
                            tmp = duration_string[i + 1:i + j + 1]
                            var = int(tmp[::-1])
                            break
                    break
        return var

    def _add_video_duration_in_seconds(details):
        # e.g. "PT1H7M19S": https://developers.google.com/youtube/v3/docs/videos?hl=en#contentDetails.duration
        # quota 1
        duration = requests.get(
            f"{yt_videos_api_url}?part=contentDetails&"
            f"id={l['video_url'].replace('https://www.youtube.com/watch?v=', '')}&"
            f"maxResults=1&key={yt_api_key}"
        ).json()['items'][0]['contentDetails']['duration']
        duration = duration[::-1]
        days = _get_duration_variable(duration, "D")
        hours = _get_duration_variable(duration, "H")
        minutes = _get_duration_variable(duration, "M")
        seconds = _get_duration_variable(duration, "S")
        courses[details['course_index']]['lectures'][details['lecture_index']]['duration_in_seconds'] = days * 86400 + hours * 3600 + minutes * 60 + seconds

    if not all('duration_in_seconds' in l
               for c in courses
               for l in c['lectures']
               if l['video_url']) or \
            OVERWRITE:
        for i, c in enumerate(courses):
            for j, l in enumerate(c['lectures']):
                if l['video_url']:
                    _add_video_duration_in_seconds({
                        'course_index': i,
                        'lecture_index': j,
                        'video_url': l['video_url'],
                    })
        update_dataset_file(courses)

    video_lectures_durations_in_seconds = [
        l['duration_in_seconds']
        for c in courses
        for l in c['lectures']
    ]

    print(f"Minimum/average/maximum duration of all video lectures: {min(video_lectures_durations_in_seconds)}/"
          f"{sum(video_lectures_durations_in_seconds) / len(video_lectures_durations_in_seconds):.2f}/"
          f"{max(video_lectures_durations_in_seconds)} seconds.")

    data = {
        c['title']: sum(l['duration_in_seconds'] for l in c['lectures']) / len(c['lectures'])
        for c in sorted(courses, key=lambda c: sum(l['duration_in_seconds'] for l in c['lectures']) / len(c['lectures']))
    }
    plot_barh(data, xlabel="Average lecture duration in seconds per course", ylabel="Courses")

    if ratios:
        # 16.
        data = {c['title']: avg([l['description_to_transcript_length_in_words_ratio'] for l in c['lectures']])
                for c in sorted(courses,
                                key=lambda c: avg([l['description_to_transcript_length_in_words_ratio'] for l in c['lectures']]))}
        plot_barh(data, xlabel="Average description length to transcript length in words", ylabel="Courses", decimals=5)

        # 17.
        data = {c['title']: avg([l['description_to_transcript_length_in_sentences_ratio'] for l in c['lectures']])
                for c in sorted(courses,
                                key=lambda c: avg([l['description_to_transcript_length_in_sentences_ratio'] for l in c['lectures']]))}
        plot_barh(data, xlabel="Average description length to transcript length in sentences", ylabel="Courses", decimals=5)


"""
Total courses: 44.
Total lectures: 1143.
Minimum/average/maximum number of lectures per course: 20/25.98/40.
Total lectures with transcript: 1096 (95.89%).
Total courses with transcript: 37 (84.09%).
Total lectures with description: 1143 (100.00%).
Total courses with description: 44 (100.00%).
Total lectures with transcript and description: 1096 (95.89%).
Total courses with transcript and description: 37 (84.09%).
Minimum/average/maximum number of sentences in a lecture description: 1/11.00/22.
Minimum/average/maximum number of words in a lecture description: 26/211.32/435.
Minimum/average/maximum duration of all video lectures: 735/3178.99/5902 seconds.
"""
"""Running 4_yale_dataset_cleaner.py:
Total courses in yale_lectures_dataset.json: 44. Filtered courses in yale_lectures_dataset_clean.json: 36.
Total lectures: 895.
Excluded courses: Capital Punishment: Race, Poverty, & Disadvantage with Stephen Bright | Atmosphere, Ocean and Environmental Change with Ron Smith | Financial Markets (2011) with Robert Shiller | Freshman Organic Chemistry II with Michael McBride | New Testament History and Literature with Dale B. Martin | Freshman Organic Chemistry with J. Michael McBride | Milton with John Rogers | France Since 1871 with John Merriman.
Running analysis of the clean dataset (yale_lectures_dataset_clean.json)...
Total courses: 36.
Total lectures: 895.
Minimum/average/maximum number of lectures per course: 20/24.86/36.
Total lectures with transcript: 895 (100.00%).
Total courses with transcript: 36 (100.00%).
Total lectures with description: 895 (100.00%).
Total courses with description: 36 (100.00%).
Total lectures with transcript and description: 895 (100.00%).
Total courses with transcript and description: 36 (100.00%).
Minimum/average/maximum number of sentences in a lecture description: 1/5.05/19.
Minimum/average/maximum number of words in a lecture description: 13/125.83/313.
Minimum/average/maximum duration of all video lectures: 1123/3278.67/5902 seconds.
"""


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nQuitting...")
        exit()
