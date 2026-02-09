from django.http import JsonResponse
from datetime import datetime
import pickle, os, hashlib
from django.views.decorators.csrf import csrf_exempt
from .models import DetectionLog

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

model = pickle.load(open(os.path.join(BASE_DIR, "model/model.pkl"), "rb"))
vectorizer = pickle.load(open(os.path.join(BASE_DIR, "model/vectorizer.pkl"), "rb"))


@csrf_exempt
def predict(request):

    if request.method == "GET":
        text = request.GET.get("text")
    else:
        text = request.POST.get("text")

    if not text:
        return JsonResponse({"error": "No text provided"})

    text_lower = text.lower()

    # =============================
    # ✅ POSITIVE WHITELIST
    # =============================
    positive_phrases = [
        "i love", "you are beautiful", "you are pretty",
        "great job", "well done", "nice work",
        "amazing", "awesome", "fantastic"
    ]

    for p in positive_phrases:
        if p in text_lower:
            return JsonResponse({
                "text": text,
                "prediction": "NORMAL"
            })

    # =============================
    # 🔥 HATE SPEECH
    # =============================
    hate_groups = [
        "all men", "all women", "all americans", "all foreigners",
        "all muslims", "all hindus", "all christians",
        "all blacks", "all whites", "all gays", "all lesbians"
    ]

    for group in hate_groups:
        if group in text_lower:
            prediction = "HATE_SPEECH"
            break
    else:

        # =============================
        # 🟠 ABUSIVE LANGUAGE
        # =============================
        abusive_words = [
            "bitch", "fuck", "shit", "asshole", "bastard",
            "slut", "whore", "moron", "idiot", "stupid"
        ]

        for word in abusive_words:
            if word in text_lower:
                prediction = "ABUSIVE"
                break
        else:

            # =============================
            # 🤖 ML FALLBACK
            # =============================
            vec = vectorizer.transform([text])
            prediction = model.predict(vec)[0]

    # =============================
    # ✅ NORMAL
    # =============================
    if prediction == "NORMAL":
        return JsonResponse({
            "text": text,
            "prediction": prediction
        })

    # =============================
    # 🔐 FORENSIC LOGGING
    # =============================
    hash_value = hashlib.sha256(text.encode()).hexdigest()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    DetectionLog.objects.create(
        text=text,
        prediction=prediction,
        hash_value=hash_value
    )

    return JsonResponse({
        "text": text,
        "prediction": prediction,
        "hash": hash_value,
        "timestamp": timestamp
    })
