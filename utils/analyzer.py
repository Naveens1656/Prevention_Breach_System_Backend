import re
import math
import joblib
import os

# Load ML model
model_path = os.path.join(os.path.dirname(__file__), "../ml_model/password_model.pkl")
model = joblib.load(model_path)

common_words = ["password", "admin", "welcome", "india", "love", "1234"]

# ================= RULE-BASED SCORE =================
def rule_based_score(pwd):
    score = 0
    feedback = []

    if len(pwd) >= 12: score += 20
    else: feedback.append("Password too short")

    if re.search(r"[A-Z]", pwd): score += 15
    else: feedback.append("Add uppercase letter")

    if re.search(r"[a-z]", pwd): score += 15
    else: feedback.append("Add lowercase letter")

    if re.search(r"[0-9]", pwd): score += 15
    else: feedback.append("Add numbers")

    if re.search(r"[!@#$%^&*]", pwd): score += 20
    else: feedback.append("Add special character")

    return score, feedback

# ================= ML STRENGTH SCORE =================
def ml_strength_score(pwd):
    features = extract_features(pwd)
    prediction = model.predict([features])[0]
    return 20 if prediction == 1 else -20

# ================= PASSWORD BREAKDOWN (Radar Chart) =================
def password_breakdown(pwd):
    """
    Returns metrics in frontend radar chart format:
    {
        "length": 0-5,
        "symbols": 0-5,
        "entropy": 0-5,
        "uniqueness": 0-5
    }
    """
    length = min(len(pwd) / 4, 5)  # scale 0-5
    uppercase = len(re.findall(r"[A-Z]", pwd))
    lowercase = len(re.findall(r"[a-z]", pwd))
    digits = len(re.findall(r"[0-9]", pwd))
    symbols = len(re.findall(r"[!@#$%^&*]", pwd))

    # Entropy estimate
    pool = 0
    if uppercase > 0: pool += 26
    if lowercase > 0: pool += 26
    if digits > 0: pool += 10
    if symbols > 0: pool += 32
    entropy = min(5, (len(pwd) * math.log2(pool)) / 40) if pool > 0 else 0

    # Uniqueness score
    uniqueness = 5
    if re.search(r"(.)\1\1", pwd): uniqueness -= 2
    if any(word in pwd.lower() for word in common_words): uniqueness -= 2
    uniqueness = max(0, uniqueness)

    return {
        "length": round(length, 2),
        "uppercase": uppercase,
        "lowercase": lowercase,
        "digits": digits,
        "symbols": symbols,
        "entropy": round(entropy, 2),
        "uniqueness": round(uniqueness, 2)
    }

# ================= PATTERN PENALTY =================
def pattern_penalty(pwd):
    penalty = 0
    feedback = []
    lower_pwd = pwd.lower()

    for word in common_words:
        if word in lower_pwd:
            penalty += 20
            feedback.append("Contains common word")

    if re.search(r"(.)\1\1", pwd):
        penalty += 10
        feedback.append("Repeated characters")

    if re.search(r"123|abc|qwe", lower_pwd):
        penalty += 15
        feedback.append("Sequential pattern detected")

    return penalty, feedback

# ================= CRACK TIME ESTIMATE =================
def crack_time_estimate(pwd):
    charset = 0
    if re.search(r"[a-z]", pwd): charset += 26
    if re.search(r"[A-Z]", pwd): charset += 26
    if re.search(r"[0-9]", pwd): charset += 10
    if re.search(r"[!@#$%^&*]", pwd): charset += 10

    combos = charset ** len(pwd) if charset > 0 else 1
    seconds = combos / 1e9  # assume 1 billion guesses/sec

    if seconds < 60: return "Less than a minute"
    elif seconds < 3600: return "Hours"
    elif seconds < 86400: return "Days"
    elif seconds < 31536000: return "Months"
    else: return "Years"
