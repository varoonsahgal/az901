"""Lap 2 · A lightweight chat client built with the Foundry SDK.

Run:  python chat_client.py "your question"      (or no argument for an interactive loop)
Needs: pip install azure-ai-projects azure-identity   and   az login
Env:   PROJECT_ENDPOINT  (Foundry project endpoint, e.g. https://<resource>.services.ai.azure.com/api/projects/<project>)
       CHAT_MODEL        (deployment name, default gpt-4-1-mini)
"""
import os, sys
from azure.identity import DefaultAzureCredential          # uses your az login — no keys in code
from azure.ai.projects import AIProjectClient

endpoint = os.environ["PROJECT_ENDPOINT"]
model = os.environ.get("CHAT_MODEL", "gpt-4-1-mini")

project = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
client = project.get_openai_client()                        # an OpenAI-compatible client, already authenticated

SYSTEM = ("You are Velo, the friendly assistant for Velocity Motors dealerships. "
          "Be concise and practical. Safety first. If you don't know a Velocity-specific fact, say so.")
history = [{"role": "system", "content": SYSTEM}]

def ask(text):
    history.append({"role": "user", "content": text})
    r = client.chat.completions.create(model=model, messages=history, temperature=0.5, max_tokens=300)
    answer = r.choices[0].message.content
    history.append({"role": "assistant", "content": answer})
    print(f"\nVelo> {answer}\n      [{r.usage.prompt_tokens} prompt + {r.usage.completion_tokens} completion = {r.usage.total_tokens} tokens]")

if len(sys.argv) > 1:
    ask(" ".join(sys.argv[1:]))
else:
    print("Chat with Velo (type 'quit' to leave)")
    while (q := input("\nYou> ").strip()).lower() not in ("quit", "exit", ""):
        ask(q)
