"""Lap 4 · Text analysis with Azure AI Language (a Foundry Tool).

Run:  python text_analysis.py
Needs: pip install azure-ai-textanalytics
Env:   FOUNDRY_ENDPOINT  (https://<resource>.cognitiveservices.azure.com)   AI_KEY
"""
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

client = TextAnalyticsClient(endpoint=os.environ["FOUNDRY_ENDPOINT"], credential=AzureKeyCredential(os.environ["AI_KEY"]))

reviews = [
    "Absolutely love my new Velocity Summit. The hybrid engine is whisper quiet, but the infotainment system crashed twice in the first week.",
    "Terrible experience at the Dayton dealership. I waited three hours for an oil change. Nobody apologized.",
    "Picked up a certified pre-owned Velocity Strata for $21,400 last month. Great value. Priya, the service advisor, was fantastic.",
]

print("── Language detection ──")
for d in client.detect_language(reviews):
    print(f"  {d.primary_language.name} ({d.primary_language.confidence_score:.2f})")

print("\n── Sentiment + opinion mining ──")
for r in client.analyze_sentiment(reviews, show_opinion_mining=True):
    s = r.confidence_scores
    print(f"  {r.sentiment:9s} pos={s.positive:.2f} neu={s.neutral:.2f} neg={s.negative:.2f}")
    for sent in r.sentences:
        for op in sent.mined_opinions:
            print(f"      ↳ target '{op.target.text}' is {op.target.sentiment}: " + ", ".join(a.text for a in op.assessments))

print("\n── Key phrases ──")
for r in client.extract_key_phrases(reviews):
    print("  " + " · ".join(r.key_phrases))

print("\n── Entities ──")
for r in client.recognize_entities(reviews):
    print("  " + ", ".join(f"{e.text} [{e.category}]" for e in r.entities))

print("\n── PII (what we must redact before storing) ──")
ticket = ["Customer Marcus Alvarez (614-555-0188, marcus.alvarez@example.com) reports a grinding noise. VIN 1VMSUM7K2NA048213. Card ending 4421."]
for r in client.recognize_pii_entities(ticket):
    print("  found:", ", ".join(f"{e.text} [{e.category}]" for e in r.entities))
    print("  redacted:", r.redacted_text)
