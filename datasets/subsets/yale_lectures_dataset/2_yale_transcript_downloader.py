from common import *

import json
import os

import lox

@lox.thread(os.cpu_count())
def download_transcripts(details):
    file_name = sanitize_lecture_name(f"{details['course_title']}-{details['lecture_title']}")
    os.popen(
        f"""
        youtube-dl \
        --skip-download \
        --all-subs \
        --sub-format vtt \
        --sub-lang en \
        --output '{transcripts_dir}/{file_name}.%(ext)s' \
        {details['video_url']}
        """
    ).read()


def main():
    for dir_name in (data_dir, transcripts_dir):
        os.makedirs(dir_name, exist_ok=True)

    courses = json.load(open(dataset_file, "r"))
    for course in courses:
        for lecture in course['lectures']:
            download_transcripts.scatter({
                'course_title': course['title'],
                'lecture_title': lecture['title'],
                'video_url': lecture['video_url'],
            })
    print(f"Downloading transcripts to {transcripts_dir}...")
    download_transcripts.gather(tqdm=True)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nQuitting...")
        exit()
