from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import pickle, os, hashlib, re
import subprocess
from datetime import datetime
from .models import DetectionLog

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

model = pickle.load(open(os.path.join(BASE_DIR, "model/model.pkl"), "rb"))
vectorizer = pickle.load(open(os.path.join(BASE_DIR, "model/vectorizer.pkl"), "rb"))

# --------------------
# SAFE GREETINGS
# --------------------
SAFE_WORDS = [
    "hi", "hello", "hey", "hii", "hola", "good morning",
    "good evening", "how are you", "wassup", "sup"
]

# --------------------
# STRONG RULE LISTS
# --------------------
HATE_PHRASES = [
    "should die",
    "kill yourself",
    "go die",
    "all indians should die"
]

ABUSIVE_WORDS = [
    "pagal",
    "idiot",
    "stupid",
    "bitch",
    "loser",
    "asshole",
    "bastard"
]

# --------------------

def start_packet_capture():
    try:
        subprocess.Popen(#tcp.port == 8000
            ["tshark", "-i", r"\Device\NPF_{8EEFC699-F111-4ECE-B9D8-61E03A3F7AAD}", "-c", "5"],#tshark -D
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )#adapter for lookback traffic capture
    except:
        pass



@csrf_exempt
def predict(request):
    start_packet_capture()

    text = request.GET.get("text", "").lower().strip()

    if text == "":
        return JsonResponse({"prediction": "NORMAL"})

    # -----------------------------------
    # 1️⃣ WHITELIST GREETINGS FIRST
    # -----------------------------------
    for w in SAFE_WORDS:
        if text == w or text.startswith(w + " "):
            return JsonResponse({
                "prediction": "NORMAL",
                "confidence": 1.0
            })

    # -----------------------------------
    # 2️⃣ HATE SPEECH (RULE)
    # -----------------------------------
    for phrase in HATE_PHRASES:
        if phrase in text:
            return block(text, "HATE-SPEECH")

    # -----------------------------------
    # 3️⃣ ABUSIVE WORDS (FULL WORD MATCH)
    # -----------------------------------
    for word in ABUSIVE_WORDS:
        if re.search(rf"\b{word}\b", text):
            return block(text, "ABUSIVE")

    # -----------------------------------
    # 4️⃣ ML MODEL
    # -----------------------------------
    vec = vectorizer.transform([text])
    probs = model.predict_proba(vec)[0]
    labels = model.classes_

    pred = labels[probs.argmax()].upper().strip()
    conf = probs.max()

    if pred == "NORMAL":
        return JsonResponse({
            "prediction": "NORMAL",
            "confidence": round(conf, 2)
        })

    return block(text, pred)


def block(text, label):
    h = hashlib.sha256(text.encode()).hexdigest()
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    DetectionLog.objects.create(
        text=text,
        prediction=label,
        hash_value=h
    )

    return JsonResponse({
        "prediction": label,
        "hash": h,
        "timestamp": time
    })
