from youtube_comment_downloader import YoutubeCommentDownloader
import requests

API_URL = "http://127.0.0.1:8000/api/predict/"

downloader = YoutubeCommentDownloader()

video_url = input("Paste YouTube video link: ")

print("\nFetching comments...\n")

comments = downloader.get_comments_from_url(video_url)

count = 0

for comment in comments:
    text = comment["text"]

    if len(text.strip()) > 3:
        response = requests.get(API_URL, params={"text": text})
        result = response.json()

        print("Comment:", text)
        print("Prediction:", result["prediction"])

        if "hash" in result:
            print("Hash:", result["hash"])
            print("Timestamp:", result["timestamp"])

        print("-" * 60)

        count += 1
        if count == 20:
            break   # only first 20 comments
