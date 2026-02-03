import pandas as pd
import numpy as np
import re
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# ---------- FEATURE EXTRACTION ----------
def extract_features(password):
    length = len(password)
    upper = len(re.findall(r'[A-Z]', password))
    lower = len(re.findall(r'[a-z]', password))
    digits = len(re.findall(r'\d', password))
    special = len(re.findall(r'[!@#$%^&*(),.?":{}|<>]', password))
    entropy = len(set(password)) / length if length > 0 else 0

    return [length, upper, lower, digits, special, entropy]


# ---------- LOAD DATASET ----------
weak_passwords = []
with open("rockyou.txt", "r", encoding="latin-1") as f:
    for i, line in enumerate(f):
        if i > 50000:  # limit size for faster training
            break
        weak_passwords.append(line.strip())

# Generate strong passwords artificially
import random
import string

def generate_strong_password():
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(14))

strong_passwords = [generate_strong_password() for _ in range(len(weak_passwords))]

# ---------- CREATE DATAFRAME ----------
passwords = weak_passwords + strong_passwords
labels = [0]*len(weak_passwords) + [1]*len(strong_passwords)

features = [extract_features(p) for p in passwords]

df = pd.DataFrame(features, columns=["length", "upper", "lower", "digits", "special", "entropy"])
df["label"] = labels

# ---------- TRAIN MODEL ----------
X = df.drop("label", axis=1)
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

preds = model.predict(X_test)
print("Model Accuracy:", accuracy_score(y_test, preds))

# ---------- SAVE MODEL ----------
joblib.dump(model, "password_model.pkl")
print("Model saved as password_model.pkl")
