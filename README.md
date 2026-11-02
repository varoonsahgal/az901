# AI-901 Grand Prix · one day, eight laps, Microsoft Foundry

A hands-on, car-themed one-day course for **Microsoft exam AI-901 (Azure AI Fundamentals)**, built for a fictional car company, Velocity Motors, and for twenty students working in one shared Azure subscription.

**Site:** https://varoonsahgal.github.io/az901/

| Lap | Title | Covers |
|---|---|---|
| 0 | Pit lane | Cloud Shell, Foundry resource + project, model deployment, first API call |
| 1 | Race rules | Responsible AI, how generative models work, choosing models and deployments, AI workloads, Content Safety |
| 2 | Pole position | Prompts in the playground, parameters, grounding, JSON output, Foundry SDK chat client |
| 3 | Pit crew | Build, test and publish an agent (file search, code interpreter), call it from Python |
| 4 | Radio check | Azure AI Language, Translator, Azure Speech, Voice mode, gpt-audio-mini |
| 5 | Eyes on the track | Azure AI Vision, multimodal image prompts, FLUX image generation |
| 6 | Paperwork | Azure Content Understanding on documents, images, audio and video; custom analyzers |
| 7 | Checkered flag | 40-question practice exam, cleanup |

## Structure

- `src/*.html` — page fragments (a `<!--META {...} -->` header plus body HTML)
- `build.py` — wraps fragments in the shared shell (nav, mast, TOC, pager, footer) → `*.html`
- `assets/` — stylesheet, site JS, quiz engine and question bank
- `pit-crew/` — the lightweight Python apps students run, plus the instructor helper
- `images/`, `media/`, `downloads/` — screenshots (real API responses, rendered), photos, documents, audio, video, raw results

Rebuild with `python3 build.py`.

## Credits and licence

Code and course text: MIT. Vehicle photos: public domain / CC0 from Wikimedia Commons (see `credits.html`). Documents, datasets, audio and video were generated for the course. Not affiliated with Microsoft; Velocity Motors is fictional.
