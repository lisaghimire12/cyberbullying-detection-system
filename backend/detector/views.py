from django.http import JsonResponse
from datetime import datetime
import pickle, os, hashlib
from .models import DetectionLog
from django.views.decorators.csrf import csrf_exempt

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

    text_vec = vectorizer.transform([text])
    prediction = model.predict(text_vec)[0]

    # ✅ NORMAL messages → no forensic logging
    if prediction == "NORMAL":
        return JsonResponse({
            "text": text,
            "prediction": prediction
        })

    # 🔐 Harmful content → generate evidence
    hash_value = hashlib.sha256(text.encode()).hexdigest()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    DetectionLog.objects.create(
    text=text,
    prediction=prediction,
    hash_value=hash_value
    )


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
