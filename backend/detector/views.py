from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from .link_agents import (
    detect_link_type,
    fetch_youtube_comments,
    fetch_ecommerce_reviews
)

from .agents import (
    input_agent,
    preprocess_agent,
    classifier_agent,
    forensic_agent
)


# -------------------------
# HOME PAGE
# -------------------------
def home(request):
    return render(request, "index.html")


# -------------------------
# TEXT ANALYSIS (Agent Pipeline)
# -------------------------
@csrf_exempt
def predict(request):

    text = request.GET.get("text", "")

    # AGENT 1 → Input Agent
    raw_text = input_agent(text)

    if raw_text == "":
        return JsonResponse({"prediction": "NORMAL"})

    # AGENT 2 → Preprocess Agent
    clean_text = preprocess_agent(raw_text)

    # AGENT 3 → Classifier Agent
    prediction, confidence = classifier_agent(clean_text)

    if prediction == "NORMAL":
        return JsonResponse({
            "prediction": "NORMAL",
            "confidence": confidence
        })

    # AGENT 4 → Forensic Agent
    hash_value, timestamp = forensic_agent(clean_text, prediction)

    return JsonResponse({
        "prediction": prediction,
        "hash": hash_value,
        "timestamp": timestamp
    })


# -------------------------
# LINK ANALYSIS (Agentic Flow)
# -------------------------
@csrf_exempt
def analyze_link(request):

    url = request.GET.get("url", "")

    if url == "":
        return JsonResponse({"error": "No URL provided"})

    link_type = detect_link_type(url)

    if link_type == "youtube":
        texts = fetch_youtube_comments(url)

    elif link_type == "ecommerce":
        texts = fetch_ecommerce_reviews(url)

    else:
        return JsonResponse({"error": "Unsupported link type"})

    results = []

    for text in texts:

        clean_text = preprocess_agent(text)
        prediction, confidence = classifier_agent(clean_text)

        if prediction == "NORMAL":
            results.append({
                "text": text,
                "prediction": prediction,
                "confidence": confidence
            })
        else:
            hash_value, timestamp = forensic_agent(clean_text, prediction)

            results.append({
                "text": text,
                "prediction": prediction,
                "confidence": confidence,
                "hash": hash_value,
                "timestamp": timestamp
            })


    return JsonResponse({"results": results})
