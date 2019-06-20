import os
import json
import time
import urllib.parse
import boto3
import requests

from lib.spotify_api import SpotifyAPI
from lib.ops import *

# Only called if the current accessToken is expired (on first visit after ~1hr)

print('Loading function')

# Only called if the current accessToken is expired (on first visit after ~1hr)

API_URL = "https://api.spotify.com"

s3 = boto3.client('s3', 'us-west-2')
bucket = os.getenv('S3_BUCKET', 'aural-analysis-repository')

ROOT_PATH = "metadata/spotify"
RECENT = f"{ROOT_PATH}/recent_played"
TRACKS = f"{ROOT_PATH}/tracks"
TRACKLIST = f"{ROOT_PATH}/tracklist"
PLAYLIST = f"{ROOT_PATH}/playlists"
PLAYLIST_TRACKS = "library/playlists/tracks"

from pathlib import Path

def run(event, context):
    """
    1. get access token
    2. pull library list
    3. get previous library list from s3 (s3://aural-analysis-repository/library/tracklist/)
    4. dump current list to s3
    5. calculate diff of list and add to the sqs as individual messages
    6. pull playlist set
    7. pull set from s3 (s3://aural-analysis-repository/library/playlist)
    7. dump set to s3
    8. pull tracklist for each playlist
    9. dump tracklist to s3 ((s3://aural-analysis-repository/library/playlists/tracks))
    """
    api_client = SpotifyAPI()
    error_log = []

    stamp = int(datetime.utcnow().timestamp())

    api_client.get_recently_played

    me_last_scans = sorted(local_files(path='data/me/artists/', recursive=False))
    if len(me_last_scans):
        me_last_scan = int(me_last_scans[0].stem) # timestamp
        if (timestamp_now() - me_last_scan) / 3600 >= 1: # 1 day threshold
            print("Pulling recently played")
            me_recently_played = api_client.get_recently_played()
            local_save_data(f"data/me/recently_played/{stamp}.json", json.dumps(me_recently_played))
            print(f"Got {len(me_recently_played)} objects")


    print("Done")

if __name__ == '__main__':
    run(None, None)
