# interesting facts about the dataset:
# 1. total courses
# 2. total lectures
# 3. average+min+max/plot lectures per course
# 4. lectures with transcript
# 5. courses where all lectures have a transcript
# 6. lectures with description
# 7. courses where all lectures have a description
# 8. lectures with video
# 9. courses where all lectures have a video
# 10. lectures with transcript+description+video
# 11. courses where all lectures have transcript+description+video
# 12. average/plot sentences in a description for all lectures, description sentences / transcript sentences %
# 13. average/plot words in a description for all lectures, description words / transcript words %
# 14. average/plot sentences in a description for lectures of a course, description sentences / transcript sentences %
# 15. average/plot words in a description for lectures of a course, description words / transcript words %
# 16. average+min+max/plot duration of a video lecture for all courses
# 17. average+min+max/plot duration of a video lecture for each course
# 18. average+min+max/plot description length to transcript length in words ratio
# 19. average+min+max/plot description length to transcript length in sentences ratio

from common import *

import os
import json

from matplotlib import pyplot as plt
import lox
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
nltk.download("punkt")

rwlock = lox.RWLock()


def plot_barh(data, xlabel, ylabel, title=None, decimals=2):
    fig, ax = plt.subplots(figsize=(32, 32))
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
    minimum_lectures_in_a_course = min(len(c['lectures']) for c in courses if c['lectures'])
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
        if os.path.isfile(f"""{transcripts_dir}/{sanitize_lecture_name(f"{c['title']}-{l['title']}")}.vtt""")
    ])
    print(f"Total lectures with transcript: {lectures_with_transcript} "
          f"({lectures_with_transcript / total_lectures * 100:.2f}%).")
    # 5.
    courses_with_transcript = len([
        c
        for c in courses
        if all(os.path.isfile(f"""{transcripts_dir}/{sanitize_lecture_name(f"{c['title']}-{l['title']}")}.vtt""")
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
    lectures_with_video = len([
        l
        for c in courses
        for l in c['lectures']
        if l['video_url']
    ])
    print(f"Total lectures with video: {lectures_with_video} "
          f"({lectures_with_video / total_lectures * 100:.2f}%).")
    # 9.
    courses_with_video = len([
        c
        for c in courses
        if all(l['video_url']
               for l in c['lectures'])
    ])
    print(f"Total courses with video: {courses_with_video} "
          f"({courses_with_video / total_courses * 100:.2f}%).")
    # 10.
    lectures_with_transcript_and_description_and_video = len([
        l
        for c in courses
        for l in c['lectures']
        if os.path.isfile(f"""{transcripts_dir}/{sanitize_lecture_name(f"{c['title']}-{l['title']}")}.vtt""") and
           l['description'] and
           l['video_url']
    ])
    print(f"Total lectures with transcript, description, and video: {lectures_with_transcript_and_description_and_video} "
          f"({lectures_with_transcript_and_description_and_video / total_lectures * 100:.2f}%).")
    # 11.
    courses_with_transcript_and_description_and_video = len([
        c
        for c in courses
        if all(os.path.isfile(f"""{transcripts_dir}/{sanitize_lecture_name(f"{c['title']}-{l['title']}")}.vtt""") and
               l['description'] and
               l['video_url']
               for l in c['lectures'])
    ])
    print(f"Total courses with transcript, description, and video: {courses_with_transcript_and_description_and_video} "
          f"({courses_with_transcript_and_description_and_video / total_courses * 100:.2f}%).")
    # 12.
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
        for c in sorted([c for c in courses if c['lectures'] and all(l['description'] for l in c['lectures'])],
                        key=lambda c: sum(len(sent_tokenize(l['description']))
                                          for l in c['lectures']) / len(c['lectures']))
    }
    plot_barh(data, xlabel="Average description length in sentences per course", ylabel="Courses")
    # 13.
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
        for c in sorted([c for c in courses if c['lectures'] and all(l['description'] for l in c['lectures'])],
                        key=lambda c: sum(len(word_tokenize(l['description']))
                                          for l in c['lectures']) / len(c['lectures']))
    }
    plot_barh(data, xlabel="Average description length in words per course", ylabel="Courses")
    # 16.

    @lox.thread(os.cpu_count())
    def _add_video_duration_in_seconds(details):
        try:
            # int(cv2.VideoCapture(l['video_url']).get(cv2.CAP_PROP_FRAME_COUNT) / int(cv2.VideoCapture(l['video_url']).get(cv2.CAP_PROP_FPS)))
            res = float(os.popen(f"ffprobe -i {details['video_url']} -show_entries format=duration -v quiet -of csv='p=0'").read())
        except ValueError:
            res = 0
        # only write to the shared object one thread at a time
        with rwlock("w"):
            courses[details['course_index']]['lectures'][details['lecture_index']]['duration_in_seconds'] = res

    if not all('duration_in_seconds' in l
               for c in courses
               for l in c['lectures']
               if l['video_url']) or \
            OVERWRITE:
        for i, c in enumerate(courses):
            for j, l in enumerate(c['lectures']):
                if l['video_url']:
                    _add_video_duration_in_seconds.scatter({
                        'course_index': i,
                        'lecture_index': j,
                        'video_url': l['video_url'],
                    })
        print("Getting video lectures durations...")
        _add_video_duration_in_seconds.gather(tqdm=True)
        update_dataset_file(courses)

    video_lectures_durations_in_seconds = [
        l['duration_in_seconds']
        for c in courses
        for l in c['lectures']
        if 'duration_in_seconds' in l
    ]

    print(f"Minimum/average/maximum duration of all video lectures: {min(video_lectures_durations_in_seconds):.2f}/"
          f"{sum(video_lectures_durations_in_seconds) / len(video_lectures_durations_in_seconds):2f}/"
          f"{max(video_lectures_durations_in_seconds):.2f} seconds.")

    data = {
        c['title']: sum(l['duration_in_seconds'] for l in c['lectures']) / len(c['lectures'])
        for c in sorted([c for c in courses if c['lectures'] and all(l['duration_in_seconds'] for l in c['lectures'])],
                        key=lambda c: sum(l['duration_in_seconds'] for l in c['lectures']) / len(c['lectures']))
    }
    plot_barh(data, xlabel="Average lecture duration in seconds per course", ylabel="Courses")

    if ratios:
        # 18.
        data = {c['title']: avg([l['description_to_transcript_length_in_words_ratio'] for l in c['lectures']])
                for c in sorted(courses,
                                key=lambda c: avg([l['description_to_transcript_length_in_words_ratio'] for l in c['lectures']]))}
        plot_barh(data, xlabel="Average description length to transcript length in words", ylabel="Courses", decimals=5)

        # 19.
        data = {c['title']: avg([l['description_to_transcript_length_in_sentences_ratio'] for l in c['lectures']])
                for c in sorted(courses,
                                key=lambda c: avg([l['description_to_transcript_length_in_sentences_ratio'] for l in c['lectures']]))}
        plot_barh(data, xlabel="Average description length to transcript length in sentences", ylabel="Courses", decimals=5)


"""
Total courses: 233.
Total lectures: 5138.
Minimum/average/maximum number of lectures per course: 1/22.05/266.
Total lectures with transcript: 4381 (85.27%).
Total courses with transcript: 179 (76.82%).
Total lectures with description: 3399 (66.15%).
Total courses with description: 179 (76.82%).
Total lectures with video: 5137 (99.98%).
Total courses with video: 232 (99.57%).
Total lectures with transcript, description, and video: 2800 (54.50%).
Total courses with transcript, description, and video: 148 (63.52%).
Minimum/average/maximum number of sentences in a lecture description: 1/2.16/13.
Minimum/average/maximum number of words in a lecture description: 3/33.23/359.
Minimum/average/maximum duration of all video lectures: 0.00/3450.028310/185820.01 seconds.
"""
"""Running analysis of the clean dataset (mitocw_lectures_dataset_clean.json)...
Total courses: 32.
Total lectures: 770.
Minimum/average/maximum number of lectures per course: 6/24.06/58.
Total lectures with transcript: 770 (100.00%).
Total courses with transcript: 32 (100.00%).
Total lectures with description: 770 (100.00%).
Total courses with description: 32 (100.00%).
Total lectures with video: 770 (100.00%).
Total courses with video: 32 (100.00%).
Total lectures with transcript, description, and video: 770 (100.00%).
Total courses with transcript, description, and video: 32 (100.00%).
Minimum/average/maximum number of sentences in a lecture description: 1/2.45/12.
Minimum/average/maximum number of words in a lecture description: 4/47.00/353.
Minimum/average/maximum duration of all video lectures: 158.46/3584.735042/6991.94 seconds.
"""


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nQuitting...")
        exit()
