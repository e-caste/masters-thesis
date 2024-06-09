from common import *

import os
import json
import requests

from tqdm import tqdm

playlist_urls_file = "yt_playlist_urls.json"


def get_courses():
    # general YouTube API docs: https://developers.google.com/youtube/v3/getting-started
    # playlistItem docs: https://developers.google.com/youtube/v3/docs/playlistItems/list
    playlist_urls = json.load(open(playlist_urls_file, "r"))
    playlist_ids = [url.split("?list=")[-1] for url in playlist_urls]

    courses = []
    for i, playlist_id in enumerate(tqdm(playlist_ids, desc="Getting courses data from YouTube API")):
        res = requests.get(f"{yt_playlists_api_url}?part=snippet&id={playlist_id}&key={yt_api_key}")  # 1 quota
        course_title = res.json()['items'][0]['snippet']['title']
        course_description = res.json()['items'][0]['snippet']['description']

        res = requests.get(f"{yt_playlist_items_api_url}?part=snippet&maxResults=50&playlistId={playlist_id}&key={yt_api_key}")  # 1 quota
        lectures = []
        for video in res.json()['items']:
            video_id = video['snippet']['resourceId']['videoId']
            # the following code allows to use the YouTube API to retrieve the captions ID to later use it to download
            # the captions file -- BUT it uses way too much quota
            # (~43 courses * ~25 lectures/course * 50 quota = 53750) which is way higher than the daily quota (10000)
            # so, we'll just use youtube-dl to download the captions (https://superuser.com/a/927532):
            # youtube-dl --all-subs --skip-download https://www.youtube.com/watch?v=videoId

            # _res = requests.get(f"{yt_captions_api_url}?part=snippet&videoId={video_id}&key={yt_api_key}")  # 50 quota
            # caption_tracks = _res.json().get('items')
            # if caption_tracks:
            #     # prefer manually transcribed audio tracks, but fallback to auto-generated
            #     if any(cc['snippet']['trackKind'] == "standard" for cc in caption_tracks):
            #         caption_id = [cc['id'] for cc in caption_tracks if cc['snippet']['trackKind'] == "standard"][0]
            #         has_manual_transcript = True
            #     else:
            #         caption_id = [cc['id'] for cc in caption_tracks if cc['snippet']['trackKind'] == "asr"][0]
            #         has_manual_transcript = False
            # else:
            #     has_manual_transcript = None
            #     caption_id = None
            lectures.append({
                    'title': video['snippet']['title'],
                    'description': video['snippet']['description'],
                    'video_url': f"https://www.youtube.com/watch?v={video_id}",
                    # 'transcript_id': caption_id,
                    # 'has_manual_transcript': has_manual_transcript,
                })

        courses.append({
            'title': course_title,
            'url': playlist_urls[i],
            'description': course_description,
            'lectures': lectures,
        })

    return courses


def main():
    if not os.path.isfile(dataset_file) or OVERWRITE:
        courses = get_courses()
        update_dataset_file(courses)
    else:
        courses = json.load(open(dataset_file, "r"))
        ...


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nQuitting...")
        exit()
