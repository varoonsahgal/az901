"""Instructor · issue a Temporary Access Pass to every student, for a sign-in with no phone and no MFA setup.

A Temporary Access Pass (TAP) is a passcode an admin issues; Microsoft Entra treats a sign-in with it as
multifactor, so it also satisfies Azure's mandatory MFA. Students type their username, then the pass.

Run (the morning of class, or the evening before with --start):
    pip install azure-identity requests
    python issue_passes.py                                  # every member of "AI-901 Students", valid 12 hours from now
    python issue_passes.py --start "2026-11-20 08:00"       # valid 08:00 to 20:00 local time that day
    python issue_passes.py --hours 4 --only student01,student02

12 hours needs the tenant's TAP policy raised from Entra's default maximum of 8: Entra admin center →
Authentication methods → Policies → Temporary Access Pass → Configure → Maximum lifetime.

Sign-in: the script prints a device code. Sign in as a Global Administrator or Authentication Administrator.
The first time, Entra asks you to consent to "Microsoft Graph Command Line Tools" reading group members and
reading users and managing authentication methods; accept for your organisation.

Output: passes-<date>.csv next to this script (readable only by you). Paste the pass column into the class sheet,
then delete the file. Passes are never printed to the screen.
Each student can hold only one pass, so running again replaces their previous pass.
"""
import argparse, csv, datetime as dt, os, sys
import requests
from azure.identity import DeviceCodeCredential

GRAPH = "https://graph.microsoft.com/v1.0"
GRAPH_CLI_APP = "14d82eec-204b-4c2f-b7e8-296a70dab67e"   # Microsoft Graph Command Line Tools (public client)
SCOPES = ["https://graph.microsoft.com/UserAuthenticationMethod.ReadWrite.All",
          "https://graph.microsoft.com/GroupMember.Read.All",
          "https://graph.microsoft.com/User.Read.All"]                 # usernames of the group's members

p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
p.add_argument("--tenant", default="vsahgal.onmicrosoft.com")
p.add_argument("--group", default="AI-901 Students", help="display name of the students group")
p.add_argument("--hours", type=float, default=12,
               help="lifetime in hours (default 12; the tenant's TAP policy caps it, and Entra's out-of-the-box max is 8)")
p.add_argument("--start", help='local start time, "YYYY-MM-DD HH:MM" (default: now)')
p.add_argument("--only", help="comma-separated usernames or prefixes, e.g. student01,student02")
p.add_argument("--out", help="CSV path (default: passes-<date>.csv next to this script)")
a = p.parse_args()

cred = DeviceCodeCredential(client_id=GRAPH_CLI_APP, tenant_id=a.tenant)
H = {"Authorization": f"Bearer {cred.get_token(*SCOPES).token}", "Content-Type": "application/json"}

def get(url):
    r = requests.get(url, headers=H); r.raise_for_status(); return r.json()

groups = get(f"{GRAPH}/groups?$filter=displayName eq '{a.group}'&$select=id")["value"]
if not groups: sys.exit(f"No group named {a.group!r}")
members, url = [], f"{GRAPH}/groups/{groups[0]['id']}/members/microsoft.graph.user?$select=id,userPrincipalName,displayName&$top=999"
while url:
    page = get(url); members += page["value"]; url = page.get("@odata.nextLink")
members = [m for m in members if m.get("userPrincipalName")]
if a.only:
    wanted = [w.strip().lower() for w in a.only.split(",")]
    members = [m for m in members if any(m["userPrincipalName"].lower().startswith(w) for w in wanted)]
members.sort(key=lambda m: m["userPrincipalName"])
if not members: sys.exit("No matching students")

body = {"lifetimeInMinutes": int(a.hours * 60), "isUsableOnce": False}
if a.start:
    body["startDateTime"] = dt.datetime.strptime(a.start, "%Y-%m-%d %H:%M").astimezone().astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

out = a.out or os.path.join(os.path.dirname(os.path.abspath(__file__)), f"passes-{dt.date.today():%Y%m%d}.csv")
rows, failed = [], []
for m in members:
    base = f"{GRAPH}/users/{m['id']}/authentication/temporaryAccessPassMethods"
    for old in get(base)["value"]:                      # one pass per user: remove the previous one
        requests.delete(f"{base}/{old['id']}", headers=H).raise_for_status()
    r = requests.post(base, headers=H, json=body)
    if not r.ok:
        failed.append((m["userPrincipalName"], r.json().get("error", {}).get("message", r.text)[:200])); continue
    t = r.json()
    start = dt.datetime.fromisoformat(t["startDateTime"].replace("Z", "+00:00")).astimezone()
    end = start + dt.timedelta(minutes=t["lifetimeInMinutes"])
    rows.append([m["userPrincipalName"].split("@")[0].replace("student", "s"), m["userPrincipalName"],
                 t["temporaryAccessPass"], f"{start:%Y-%m-%d %H:%M}", f"{end:%Y-%m-%d %H:%M}"])
    print(f"  {m['userPrincipalName']:40s} pass issued · valid {start:%a %H:%M} → {end:%a %H:%M}")

old_umask = os.umask(0o077)                              # the file holds credentials: owner-only
with open(out, "w", newline="") as f:
    csv.writer(f).writerows([["Student #", "Sign-in (username)", "Temporary Access Pass", "Valid from", "Valid until"]] + rows)
os.umask(old_umask)
print(f"\n{len(rows)} passes written to {out}")
for upn, msg in failed:
    print(f"  FAILED {upn}: {msg}")
if any("lifetime" in msg.lower() for _, msg in failed):
    print("  The tenant policy caps the lifetime: Entra admin center → Authentication methods → Policies → "
          "Temporary Access Pass → Configure → Maximum lifetime.")
sys.exit(1 if failed else 0)
