"""Lap 6 · Information extraction with Azure Content Understanding (a Foundry Tool).
Works on documents, images, audio and video. This script sends a file to an analyzer and prints the fields.

Run:  python extract_info.py prebuilt-invoice service-invoice.pdf
      python extract_info.py velocityWindowSticker window-sticker.png
      python extract_info.py prebuilt-audio teaser.mp3
Needs: pip install requests
Env:   FOUNDRY_ENDPOINT_AI (https://<resource>.services.ai.azure.com)   AI_KEY
"""
import os, sys, time, mimetypes, requests

analyzer, path = (sys.argv + ["prebuilt-invoice", "service-invoice.pdf"])[1:3]
base = os.environ["FOUNDRY_ENDPOINT_AI"].rstrip("/") + "/contentunderstanding"
ver = "api-version=2025-11-01"
headers = {"Ocp-Apim-Subscription-Key": os.environ["AI_KEY"]}
ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"

# 1) Start the analysis (long-running operation → 202 + Operation-Location)
r = requests.post(f"{base}/analyzers/{analyzer}:analyzeBinary?{ver}", headers={**headers, "Content-Type": ctype}, data=open(path, "rb").read())
r.raise_for_status()
op = r.headers["Operation-Location"]
print(f"submitted {path} to {analyzer} …", end="", flush=True)

# 2) Poll until it finishes
while True:
    time.sleep(3); result = requests.get(op, headers=headers).json()
    print(".", end="", flush=True)
    if result["status"].lower() in ("succeeded", "failed"): break
print(" " + result["status"])
if result["status"].lower() == "failed": sys.exit(result.get("error"))

# 3) Read the results: every content item has markdown, and (for field analyzers) typed fields
def value(f):
    for k in ("valueString", "valueNumber", "valueInteger", "valueBoolean", "valueDate"):
        if k in f: return f[k]
    if "valueArray" in f: return [value(i) for i in f["valueArray"]]
    if "valueObject" in f: return {k: value(v) for k, v in f["valueObject"].items()}
    return f.get("content")

for content in result["result"]["contents"]:
    span = f" {content['startTimeMs']/1000:.1f}s→{content['endTimeMs']/1000:.1f}s" if "startTimeMs" in content else ""
    print(f"\n── {content.get('kind', 'content')}{span} ──")
    for name, field in content.get("fields", {}).items():
        conf = f"  (confidence {field['confidence']:.2f})" if field.get("confidence") is not None else ""
        print(f"  {name:20s} {value(field)!s:.110}{conf}")
    if not content.get("fields"):
        print("  markdown:", content.get("markdown", "")[:600].replace("\n", "\n            "))
