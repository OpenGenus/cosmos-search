import requests
from apiclient.discovery import build
import json
# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# Please ensure that you have enabled the YouTube Data API for your project.

DEVELOPER_KEY = ["Insert your API key here"]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


def youtube_search(options):
    videos_Results = []
    status_link = "https://www.googleapis.com/youtube/v3/videos?part=status&"
    content_details = "https://www.googleapis.com/youtube/v3/videos?part=contentDetails&"
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

    search_response = youtube.search().list(
        q=options['q'],
        part="id, snippet",
        maxResults=options['max_results']
    ).execute()

    i = 0

    for search_result in search_response.get("items", []):
        if search_result['id']['kind'] == 'youtube#video':
            q = {
                'id': search_result['id']['videoId'],
                'key': DEVELOPER_KEY
            }
            response = requests.get(status_link, q)
            data = list(json.loads(response.content)['items'])
            if data[0]['status']['embeddable']:
                response = requests.get(content_details, q)
                content = list(json.loads(response.content)['items'])

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
            if len(videos_Results) >= 50:
                break
    return videos_Results
