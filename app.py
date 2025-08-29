import os
import re
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import googleapiclient.discovery
import googleapiclient.errors
# Final Upgrade: Using a RoBERTa model trained on Twitter data for maximum slang/context accuracy
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

# --- Setup ---
app = Flask(__name__)
CORS(app)
load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

if not API_KEY:
    raise ValueError("YOUTUBE_API_KEY not found in .env file. Please create a .env file and add your key.")

# --- State-of-the-Art AI Model Loading (Twitter Emotion) ---
# This model is one of the best for understanding slang and informal text.
# The model will be downloaded on the first run.
print("Loading Twitter-trained RoBERTa model for emotion classification...")
MODEL = "cardiffnlp/twitter-roberta-base-emotion-latest"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)
emotion_pipeline = pipeline("text-classification", model=model, tokenizer=tokenizer, top_k=None)
print("Model loaded successfully.")


# --- Serve Frontend ---
@app.route("/")
def serve_index():
    """Serves the main index.html file to the user."""
    return send_from_directory('.', 'index.html')

# --- Helper Function ---
def extract_video_id(url):
    """Extracts the YouTube video ID from various common URL formats."""
    patterns = [
        r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})",
        r"(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]{11})",
        r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

# --- API Endpoint ---
@app.route("/analyze", methods=["POST"])
def analyze_comments():
    """
    API endpoint that receives a YouTube URL, fetches up to 700 comments,
    performs detailed emotion analysis, and returns a comprehensive JSON response.
    """
    data = request.get_json()
    if not data or "youtube_url" not in data:
        return jsonify({"error": "youtube_url is required"}), 400

    video_url = data["youtube_url"]
    video_id = extract_video_id(video_url)

    if not video_id:
        return jsonify({"error": "Invalid YouTube URL"}), 400

    try:
        youtube = googleapiclient.discovery.build(
            "youtube", "v3", developerKey=API_KEY
        )

        video_request = youtube.videos().list(part="snippet", id=video_id)
        video_response = video_request.execute()
        
        if not video_response.get("items"):
            return jsonify({"error": "Video not found."}), 404

        video_snippet = video_response["items"][0]["snippet"]
        video_details = {
            "title": video_snippet["title"],
            "thumbnail_url": video_snippet["thumbnails"]["medium"]["url"]
        }

        all_comments = []
        next_page_token = None
        for _ in range(7): # Fetch up to 700 comments
            comment_request = youtube.commentThreads().list(
                part="snippet", videoId=video_id, maxResults=100,
                textFormat="plainText", pageToken=next_page_token
            )
            comment_response = comment_request.execute()
            
            for item in comment_response.get("items", []):
                comment_text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                # Filter out very short, non-meaningful comments
                if len(comment_text.split()) > 2:
                    all_comments.append(comment_text)

            next_page_token = comment_response.get("nextPageToken")
            if not next_page_token:
                break

        if not all_comments:
            return jsonify({
                "error": "No meaningful comments found or comments are disabled for this video.",
                "video_details": video_details
            }), 200

        # This model outputs: anger, joy, optimism, sadness
        emotion_labels = ["anger", "joy", "optimism", "sadness"]
        emotions = {label: 0 for label in emotion_labels}
        comment_analysis = []
        batch_size = 16
        
        for i in range(0, len(all_comments), batch_size):
            batch = all_comments[i:i + batch_size]
            results = emotion_pipeline(batch, truncation=True) if batch else []

            for j, result in enumerate(results):
                comment_text = batch[j]
                top_emotion = result[0]
                label = top_emotion['label']
                score = top_emotion['score']
                
                comment_analysis.append({"text": comment_text, "label": label, "score": score})
                if label in emotions:
                    emotions[label] += 1
        
        comment_analysis.sort(key=lambda x: x["score"], reverse=True)
        top_comments_by_emotion = {label: [] for label in emotion_labels}
        
        for comment in comment_analysis:
            label = comment['label']
            if label in top_comments_by_emotion and len(top_comments_by_emotion[label]) < 2:
                top_comments_by_emotion[label].append(comment['text'])

        response_data = {
            "emotions": emotions,
            "video_details": video_details,
            "top_comments_by_emotion": top_comments_by_emotion,
            "total_comments_analyzed": len(all_comments)
        }

        return jsonify(response_data), 200

    except googleapiclient.errors.HttpError as e:
        try:
            error_details = e.error_details[0]
            if error_details["reason"] == "commentsDisabled":
                return jsonify({
                    "error": "Comments are disabled for this video.",
                    "video_details": video_details
                }), 200
        except (AttributeError, IndexError):
             pass
        print(f"An API error occurred: {e}")
        return jsonify({"error": "Could not retrieve comments. Please check the video URL and API key."}), 400
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)

