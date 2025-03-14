from api_token import ytmusic_oauth_client_id, ytmusic_oauth_client_secret
from ytmusicapi import YTMusic, OAuthCredentials


def youtube_api_query(query):
    ytmusic = YTMusic('oauth.json', oauth_credentials=OAuthCredentials(client_id=ytmusic_oauth_client_id,
                                                                       client_secret=ytmusic_oauth_client_secret))
    test = ytmusic.get_search_suggestions(query)[0]
    search_results = ytmusic.search(test, filter="songs")[0]
    print(search_results)
    video_id = search_results['videoId']
    return f"https://music.youtube.com/watch?v={video_id}&autoplay=1"
