from youtube_comment_downloader import YoutubeCommentDownloader


# --------------------------------------
# YOUTUBE LINK DETECTOR
# --------------------------------------
def detect_link_type(url):
    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    return "unknown"


# --------------------------------------
# YOUTUBE COMMENT EXTRACTION AGENT
# --------------------------------------
def fetch_youtube_comments(url, limit=300):

    downloader = YoutubeCommentDownloader()
    comments = []

    try:
        for comment in downloader.get_comments_from_url(url):
            comments.append(comment["text"])

            # ✅ THIS MUST BE INSIDE LOOP
            if len(comments) >= limit:
                break

    except Exception as e:
        print("Error fetching comments:", e)
        return []

    print("TOTAL COMMENTS FETCHED:", len(comments))
    return comments


# def fetch_youtube_comments(url):

#     downloader = YoutubeCommentDownloader()
#     comments = []

#     try:
#         for comment in downloader.get_comments_from_url(url):
#             comments.append(comment["text"])
#     except Exception as e:
#         print("Error:", e)
#         return []

#     print("TOTAL COMMENTS FETCHED:", len(comments))
#     return comments
