from flask import Flask, request, jsonify
import instaloader
import requests
import time
import random

app = Flask(__name__)

# Instagram Login
USERNAME = "pakkijobs"
SESSION_FILE = "pakkijobs"

def get_instaloader():
    """Returns an authenticated Instaloader session with delays."""
    loader = instaloader.Instaloader()
    loader.load_session_from_file(SESSION_FILE)
    time.sleep(random.randint(5, 15))  # Prevent rate-limiting
    return loader

@app.route("/get_instagram_video", methods=["GET"])
def get_instagram_video():
    try:
        url = request.args.get("url")
        if not url:
            return jsonify({"status": "error", "message": "Missing 'url' parameter"}), 400
        
        shortcode = url.split("/")[-2]

        loader = get_instaloader()
        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        if post.is_video:
            video_url = post.video_url
            title = post.caption.split("\n")[0] if post.caption else "No Title"

            # Get video file size with headers
            headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_2 like Mac OS X)"}
            response = requests.head(video_url, headers=headers)
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
    app.run(debug=True)
