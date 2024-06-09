from common import *

import os
import json
import requests

import lox


@lox.thread(os.cpu_count())
def download_file(details):
    file_name_no_ext = f"{details['dir']}/{details['name']}"
    file_name = f"{file_name_no_ext}.{details['extension']}"

    res = requests.get(details['url'], stream=True)
    file_size = int(res.headers.get('Content-Length', 0))

    # download not existing files and re-download only partially downloaded files
    if not os.path.isfile(file_name) or \
            (os.path.isfile(file_name) and os.path.getsize(file_name) < file_size) or \
            OVERWRITE:
        with open(file_name, 'wb') as f:
            for data in res:
                f.write(data)

    return file_name


def main():
    for dir_name in (data_dir, transcripts_dir):
        os.makedirs(dir_name, exist_ok=True)

    courses = json.load(open(dataset_file, "r"))
    for course in courses:
        for lecture in [l for l in course['lectures'] if l['transcript_url']]:
            download_file.scatter({
                'dir': transcripts_dir,
                'name': sanitize_lecture_name(f"{course['title']}-{lecture['title']}"),
                'extension': "vtt",
                'url': lecture['transcript_url'],
            })
    print(f"Downloading transcripts to {transcripts_dir}...")
    download_file.gather(tqdm=True)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nQuitting...")
        exit()
