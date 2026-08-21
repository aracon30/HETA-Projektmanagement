"""
Anbindung an Microsoft To Do (= Outlook-Aufgaben, gleiche Daten) über Microsoft Graph.

Nutzt den Client-Credentials-Flow (App-only, kein Login der Person nötig),
damit im Namen jeder beliebigen Person eine Aufgabe angelegt werden kann.
Benötigt eine Azure-AD-App-Registrierung mit Anwendungsberechtigung
"Tasks.ReadWrite" (Microsoft Graph, mit Admin-Zustimmung).

Konfiguration über Umgebungsvariablen:
  GRAPH_TENANT_ID
  GRAPH_CLIENT_ID
  GRAPH_CLIENT_SECRET

Ist eine dieser Variablen nicht gesetzt, ist die Integration "deaktiviert"
und create_task() gibt None zurück, ohne einen Fehler zu werfen — das Tool
funktioniert dann weiter wie bisher (Aufgabe wird nur lokal markiert).
"""
import os
import requests

TENANT_ID = os.environ.get("GRAPH_TENANT_ID")
CLIENT_ID = os.environ.get("GRAPH_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GRAPH_CLIENT_SECRET")
LIST_NAME = "Auftragspipeline"

GRAPH_BASE = "https://graph.microsoft.com/v1.0"


def is_configured():
    return bool(TENANT_ID and CLIENT_ID and CLIENT_SECRET)


def _get_token():
    if not is_configured():
        return None
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials",
    }
    res = requests.post(url, data=data, timeout=10)
    res.raise_for_status()
    return res.json()["access_token"]


def _get_or_create_list(token, user_email):
    """Findet (oder legt an) die 'Auftragspipeline'-Liste im To Do der Person."""
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"{GRAPH_BASE}/users/{user_email}/todo/lists", headers=headers, timeout=10)
    res.raise_for_status()
    for lst in res.json().get("value", []):
        if lst["displayName"] == LIST_NAME:
            return lst["id"]

    res = requests.post(
        f"{GRAPH_BASE}/users/{user_email}/todo/lists",
        headers=headers,
        json={"displayName": LIST_NAME},
        timeout=10,
    )
    res.raise_for_status()
    return res.json()["id"]


def create_task(user_email, title, body_text=None, due_date_iso=None):
    """
    Legt eine Aufgabe in der persönlichen To-Do-Liste der Person an.
    Gibt (list_id, task_id) zurück, oder None wenn die Integration nicht
    konfiguriert ist. Wirft eine Exception bei einem echten API-Fehler.
    """
    if not is_configured():
        return None

    token = _get_token()
    list_id = _get_or_create_list(token, user_email)

    headers = {"Authorization": f"Bearer {token}"}
    payload = {"title": title}
    if body_text:
        payload["body"] = {"content": body_text, "contentType": "text"}
    if due_date_iso:
        payload["dueDateTime"] = {"dateTime": f"{due_date_iso}T09:00:00", "timeZone": "W. Europe Standard Time"}

    res = requests.post(
        f"{GRAPH_BASE}/users/{user_email}/todo/lists/{list_id}/tasks",
        headers=headers,
        json=payload,
        timeout=10,
    )
    res.raise_for_status()
    task = res.json()
    return list_id, task["id"]
