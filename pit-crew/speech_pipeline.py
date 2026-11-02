"""Lap 4 · Speech in → model → speech out, with Azure Speech (a Foundry Tool).

Run:  python speech_pipeline.py question.wav answer.wav
Needs: pip install azure-cognitiveservices-speech openai azure-identity azure-ai-projects
Env:   AI_KEY  SPEECH_REGION (e.g. eastus2)  PROJECT_ENDPOINT  CHAT_MODEL
Works in Cloud Shell because it reads and writes .wav files instead of using a microphone.
"""
import os, sys
import azure.cognitiveservices.speech as speechsdk
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

in_wav, out_wav = (sys.argv + ["question.wav", "answer.wav"])[1:3]
speech = speechsdk.SpeechConfig(subscription=os.environ["AI_KEY"], region=os.environ["SPEECH_REGION"])

# 1) Speech recognition (speech-to-text)
rec = speechsdk.SpeechRecognizer(speech_config=speech, audio_config=speechsdk.audio.AudioConfig(filename=in_wav))
heard = rec.recognize_once()
print(f"heard   : {heard.text!r}  ({heard.reason.name})")

# 2) Ask the model
project = AIProjectClient(endpoint=os.environ["PROJECT_ENDPOINT"], credential=DefaultAzureCredential())
r = project.get_openai_client().chat.completions.create(model=os.environ.get("CHAT_MODEL", "gpt-4-1-mini"), max_tokens=120, messages=[
    {"role": "system", "content": "You are Velo, the in-car assistant for Velocity Motors. Safety first. Reply in under 40 spoken-friendly words."},
    {"role": "user", "content": heard.text}])
answer = r.choices[0].message.content
print(f"answer  : {answer}")

# 3) Speech synthesis (text-to-speech) with a neural voice
speech.speech_synthesis_voice_name = "en-US-AvaMultilingualNeural"
synth = speechsdk.SpeechSynthesizer(speech_config=speech, audio_config=speechsdk.audio.AudioOutputConfig(filename=out_wav))
result = synth.speak_text_async(answer).get()
print(f"spoken  : {out_wav} ({len(result.audio_data)//1024} KB, {result.reason.name})")
