from flask import Flask, request, jsonify
import instaloader
import requests
from flask_caching import Cache
import concurrent.futures
import random

app = Flask(__name__)

# Configure cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# List of proxies
PROXIES = [
    'https://52.73.224.54:3128',
    'https://54.248.238.110:80',
    'https://13.59.156.167:3128'
]

def clean_instagram_url(url: str) -> str:
    """Cleans Instagram URL by removing tracking parameters and replacing 'reel' with 'p'."""
    url = url.split("?")[0]  # Remove URL parameters
    url = url.replace("/reel/", "/p/")  # Convert Reel to Post URL
    return url

def fetch_post_details(shortcode):
    """Fetch post details using Instaloader."""
    loader = instaloader.Instaloader(
        download_comments=False,
        download_geotags=False,
        download_pictures=False,
        download_video_thumbnails=False,
        save_metadata=False
    )
    return instaloader.Post.from_shortcode(loader.context, shortcode)

@app.route("/get_instagram_video", methods=["GET"])
@cache.cached(timeout=300, query_string=True)
def get_instagram_video():
    """Fetches the Instagram video URL, title, and size."""
    try:
        url = request.args.get("url")
        if not url:
            return jsonify({"status": "error", "message": "Missing 'url' parameter"}), 400
        
        clean_url = clean_instagram_url(url)
        shortcode = clean_url.split("/")[-2]

        # Use a random proxy
        proxy = {'http': random.choice(PROXIES)}
        post = fetch_post_details(shortcode)

        if post.is_video:
            video_url = post.video_url
            title = post.caption.split("\n")[0] if post.caption else "No Title"

            # Get video file size
            response = requests.head(video_url, proxies=proxy)
            size_bytes = int(response.headers.get("content-length", 0))
            size_mb = size_bytes / (1024 * 1024)

            return jsonify({
                "status": "success",
                "video_url": video_url,
                "title": title,
                "video_size_MB": round(size_mb, 2)
            })
        else:
            return jsonify({"status": "error", "message": "This post does not contain a video."}), 400
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(threaded=True)
