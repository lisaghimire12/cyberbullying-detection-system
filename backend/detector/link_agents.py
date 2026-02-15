from youtube_comment_downloader import YoutubeCommentDownloader

# --------------------------------------
# YOUTUBE LINK DETECTOR
# --------------------------------------
def detect_link_type(url):
    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    return "unknown"

def fetch_youtube_comments(url, limit=300):
    #Extract up to 300 comments from a YouTube video.
    downloader = YoutubeCommentDownloader()
    comments = []

    try:
        for comment in downloader.get_comments_from_url(url):
            comments.append(comment["text"])

            # STOP after 300 comments
            if len(comments) >= limit:
                break
            #extract ALL comments
            # if False:
            #     break


    except Exception as e:
        print("Error fetching comments:", e)
        return []

    return comments
