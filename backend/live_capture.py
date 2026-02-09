import subprocess
import requests
import re

DJANGO_API = "http://127.0.0.1:8000/api/predict/"

print("🔴 Real-Time Packet Capture Started...")

command = [
    "tshark",
    "-l",
    "-Y", "http",
    "-T", "fields",
    "-e", "http.file_data"
]

process = subprocess.Popen(
    command,
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    text=True
)

for line in process.stdout:
    text = line.strip()

    if len(text) > 5:
        clean = re.sub(r"[^a-zA-Z0-9 .,!?']", "", text)

        try:
            requests.get(DJANGO_API, params={"text": clean})
            print("Captured:", clean)
        except:
            pass
