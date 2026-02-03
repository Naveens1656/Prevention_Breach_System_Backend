from tinydb import TinyDB
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
import os

DB_PATH = "db.json"

# Ensure DB file exists
if not os.path.exists(DB_PATH):
    with open(DB_PATH, "w") as f:
        f.write("{}")

db = TinyDB(DB_PATH, storage=CachingMiddleware(JSONStorage))

def log_analysis(score, breach, crack_time):
    try:
        db.insert({
            "score": score,
            "breach": breach,
            "crack_time": crack_time
        })
        db.storage.flush()
    except Exception as e:
        print("DB Write Error:", e)


# 🔥 NEW FUNCTION — used by your dashboard
def get_stats():
    try:
        records = db.all()

        if not records:
            return {
                "total": 0,
                "avg_score": 0,
                "breaches": 0
            }

        total = len(records)
        avg_score = sum(r.get("score", 0) for r in records) / total
        breaches = sum(1 for r in records if r.get("breach"))

        return {
            "total": total,
            "avg_score": round(avg_score, 2),
            "breaches": breaches
        }
    except Exception as e:
        print("DB Read Error:", e)
        return {
            "total": 0,
            "avg_score": 0,
            "breaches": 0
        }
