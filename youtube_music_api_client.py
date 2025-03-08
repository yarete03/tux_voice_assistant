from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from api_token import youtube_api_key


def youtube_api_query(query):
    try:
        youtube = build('youtube', 'v3', developerKey=youtube_api_key)
        search_request = youtube.search().list(
            part="id",
            q=query + " music",
            type="video",
            maxResults=1
        )
        search_response = search_request.execute()
        video_id = search_response["items"][0]["id"]["videoId"]
        return f"https://music.youtube.com/watch?v={video_id}&autoplay=1"
    except HttpError as error:
        print(f'Error: {error}')
        return False