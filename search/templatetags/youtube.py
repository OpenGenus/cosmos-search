import requests
from apiclient.discovery import build
import json
from cosmos_search.settings import DEVELOPER_KEY
from django.core.cache import cache

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


def fetchJson(url):
    cached = cache.get(url)
    if not cached:
        return False
    else:
        return cached


videos_Results = []


def youtube_search(options):
    global videos_Results
    if not options['next_page']:
        videos_Results = []
    content_details = "https://www.googleapis.com/youtube/v3/videos?part=contentDetails&"
    SEARCH = "https://www.googleapis.com/youtube/v3/search?"
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)
    i = int(options['id'])
    url = (SEARCH + 'q=' + options['q'] +
           '&part=id,snippet&maxResults=' +
           str(options['max_results']) + '&pageToken=' +
           options['next_page'] + '&type=video&videoEmbeddable=true&key=' + DEVELOPER_KEY)

    search_response = fetchJson(url)
    if not search_response:
        search_response = youtube.search().list(
            q=options['q'],
            part="id, snippet",
            maxResults=options['max_results'],
            pageToken=options['next_page'],
            type='video',
            videoEmbeddable='true',
        ).execute()
        if search_response:
            cache.set(url, search_response)

    next_page = search_response.get('nextPageToken')
    for search_result in search_response.get("items", []):
        if search_result['id']['kind'] == 'youtube#video':
            q = {
                'id': search_result['id']['videoId'],
                'key': DEVELOPER_KEY
            }
            d = fetchJson(content_details + '&id=' + q['id'] + '&key=' + q['key'])
            if d:
                content = json.loads(d)
            else:
                response = requests.get(content_details, q)
                if response.ok:
                    cache.set(response.url, response.content.decode('utf-8'))
                    content = json.loads(response.content.decode('utf-8'))

            content = list(content['items'])
            durationh = content[0]['contentDetails']['duration'].split('PT')[-1].split('H')
            if len(durationh) > 1:
                h = durationh[0]
                H = durationh[1]
            else:
                h = 0
                H = durationh[0]
            durationm = H.split('M')
            if len(durationm) > 1:
                m = durationm[0]
                M = durationm[1]
            else:
                m = 0
                M = durationm[0]
            durations = M.split('S')

            if len(durations) > 1:
                s = durations[0]
            else:
                s = 0
            duration = str(h) + ":" + str(m) + ":" + str(s)
            pdate = search_result['snippet']['publishedAt'].split("T")[0]
            ptime = search_result['snippet']['publishedAt'].split("T")[1].split(".")[0]
            res = {
                'id': i,
                'title': search_result['snippet']['title'],
                'videoId': search_result['id']['videoId'],
                'description': search_result['snippet']['description'],
                'image': search_result['snippet']['thumbnails']['high']['url'],
                'embed': "https://www.youtube.com/embed/" + search_result['id']['videoId'],
                'date': pdate,
                'time': ptime,
                'duration': duration
            }

            videos_Results.append(res)
            i += 1

    return {'videos_Results': videos_Results, 'nextpage': next_page}
