from googleapiclient.discovery import build
from config import YOUTUBE_API_KEY

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

def search_youtube_videos(query, max_results=5):
    """
    Search YouTube for videos related to the given query.
    By default, fetches up to 5 videos; you can override this with max_results.
    """
    request = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=max_results
    )
    response = request.execute()
    
    videos = []
    for item in response.get("items", []):
        videos.append({
            "title": item["snippet"]["title"],
            "video_id": item["id"]["videoId"],
            "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
            "channel": item["snippet"]["channelTitle"],
            "published_at": item["snippet"]["publishedAt"]
        })
    return videos
