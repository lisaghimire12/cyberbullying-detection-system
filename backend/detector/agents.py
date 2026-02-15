import pickle
import os
import hashlib
from datetime import datetime

# -----------------------------------
# LOAD ML MODEL & VECTORIZER
# -----------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

model = pickle.load(open(os.path.join(BASE_DIR, "model/model.pkl"), "rb"))
vectorizer = pickle.load(open(os.path.join(BASE_DIR, "model/vectorizer.pkl"), "rb"))


# -----------------------------------
# AGENT 1 — INPUT AGENT
# -----------------------------------
def input_agent(text):
    return text.strip().lower()


# -----------------------------------
# AGENT 2 — PREPROCESS AGENT
# -----------------------------------
def preprocess_agent(text):
    return text


# -----------------------------------
# AGENT 3 — CLASSIFIER AGENT
# -----------------------------------
def classifier_agent(text):

    vec = vectorizer.transform([text])
    probs = model.predict_proba(vec)[0]
    labels = model.classes_

    prediction = labels[probs.argmax()]
    confidence = probs.max()

    # 🔥 CRITICAL FIX
    prediction = prediction.strip().upper()

    return prediction, confidence


# -----------------------------------
# AGENT 4 — SEVERITY AGENT
# -----------------------------------
def severity_agent(prediction, confidence):

    base_scores = {
        "HATE-SPEECH": 90,
        "CYBERBULLYING": 75,
        "ABUSIVE": 55,
        "NORMAL": 0
    }

    base = base_scores.get(prediction, 0)

    severity_score = int(base * confidence)

    return severity_score


# -----------------------------------
# AGENT 5 — EXPLAINABILITY AGENT
# -----------------------------------
def explainability_agent(prediction):

    explanations = {
        "HATE-SPEECH": "Targets a protected group or promotes hate.",
        "CYBERBULLYING": "Harassment or personal attack detected.",
        "ABUSIVE": "Offensive or toxic language detected.",
        "NORMAL": "No harmful intent detected."
    }

    # 🔥 SAFETY FALLBACK
    return explanations.get(prediction, "No explanation available.")


# -----------------------------------
# AGENT 6 — FORENSIC AGENT
# -----------------------------------
def forensic_agent(text):

    hash_value = hashlib.sha256(text.encode()).hexdigest()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return hash_value, timestamp
