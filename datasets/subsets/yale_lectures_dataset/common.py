import json
import string

OVERWRITE = False

dataset_file = "yale_lectures_dataset.json"
clean_dataset_file = "yale_lectures_dataset_clean.json"
transcripts_only_dataset_file = "yale_lectures_dataset_transcripts_only.json"
data_dir = "./data"
videos_dir = f"{data_dir}/videos"
transcripts_dir = f"{data_dir}/transcripts"

yt_api_url = "https://youtube.googleapis.com/youtube/v3"
yt_playlists_api_url = f"{yt_api_url}/playlists"
yt_playlist_items_api_url = f"{yt_api_url}/playlistItems"
yt_captions_api_url = f"{yt_api_url}/captions"
yt_videos_api_url = f"{yt_api_url}/videos"
yt_api_key = "YOUR API KEY"


def update_dataset_file(contents, clean=False, transcripts_only=False):
    if clean:
        output_file = clean_dataset_file
    elif transcripts_only:
        output_file = transcripts_only_dataset_file
    else:
        output_file = dataset_file
    with open(output_file, "w") as f:
        json.dump(contents, f, indent=4, ensure_ascii=False)


def sanitize_lecture_name(name: str) -> str:
    """given the title for a lecture, return a sanitized version that is filesystem friendly"""
    result = ""
    for character in name:
        if character in string.ascii_letters or character in string.digits:
            result += character
        elif character == "&":
            result += "and"
        elif character in "()[]{}":
            result += "+"
        else:
            result += "-"
    return result


def avg(lst):
    return sum(lst) / len(lst) if len(lst) > 0 else 0
