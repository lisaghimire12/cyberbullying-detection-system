from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from .link_agents import detect_link_type, fetch_youtube_comments

from .agents import (
    preprocess_agent,
    classifier_agent,
    severity_agent,
    explainability_agent,
    forensic_agent
)

# --------------------------------
# HOME PAGE
# --------------------------------
def home(request):
    return render(request, "index.html")

# --------------------------------
# YOUTUBE LINK ANALYSIS
# --------------------------------
@csrf_exempt
def analyze_link(request):

    url = request.GET.get("url", "").strip()

    if url == "":
        return JsonResponse({"error": "No URL provided"})

    if detect_link_type(url) != "youtube":
        return JsonResponse({"error": "Only YouTube links supported"})

    comments = fetch_youtube_comments(url)

    results = []

    # -------- DASHBOARD COUNTERS --------
    total_comments = 0
    normal = 0
    abusive = 0
    cyberbullying = 0
    hate_speech = 0

    # -----------------------------------
    for text in comments:

        total_comments += 1

        clean = preprocess_agent(text)
        prediction, confidence = classifier_agent(clean)

        severity_score = severity_agent(prediction, confidence)
        explanation = explainability_agent(prediction)

        # ---------- RISK LEVEL ----------
        if severity_score >= 80:
            risk = "CRITICAL"
        elif severity_score >= 60:
            risk = "HIGH"
        elif severity_score >= 40:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        # ---------- NORMAL ----------
        if prediction == "NORMAL":

            normal += 1

            results.append({
                "text": text,
                "prediction": prediction,
                "confidence": round(confidence,2),
                "severity_score": severity_score,
                "risk_level": risk,
                "explanation": explanation
            })

        # ---------- HARMFUL ----------
        else:

            if prediction == "ABUSIVE":
                abusive += 1
            elif prediction == "CYBERBULLYING":
                cyberbullying += 1
            elif prediction == "HATE-SPEECH":
                hate_speech += 1

            hash_value, timestamp = forensic_agent(clean)

            results.append({
                "text": text,
                "prediction": prediction,
                "confidence": round(confidence,2),
                "severity_score": severity_score,
                "risk_level": risk,
                "explanation": explanation,
                "hash": hash_value,
                "timestamp": timestamp
            })

    summary = {
        "total_comments": total_comments,
        "normal": normal,
        "abusive": abusive,
        "cyberbullying": cyberbullying,
        "hate_speech": hate_speech,
        "total_flagged": abusive + cyberbullying + hate_speech
    }

    return JsonResponse({
        "summary": summary,
        "results": results
    })
