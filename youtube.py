from googleapiclient.discovery import build
from datetime import datetime, timedelta
from google import  genai


API_KEY = "YOUTUBE_API_KEY_HERE"
GEMINI_API_KEY  = "GEMINI_API_KEY_HERE"
def get_youtube_titles(query):
    youtube = build("youtube", "v3", developerKey=API_KEY)

    published_after = (datetime.utcnow() - timedelta(days=14)).isoformat() + "Z"

    # Search for videos
    search_response = youtube.search().list(
        q=query,
        part="id",
        type="video",
        maxResults=20,
        publishedAfter=published_after
    ).execute()

    video_ids = [item["id"]["videoId"] for item in search_response["items"]]

    # Get video details (length & title)
    video_response = youtube.videos().list(
        part="snippet,contentDetails",
        id=",".join(video_ids)
    ).execute()

    valid_videos = []
    for video in video_response["items"]:
        duration = video["contentDetails"]["duration"]
        title = video["snippet"]["title"]

        minutes = parse_duration(duration)

        if 4 <= minutes <= 20:
            valid_videos.append(title)

    return valid_videos

def parse_duration(duration):
    import isodate
    duration_obj = isodate.parse_duration(duration)
    return duration_obj.total_seconds() / 60


def find_best_title(titles):
    # Create a prompt with numbered titles
    prompt = "Which of these video titles is the best based on relevance and engagement? Give only one title and a brief decription as to why you chose it.\n\n"
    for i, title in enumerate(titles, start=1):
        prompt += f"{i}. {title}\n"
    client = genai.Client(api_key=GEMINI_API_KEY)
    # Send request to Gemini
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,)
    return response.text.strip()



query = input("Enter query to be searched: ")

titles = get_youtube_titles(query)
print(titles)
best_title = find_best_title(titles)

print("Best Video Title:", best_title)
