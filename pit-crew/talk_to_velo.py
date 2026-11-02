"""Lap 4 · Respond to a SPOKEN prompt with a multimodal audio model (gpt-audio-mini).
One model hears the question and speaks the answer — no separate speech-to-text step.

Run:  python talk_to_velo.py question.wav reply.wav
Needs: pip install openai
Env:   AOAI_ENDPOINT (https://<resource>.openai.azure.com)  AI_KEY  AUDIO_MODEL (default gpt-audio-mini)
"""
import os, sys, base64
from openai import AzureOpenAI

in_wav, out_wav = (sys.argv + ["question.wav", "reply.wav"])[1:3]
client = AzureOpenAI(azure_endpoint=os.environ["AOAI_ENDPOINT"], api_key=os.environ["AI_KEY"], api_version="2025-01-01-preview")

r = client.chat.completions.create(
    model=os.environ.get("AUDIO_MODEL", "gpt-audio-mini"),
    modalities=["text", "audio"], audio={"voice": "alloy", "format": "wav"},
    messages=[
        {"role": "system", "content": "You are Velo, the in-car assistant for Velocity Motors. Safety first, then one or two short steps. Under 50 words."},
        {"role": "user", "content": [{"type": "input_audio", "input_audio": {"data": base64.b64encode(open(in_wav, "rb").read()).decode(), "format": "wav"}}]}])

msg = r.choices[0].message
open(out_wav, "wb").write(base64.b64decode(msg.audio.data))
print("Velo said:", msg.audio.transcript)
print(f"saved {out_wav} · tokens: {r.usage.prompt_tokens_details.audio_tokens} audio in, {r.usage.completion_tokens_details.audio_tokens} audio out")
