#!/usr/bin/env python3
"""Copy screenshots, photos, generated images, documents and media from the scratchpad into the site tree (web-optimised)."""
import os, shutil, glob, json
from PIL import Image
SP="/private/tmp/claude-501/-Users-varoonsahgal-az901/85ba462c-e83a-4cf4-9e18-19dd77e0eb0b/scratchpad"; ROOT=os.path.dirname(os.path.abspath(__file__))
def ensure(p): os.makedirs(p, exist_ok=True); return p
def jpg(src, dst, maxw=1400, q=86):
    im=Image.open(src).convert("RGB"); 
    if im.width>maxw: im.thumbnail((maxw, maxw*4))
    im.save(dst, "JPEG", quality=q, optimize=True, progressive=True)
# screenshots (PNG, keep crisp)
d=ensure(f"{ROOT}/images/shots")
for f in glob.glob(f"{SP}/shots/lab*.png"): shutil.copy(f, d)
# photos
d=ensure(f"{ROOT}/images/photos")
for f in glob.glob(f"{SP}/photos/*.jpg"): shutil.copy(f, d)
# vision visualisations -> jpg
d=ensure(f"{ROOT}/images/vision")
for f in glob.glob(f"{SP}/results/vision/viz/*.png"): jpg(f, f"{d}/{os.path.basename(f)[:-4]}.jpg")
# generated images -> jpg
d=ensure(f"{ROOT}/images/gen")
for f in glob.glob(f"{SP}/results/images/*.png"): jpg(f, f"{d}/{os.path.basename(f)[:-4]}.jpg", 1200, 88)
# charts
d=ensure(f"{ROOT}/images/charts")
for f in glob.glob(f"{SP}/charts/*.png"): shutil.copy(f, d)
# documents (images + downloads)
d=ensure(f"{ROOT}/images/docs"); dl=ensure(f"{ROOT}/downloads")
for n in ["window-sticker.png","vin-plate.png","service-note.png","service-invoice.png"]: shutil.copy(f"{SP}/docs/{n}", d); shutil.copy(f"{SP}/docs/{n}", dl)
for n in ["service-invoice.pdf","velocity-warranty-guide.md","velocity-teaser.mp4"]: shutil.copy(f"{SP}/docs/{n}", dl)
for n in ["velocity_used_cars.csv","velocity_leads.csv","velocity_owners.csv"]: shutil.copy(f"{SP}/data/{n}", dl)
# media
m=ensure(f"{ROOT}/media")
for n in ["velo-ava.mp3","velo-andrew-multilingual.mp3","user-brake-question.wav","velo-audio-reply.wav","pipeline-answer.wav"]:
    if os.path.exists(f"{SP}/results/speech/{n}"): shutil.copy(f"{SP}/results/speech/{n}", m)
shutil.copy(f"{SP}/results/speech/user-brake-question.wav", f"{dl}/question.wav")
# sample photos for download (zip)
import zipfile
with zipfile.ZipFile(f"{dl}/lot-photos.zip","w",zipfile.ZIP_DEFLATED) as z:
    for f in glob.glob(f"{SP}/photos/*.jpg"): z.write(f, os.path.basename(f))
    z.write(f"{SP}/photos/credits.json","credits.json")
# scripts zip
with zipfile.ZipFile(f"{dl}/pit-crew-scripts.zip","w",zipfile.ZIP_DEFLATED) as z:
    for f in glob.glob(f"{ROOT}/pit-crew/*.py"): z.write(f, "pit-crew/"+os.path.basename(f))
# results JSON for the curious
r=ensure(f"{ROOT}/downloads/results")
for f in ["results/vision/suv-volvo-xc90.json","results/vision/traffic-auckland.json","results/language/all.json","results/translator/all.json","results/safety/all.json","results/openai/all.json","results/agents/agents.json","results/docs/docintel-invoice.json","results/docs/ocr-window-sticker.json","results/speech/stt.json","results/speech/audio-model.json"]:
    if os.path.exists(f"{SP}/{f}"): shutil.copy(f"{SP}/{f}", f"{r}/{f.split('/')[1]}-{os.path.basename(f)}")
for f in glob.glob(f"{SP}/results/cu/*.json"): shutil.copy(f, f"{r}/cu-{os.path.basename(f)}")
tot=sum(os.path.getsize(os.path.join(dp,f)) for dp,_,fs in os.walk(ROOT) for f in fs if ".git" not in dp)
print("synced; site tree is", tot//1024//1024, "MB;", len(os.listdir(f"{ROOT}/images/shots")), "shots")
