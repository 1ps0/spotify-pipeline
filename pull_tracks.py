import os
import json
import time
import boto3

from pathlib import Path

from .lib.spotify_api import SpotifyAPI
from .lib.ops import *

ROOT_PATH = "metadata/spotify"
TRACKS = f"{ROOT_PATH}/tracks"
TRACKLIST = f"{ROOT_PATH}/tracklist"
PLAYLIST = f"{ROOT_PATH}/playlists"
PLAYLIST_TRACKS = "library/playlists/tracks"

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

    # TODO make list updating
    library = local_load_data("data/tracks.json")
    if not library or not len(library):
        print("Library not found, getting tracklist")
        library = api_client.get_tracks()

        tracklist_path = Path(f"data/track_list/{stamp}.json")
        local_save_data(str(tracklist_path), json.dumps(library))
        tracks_path = Path('data/tracks.json')
        if tracks_path.exists():
            tracks_path.unlink('data/tracks.json')

        try:
            os.symlink(str(tracklist_path), 'data/tracks.json')
        except Exception as err:
            print(err)

    for page in library:
        for item in page.get('items', []):
            track = item.get('track', {})
            track_id = track.get('id')
            if not track_id:
                breakpoint()

            analysis_path = f'data/tracks/{track_id}/analysis.json'
            if not os.path.exists(analysis_path):
                print(f"Getting analysis for {track_id}")
                analysis_data = api_client.get_analysis(track_id)
                local_save_data(analysis_path, json.dumps(analysis_data))
                print("Saved analysis")

            features_path = f'data/tracks/{track_id}/features.json'
            if not os.path.exists(features_path):
                print(f"Getting features for {track_id}")
                features_data = api_client.get_features(track_id)
                local_save_data(features_path, json.dumps(features_data))
                print("Saved features")

            artists = track.get('artists', [])
            for artist in artists:
                artist_id = artist['id']
                # breakpoint()
                artist_path = f'data/artists/{artist_id}.json'
                if not os.path.exists(artist_path):
                    print(f"Getting artist data for {artist_id}")
                    artist_data = api_client.get_artist(artist_id)
                    if 'error' in artist_data:
                        print("Failed to save artist_data")
                        error_log.append(artist_data)
                    else:
                        local_save_data(artist_path, json.dumps(artist_data))
                        print("Saved artist")

    local_save_data(f"data/log/errors-{stamp}.log", json.dumps(error_log))

    # Get the object from the event and show its content type
    # bucket = event['Records'][0]['s3']['bucket']['name']
    # key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    # try:
    #     response = s3.get_object(Bucket=bucket, Key=key)
    #     print("CONTENT TYPE: " + response['ContentType'])
    #     return response['ContentType']
    # except Exception as e:
    #     print(e)
    #     print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
    #     raise e

if __name__ == '__main__':
    run(None, None)
