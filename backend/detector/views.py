from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from .link_agents import detect_link_type, fetch_youtube_comments
import io


from .agents import (
    preprocess_agent,
    classifier_agent,
    severity_agent,
    explainability_agent,
    forensic_agent,
    victim_targeting_agent,
    escalation_risk_agent,
    harassment_density_agent
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

        # 🔥 NEW AGENTIC METRICS
        vti = victim_targeting_agent(text)
        ers = escalation_risk_agent(confidence, severity_score)

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
                "explanation": explanation,
                "vti": vti,
                "ers": ers
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
                "timestamp": timestamp,
                "vti": vti,
                "ers": ers
            })

    # 🔥 HARASSMENT DENSITY SCORE
    harmful_total = abusive + cyberbullying + hate_speech
    hds = harassment_density_agent(total_comments, harmful_total)

    summary = {
        "total_comments": total_comments,
        "normal": normal,
        "abusive": abusive,
        "cyberbullying": cyberbullying,
        "hate_speech": hate_speech,
        "total_flagged": harmful_total,
        "harassment_density": hds
    }

    return JsonResponse({
        "summary": summary,
        "results": results
    })


@csrf_exempt
def download_report(request):

    url = request.GET.get("url", "")

    comments = fetch_youtube_comments(url)

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 40

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, y, "Agentic AI Content Moderation Evidence Report")
    y -= 30

    pdf.setFont("Helvetica", 10)
    pdf.drawString(40, y, f"Video URL: {url}")
    y -= 20

    for text in comments:

        clean = preprocess_agent(text)
        prediction, confidence = classifier_agent(clean)

        if prediction == "NORMAL":
            continue

        severity = severity_agent(prediction, confidence)
        ers = escalation_risk_agent(confidence, severity)
        vti = victim_targeting_agent(text)
        hash_value, timestamp = forensic_agent(clean)

        pdf.drawString(40, y, f"Comment: {text[:120]}")
        y -= 14
        pdf.drawString(40, y, f"Prediction: {prediction}")
        y -= 14
        pdf.drawString(40, y, f"Severity: {severity}")
        y -= 14
        pdf.drawString(40, y, f"Victim Targeting Index: {vti}")
        y -= 14
        pdf.drawString(40, y, f"Escalation Risk Score: {ers}")
        y -= 14
        pdf.drawString(40, y, f"Hash: {hash_value}")
        y -= 14
        pdf.drawString(40, y, f"Time: {timestamp}")
        y -= 25

        if y < 100:
            pdf.showPage()
            y = height - 40

    pdf.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=forensic_report.pdf"

    return response