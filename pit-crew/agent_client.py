"""Lap 3 · A lightweight client for the agent you built in the Foundry portal.

Run:  python agent_client.py "your question"      (or no argument for an interactive loop)
Needs: pip install azure-ai-projects azure-identity   and   az login
Env:   PROJECT_ENDPOINT   AGENT_NAME (default velo-warranty-expert)   AGENT_VERSION (default 1)
"""
import os, sys
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

project = AIProjectClient(endpoint=os.environ["PROJECT_ENDPOINT"], credential=DefaultAzureCredential())
client = project.get_openai_client()
agent = {"name": os.environ.get("AGENT_NAME", "velo-warranty-expert"), "version": os.environ.get("AGENT_VERSION", "1"), "type": "agent_reference"}

conversation = client.conversations.create()          # the agent remembers everything in this conversation
print(f"Talking to agent {agent['name']} v{agent['version']} · conversation {conversation.id[:18]}…")

def ask(text):
    r = client.responses.create(conversation=conversation.id, input=text, extra_body={"agent_reference": agent})
    tools = [o.type for o in r.output if o.type != "message"]          # e.g. file_search_call, code_interpreter_call
    print(f"\n{agent['name']}> {r.output_text}")
    if tools: print(f"   [tools used: {', '.join(tools)}]")

if len(sys.argv) > 1:
    ask(" ".join(sys.argv[1:]))
else:
    while (q := input("\nYou> ").strip()).lower() not in ("quit", "exit", ""):
        ask(q)
