from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = ["Insert your key here"]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
videos = []
channels = []
playlists = []


# Add each result to the appropriate list, and then display the lists of
# matching videos, channels, and playlists.

def youtube_search(options):
    videos_Results = []
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

    search_response = youtube.search().list(
        q=options['q'],
        part="id, snippet",
        maxResults=options['max_results']
    ).execute()
    for search_result in search_response.get("items", []):
        if search_result['id']['kind'] == 'youtube#video':
            res = {
                'title': search_result['snippet']['title'],
                'videoId': search_result['id']['videoId'],
                'description': search_result['snippet']['description'],
                'image': search_result['snippet']['thumbnails']['medium']['url'],
                'embed': "https://www.youtube.com/embed/" + search_result['id']['videoId']
            }
            videos_Results.append(res)
        if len(videos_Results) >= 50:
            break
    return videos_Results


if __name__ == "__main__":
    argparser.add_argument("--q", help="Search term", default="Google")
    argparser.add_argument("--max-results", help="Max results", default=25)
    args = argparser.parse_args()

    try:
        youtube_search(args)
    except HttpError as e:
        print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
