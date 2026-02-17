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


# -----------------------------------
# AGENT 7 — VICTIM TARGETING AGENT (VTI)
# -----------------------------------
def victim_targeting_agent(text):

    targeting_words = ["you", "your", "u", "ur", "he", "she", "they", "him", "her"]
    count = sum(1 for w in targeting_words if w in text.lower())

    score = min(count / 5, 1)  # normalize 0 → 1

    return round(score, 2)


# -----------------------------------
# AGENT 8 — ESCALATION RISK AGENT (ERS)
# -----------------------------------
def escalation_risk_agent(confidence, severity):

    ers = (confidence * 50) + (severity * 0.5)

    return round(ers, 2)


# -----------------------------------
# AGENT 9 — HARASSMENT DENSITY AGENT (HDS)
# -----------------------------------
def harassment_density_agent(total_comments, harmful_comments):

    if total_comments == 0:
        return 0

    return round((harmful_comments / total_comments) * 100, 2)

