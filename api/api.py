from flask import Flask, request, jsonify
import instaloader
import requests

app = Flask(__name__)

def clean_instagram_url(url: str) -> str:
    """Cleans Instagram URL by removing tracking parameters and replacing 'reel' with 'p'."""
    url = url.split("?")[0]  # Remove URL parameters
    url = url.replace("/reel/", "/p/")  # Convert Reel to Post URL
    return url

@app.route('/get_instagram_video', methods=['GET'])
def get_instagram_video():
    """Fetches the Instagram video URL, title, and size."""
    try:
        url = request.args.get("url")
        if not url:
            return jsonify({"status": "error", "message": "Missing 'url' parameter"}), 400
        
        clean_url = clean_instagram_url(url)
        shortcode = clean_url.split("/")[-2]

        # Initialize Instaloader
        loader = instaloader.Instaloader(
            download_comments=False,
            download_geotags=False,
            download_pictures=False,
            download_video_thumbnails=False,
            save_metadata=False
        )

        # Fetch post details
        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        if post.is_video:
            video_url = post.video_url
            title = post.caption.split("\n")[0] if post.caption else "No Title"

            # Get video file size
            response = requests.head(video_url)
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

if __name__ == '__main__':
    app.run(debug=True)

