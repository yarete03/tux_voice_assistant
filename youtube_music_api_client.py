from googleapiclient.discovery import build
from secrets import api_key
from webbrowser import open


def youtube_api_query(query):
    youtube = build('youtube', 'v3', developerKey=api_key)
    search_request = youtube.search().list(
        part="id",
        q=query,
        type="video",
        maxResults=1
    )
    search_response = search_request.execute()
    video_id = search_response["items"][0]["id"]["videoId"]
    open(f"https://music.youtube.com/watch?v={video_id}&autoplay=1")
