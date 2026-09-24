import json
import os
import urllib.request
import urllib.error
import urllib.parse
import ssl
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="J.A.V.I.S. OS", page_icon="🤖", layout="centered"
)

API_KEY = "Gsk_kEBYvrWMlgWDk31sXJjjWGdyb3FY9EBIRotr0K3KwlGDPVJznJho"
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MEMORY_FILE = "jarvis_memory.json"

DEFAULT_MEMORY = {
    "operator": "Operator",
    "bio": (
        "An ambitious developer and tech enthusiast building custom AI systems"
        " on iOS."
    ),
    "interests": [
        "Python programming",
        "Artificial Intelligence",
        "Sci-fi",
        "Data Science",
    ],
    "focus_goal": 4.0,
    "habits": ["7:00 AM Wake Up", "Python Practice", "Data Science Study"],
    "study_logs": [3.0, 4.0, 5.0, 2.0, 6.0],
    "pending_tasks": [
        "Complete Linear Algebra practice",
        "Build modular Python engine",
    ],
}


def load_memory():
  if os.path.exists(MEMORY_FILE):
    try:
      with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    except Exception:
      pass
  return DEFAULT_MEMORY.copy()


jarvis_memory = load_memory()
SSL_CONTEXT = ssl._create_unverified_context()


def get_clean_headers():
  clean_key = API_KEY.strip()
  if clean_key.startswith("Gsk_"):
    clean_key = "gsk_" + clean_key[4:]
  return {
      "Authorization": f"Bearer {clean_key}",
      "Content-Type": "application/json",
      "User-Agent": "Mozilla/5.0",
  }


def build_system_prompt():
  tasks = ", ".join(jarvis_memory.get("pending_tasks", []))
  return f"""
    You are J.A.V.I.S., a witty, sarcastic, and sharp AI companion built for a developer operator.
    Operator Name: {jarvis_memory.get('operator', 'Operator')}
    Active Tasks: {tasks}
    Keep responses punchy, fast, and clever.
    """


def query_ai_engine(history):
  headers = get_clean_headers()
  messages = [{"role": "system", "content": build_system_prompt()}]
  for msg in history:
    messages.append({"role": msg["role"], "content": msg["content"]})

  payload = {
      "model": "openai/gpt-oss-20b",
      "messages": messages,
      "temperature": 0.7,
  }

  try:
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15, context=SSL_CONTEXT) as response:
      res_data = json.loads(response.read().decode("utf-8"))
      return res_data["choices"][0]["message"]["content"]
  except urllib.error.HTTPError as e:
    error_body = e.read().decode("utf-8", errors="ignore")
    return f"[Error HTTP {e.code}]: {error_body}"
  except Exception as e:
    return f"[Error]: {str(e)}"


# UI Layout
st.title("J.A.V.I.S. OS v7.8.0")
st.caption(
    "Meet J.A.V.I.S., your elite, Tony Stark-inspired AI companion built for"
    " iOS."
)

if "messages" not in st.session_state:
  st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

# User prompt
if prompt := st.chat_input("State your query, Operator..."):
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
    st.markdown(prompt)

  with st.chat_message("assistant"):
    with st.spinner("J.A.V.I.S. Thinking..."):
      response = query_ai_engine(st.session_state.messages)
      st.markdown(response)

  st.session_state.messages.append({"role": "assistant", "content": response})
