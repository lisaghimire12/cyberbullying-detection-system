from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

import matplotlib.pyplot as plt

from .link_agents import detect_link_type, fetch_youtube_comments

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

import io
import logging
import time

logger = logging.getLogger(__name__)


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

    logger.info("\n=========== NEW ANALYSIS REQUEST ===========")
    logger.info(f"[SYSTEM] Fetching comments from: {url}")

    comments = fetch_youtube_comments(url)

    results = []

    # -------- DASHBOARD COUNTERS --------
    total_comments = 0
    normal = 0
    abusive = 0
    cyberbullying = 0
    hate_speech = 0

    # -------- GRAPH DATA --------
    processing_times = []
    comment_indices = []

    # -----------------------------------
    # AGENTIC AI PIPELINE
    # -----------------------------------
    for idx, text in enumerate(comments, start=1):

        logger.info("\n========== NEW COMMENT ==========")
        logger.info(f"[COMMENT {idx}] {text[:80]}")

        start_time = time.time()

        total_comments += 1

        # INPUT
        logger.info("[INPUT AGENT] Receiving text")

        # PREPROCESS
        clean = preprocess_agent(text)
        logger.info("[PREPROCESS AGENT] Text cleaned")

        # CLASSIFICATION
        prediction, confidence = classifier_agent(clean)
        logger.info(
            f"[CLASSIFIER AGENT] Prediction={prediction} | Confidence={confidence:.2f}"
        )

        # SEVERITY
        severity_score = severity_agent(prediction, confidence)
        logger.info(f"[SEVERITY AGENT] Score={severity_score}")

        explanation = explainability_agent(prediction)

        # NEW AGENTIC METRICS
        vti = victim_targeting_agent(text)
        logger.info(f"[VTI AGENT] Index={vti}")

        ers = escalation_risk_agent(confidence, severity_score)
        logger.info(f"[ERS AGENT] Score={ers}")

        # RISK LEVEL
        if severity_score >= 80:
            risk = "CRITICAL"
        elif severity_score >= 60:
            risk = "HIGH"
        elif severity_score >= 40:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        logger.info(f"[RISK LEVEL] {risk}")

        # NORMAL
        if prediction == "NORMAL":

            normal += 1

            results.append({
                "text": text,
                "prediction": prediction,
                "confidence": round(confidence, 2),
                "severity_score": severity_score,
                "risk_level": risk,
                "explanation": explanation,
                "vti": vti,
                "ers": ers
            })

        # HARMFUL
        else:

            if prediction == "ABUSIVE":
                abusive += 1
            elif prediction == "CYBERBULLYING":
                cyberbullying += 1
            elif prediction == "HATE-SPEECH":
                hate_speech += 1

            hash_value, timestamp = forensic_agent(clean)
            logger.info("[FORENSIC AGENT] Evidence generated")

            results.append({
                "text": text,
                "prediction": prediction,
                "confidence": round(confidence, 2),
                "severity_score": severity_score,
                "risk_level": risk,
                "explanation": explanation,
                "hash": hash_value,
                "timestamp": timestamp,
                "vti": vti,
                "ers": ers
            })

        # PROCESSING TIME
        end_time = time.time()
        processing_times.append(end_time - start_time)
        comment_indices.append(idx)

        logger.info("=================================")

    # --------------------------------
    # HARASSMENT DENSITY SCORE
    # --------------------------------
    harmful_total = abusive + cyberbullying + hate_speech
    hds = harassment_density_agent(total_comments, harmful_total)

    logger.info("\n========== VIDEO SUMMARY ==========")
    logger.info(f"Total Comments: {total_comments}")
    logger.info(f"Harmful Comments: {harmful_total}")
    logger.info(f"Harassment Density Score: {hds}%")
    logger.info("===================================")

    summary = {
        "total_comments": total_comments,
        "normal": normal,
        "abusive": abusive,
        "cyberbullying": cyberbullying,
        "hate_speech": hate_speech,
        "total_flagged": harmful_total,
        "harassment_density": hds
    }

    # --------------------------------
    # BACKEND GRAPH GENERATION
    # --------------------------------
    plt.figure(figsize=(8,4))

    plt.plot(comment_indices, processing_times, marker='o')

    plt.title("Backend Processing Time per Comment")
    plt.xlabel("Comment Number")
    plt.ylabel("Processing Time (seconds)")

    plt.grid(True)

    plt.savefig("processing_graph.png")

    logger.info("Backend graph generated: processing_graph.png")

    return JsonResponse({
        "summary": summary,
        "results": results
    })


# --------------------------------
# DOWNLOAD PDF REPORT
# --------------------------------
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
        vti = victim_targeting_agent(text)
        ers = escalation_risk_agent(confidence, severity)
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

