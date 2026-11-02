"""Lap 5 · Vision two ways: Azure AI Vision (Foundry Tool) and a multimodal GPT model.

Run:  python vision_app.py photo.jpg
Needs: pip install azure-ai-vision-imageanalysis openai azure-identity azure-ai-projects
Env:   FOUNDRY_ENDPOINT (https://<resource>.cognitiveservices.azure.com)  AI_KEY  PROJECT_ENDPOINT  CHAT_MODEL
"""
import os, sys, base64
from azure.core.credentials import AzureKeyCredential
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

path = sys.argv[1] if len(sys.argv) > 1 else "photo.jpg"
image = open(path, "rb").read()

# 1) Azure AI Vision: fast, cheap, structured — captions, objects with boxes, OCR
vision = ImageAnalysisClient(endpoint=os.environ["FOUNDRY_ENDPOINT"], credential=AzureKeyCredential(os.environ["AI_KEY"]))
res = vision.analyze(image_data=image, visual_features=[VisualFeatures.CAPTION, VisualFeatures.OBJECTS, VisualFeatures.READ, VisualFeatures.TAGS], gender_neutral_caption=True)
print(f"── Azure AI Vision on {path} ──")
print(f"  caption : “{res.caption.text}” ({res.caption.confidence:.2f})")
print("  objects :", ", ".join(f"{o.tags[0].name} {o.tags[0].confidence:.2f} @ {o.bounding_box}" for o in res.objects.list) or "none")
print("  tags    :", ", ".join(t.name for t in res.tags.list[:10]))
if res.read and res.read.blocks:
    print("  text    :", " | ".join(line.text for b in res.read.blocks for line in b.lines))

# 2) A multimodal model: slower, costs tokens, but it can reason about what it sees
project = AIProjectClient(endpoint=os.environ["PROJECT_ENDPOINT"], credential=DefaultAzureCredential())
client = project.get_openai_client()
b64 = base64.b64encode(image).decode()
r = client.chat.completions.create(model=os.environ.get("CHAT_MODEL", "gpt-4-1-mini"), max_tokens=250, messages=[
    {"role": "system", "content": "You are a Velocity Motors used-car appraiser."},
    {"role": "user", "content": [
        {"type": "text", "text": "Describe this vehicle for a listing (body style, color, condition clues) in 3 bullets, then suggest one thing to inspect."},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}", "detail": "low"}}]}])
print(f"\n── {r.model} (multimodal) ──\n" + r.choices[0].message.content)
print(f"  [{r.usage.prompt_tokens} prompt tokens incl. the image]")
