import os

import requests

from .ops import local_load_data

API_URL = "https://api.spotify.com"

def get_access_token():
    print('getting new token')
    # global access_token
    # if access_token:
    #     return access_token
    tokens = local_load_data('spotify_auth_tokens.json')
    refresh_token = os.getenv('SPOTIFY_REFRESH_TOKEN', tokens['refresh_token'])
    hash_auth = f"Basic {os.getenv('SPOTIFY_HASH')}"

    data = {'grant_type': 'refresh_token', 'refresh_token': refresh_token}

    headers = {'Authorization': hash_auth }
    ret = requests.post('https://accounts.spotify.com/api/token', data=data, headers=headers)
    ret_json = ret.json()
    ret_token = ret_json.get('access_token')
    if ret_token:
        # access_token = ret_token
        # TODO save to dynamo
        return { 'Authorization': f"Bearer {ret_token}", 'Content-Type': 'application/json', 'Accept': 'application/json' }

    else:
        raise Exception("Failed to get access token")

class SpotifyAPI():
    def __init__(self):
        self.err_count = 0
        self.access_token = get_access_token()

    def get_req(self, url:str):
        response = None
        try:
            response = requests.get(
                url,
                headers=self.access_token
            )

            status_code = response.status_code
            if status_code == 200:
                return response.json()

            elif status_code in (404, 401, 403):
                print(status_code, "for", url)
                self.err_count += 1
                return { 'error': { 'status_code': status_code, 'url': url }}

            elif status_code == 419:
                breakpoint()
                retry_after = response.headers.get('Retry-After', 5)
                time.sleep(retry_after)
                return self.get_req(url)

            elif status_code == 502:
                #breakpoint()
                print('Bugger. 502 -----')

            else:
                breakpoint()
                self.access_token = get_access_token()
                time.sleep(10)
                return self.get_req(url)

        except Exception as e:
            print(e)
            breakpoint()
            return None

    def get_analysis(self, track_id:str):
        return self.get_req(f"{API_URL}/v1/audio-analysis/{track_id}")

    def get_features(self, track_id:str):
        return self.get_req(f"{API_URL}/v1/audio-features/{track_id}")

    def get_artist(self, artist_id:str):
        return self.get_req(f"{API_URL}/v1/artists/{artist_id}")

    def get_personalization(self, type:str):
        return self.paginate(f"{API_URL}/v1/me/top/{type}")

    def get_tracks(self):
        return self.paginate(f"{API_URL}/v1/me/tracks")

    def get_playlists(self, ):
        return self.get_req(f"{API_URL}/v1/me/playlists")

    def get_playlist_tracks(self, playlist_id:str):
        return self.get_req(f"{API_URL}/v1/playlists/{playlist_id}/tracks")

    def get_recently_played(self):
        return self.get_req(f"{API_URL}/v1/me/player/currently-playing")

    def paginate(self, url):
        pages = []
        next_url = url
        while next_url:
            print(f"Have {len(pages)} pages. now fetching {next_url}")
            page_current = self.get_req(next_url)
            next_url = page_current.get('next')
            pages.append(page_current)
        return pages
