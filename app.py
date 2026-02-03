from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.analyzer import rule_based_score, pattern_penalty, crack_time_estimate, password_breakdown
from utils.breach_check import check_breach
from utils.generator import generate_password, generate_passphrase
from utils.db import log_analysis, get_stats
from functools import lru_cache
from utils.leak_check import find_similar_passwords, password_in_list
import threading

app = Flask(__name__)
CORS(app)

# -----------------------------
# CACHE HEAVY CALCULATIONS
# -----------------------------
@lru_cache(maxsize=5000)
def cached_crack_time(pwd):
    return crack_time_estimate(pwd)

@lru_cache(maxsize=5000)
def cached_breach_check(pwd):
    return check_breach(pwd)

# -----------------------------
# BACKGROUND LOGGING THREAD
# -----------------------------
def log_in_background(score, breach, crack_time):
    thread = threading.Thread(
        target=log_analysis,
        args=(score, breach, crack_time)
    )
    thread.daemon = True
    thread.start()

# -----------------------------
# ROUTES
# -----------------------------
@app.route("/")
def home():
    return "Password Analyzer API Running"

@app.route("/generate-passphrase", methods=["GET"])
def passphrase():
    return jsonify({"passphrase": generate_passphrase()})


@app.route("/analyze", methods=["POST"])
def analyze():
    def analyze():
    data = request.json
    password = data.get("password", "")
    
    score = len(password)  # simple test logic
    return jsonify({"score": score})
    data = request.get_json()
    if not data or "password" not in data:
        return jsonify({"error": "Password required"}), 400

    pwd = data["password"]

    # Score calculation
    score, fb1 = rule_based_score(pwd)
    penalty, fb2 = pattern_penalty(pwd)
    final_score = max(0, min(100, score - penalty))

    # Color
    if final_score < 40:
        color = "red"
    elif final_score < 70:
        color = "orange"
    else:
        color = "green"

    # Cached heavy operations (FAST after first call)
    crack_time = cached_crack_time(pwd)
    breach = cached_breach_check(pwd)

    # Background logging (non-blocking)
    log_in_background(final_score, breach, crack_time)

    return jsonify({
        "score": final_score,
        "feedback": fb1 + fb2,
        "crack_time": crack_time,
        "breach": breach,
        "color": color,
        "breakdown": password_breakdown(pwd)
    })


@app.route("/stats", methods=["GET"])
def stats():
    return jsonify(get_stats())

@app.route("/leak-check", methods=["POST"])
def leak_check():
    data = request.json
    pwd = data.get("password")

    leaked = password_in_list(pwd)
    similar = find_similar_passwords(pwd)   # ← REMOVE condition

    return jsonify({
        "leaked": leaked,
        "similar": similar
    })



if __name__ == "__main__":
    # Turn OFF debug in production for speed
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
