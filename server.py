import json
import os
from flask import Flask, request, jsonify, send_from_directory, after_this_request
from flask_cors import CORS  # <-- Add this import

app = Flask(__name__)
CORS(app)  # <-- This opens up your API so your GitHub Pages site can talk to it


@app.after_request
def allow_framing(response):
    response.headers.pop("X-Frame-Options", None)
    response.headers["Content-Security-Policy"] = "frame-ancestors *"
    return response

SCORES_FILE = "scores.json"


def load_scores():
    if not os.path.exists(SCORES_FILE):
        return []
    with open(SCORES_FILE, "r") as f:
        try:
            return json.load(f)
        except Exception:
            return []


def save_scores(scores):
    with open(SCORES_FILE, "w") as f:
        json.dump(scores, f)


@app.route("/")
def index():
    return send_from_directory(".", "Earth2025.html")


@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(".", filename)


@app.route("/api/scores", methods=["GET"])
def get_scores():
    scores = load_scores()
    scores.sort(key=lambda x: x["score"], reverse=True)
    return jsonify(scores[:20])


@app.route("/api/scores", methods=["POST"])
def post_score():
    data = request.get_json()
    name = str(data.get("name", "Anonymous")).strip()[:30]
    score = int(data.get("score", 0))
    difficulty = str(data.get("difficulty", "normal"))
    if difficulty not in ("easy", "normal", "hard"):
        difficulty = "normal"
    if not name:
        name = "Anonymous"
    scores = load_scores()
    scores.append({"name": name, "score": score, "difficulty": difficulty})
    scores.sort(key=lambda x: x["score"], reverse=True)
    scores = scores[:100]
    save_scores(scores)
    rank = next((i + 1 for i, s in enumerate(scores) if s["name"] == name and s["score"] == score), None)
    return jsonify({"success": True, "rank": rank})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
