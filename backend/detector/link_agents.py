import requests
from bs4 import BeautifulSoup
from youtube_comment_downloader import YoutubeCommentDownloader

# ---------------------------
# LINK TYPE DETECTOR AGENT
# ---------------------------
def detect_link_type(url):
    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    if "amazon." in url or "flipkart." in url or "meesho." in url:
        return "ecommerce"
    return "unknown"


# ---------------------------
# YOUTUBE AGENT
# ---------------------------
def fetch_youtube_comments(url, limit=20):
    downloader = YoutubeCommentDownloader()
    comments = []

    for comment in downloader.get_comments_from_url(url):
        comments.append(comment["text"])
        if len(comments) >= limit:
            break

    return comments


# ---------------------------
# ECOMMERCE AGENT
# ---------------------------
def fetch_ecommerce_reviews(url):

    try:
        res = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0"
        })
    except Exception as e:
        print("Request failed:", e)
        return []

    if res.status_code != 200:
        print("Failed to fetch page")
        return []

    soup = BeautifulSoup(res.text, "html.parser")

    reviews = []

    # Try extracting paragraph text as demo
    for p in soup.find_all("p"):
        text = p.get_text().strip()
        if len(text) > 30:
            reviews.append(text)

    return reviews[:10]