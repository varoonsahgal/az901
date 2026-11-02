"""Lap 5 · Generate an image with a Foundry image model (FLUX.2-pro, FLUX-1.1-pro, gpt-image-1-mini, ...).

Run:  python make_image.py "prompt text" out.png
Needs: pip install requests
Env:   FOUNDRY_ENDPOINT_AI (https://<resource>.services.ai.azure.com)   AI_KEY   IMAGE_MODEL (deployment name, default flux-2-pro)
Note:  a capacity-1 deployment allows about one request per minute; a 429 means wait 60 seconds and retry.
"""
import os, sys, base64, requests

prompt = sys.argv[1] if len(sys.argv) > 1 else "A sleek Velocity Volt electric sedan on a wet racetrack at golden hour, photorealistic"
out = sys.argv[2] if len(sys.argv) > 2 else "out.png"
model = os.environ.get("IMAGE_MODEL", "flux-2-pro")

url = f"{os.environ['FOUNDRY_ENDPOINT_AI'].rstrip('/')}/openai/deployments/{model}/images/generations?api-version=2025-04-01-preview"
r = requests.post(url, headers={"api-key": os.environ["AI_KEY"], "Content-Type": "application/json"},
                  json={"prompt": prompt, "n": 1, "size": "1024x768", "output_format": "png"}, timeout=180)
if r.status_code == 429:
    sys.exit("429: the deployment's rate limit (about one image per minute at capacity 1) — wait a minute and try again")
r.raise_for_status()
open(out, "wb").write(base64.b64decode(r.json()["data"][0]["b64_json"]))
print(f"saved {out} ({os.path.getsize(out)//1024} KB) · model {model} · prompt: {prompt!r}")
