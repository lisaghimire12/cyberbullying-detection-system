# backend/detector/agents.py

import re
import pickle, os, hashlib
from datetime import datetime
from .models import DetectionLog

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

model = pickle.load(open(os.path.join(BASE_DIR, "model/model.pkl"), "rb"))
vectorizer = pickle.load(open(os.path.join(BASE_DIR, "model/vectorizer.pkl"), "rb"))


# -------------------------
# AGENT 1 - INPUT AGENT
# -------------------------
def input_agent(text):
    return text.strip()


# -------------------------
# AGENT 2 - PREPROCESS AGENT
# -------------------------
def preprocess_agent(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9 .,!?']", "", text)
    return text


# -------------------------
# AGENT 3 - CLASSIFIER AGENT
# -------------------------
def classifier_agent(text):
    vec = vectorizer.transform([text])
    probs = model.predict_proba(vec)[0]
    labels = model.classes_

    pred = labels[probs.argmax()]
    conf = round(probs.max(), 2)

    return pred, conf


# -------------------------
# AGENT 4 - FORENSIC AGENT
# -------------------------
def forensic_agent(text, label):
    h = hashlib.sha256(text.encode()).hexdigest()
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    DetectionLog.objects.create(
        text=text,
        prediction=label,
        hash_value=h
    )

    return h, time
