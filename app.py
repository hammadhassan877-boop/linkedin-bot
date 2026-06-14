import streamlit as st
import anthropic
import requests
import json

# --- APP CONFIGURATION ---
st.set_page_config(page_title="LinkedIn AI Strategist", page_icon="📈", layout="wide")

# --- STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #0077b5; color: white; }
    .stTextArea textarea { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR / CREDENTIALS ---
with st.sidebar:
    st.title("Settings")
    st.info("Ensure your API keys are set in Streamlit Secrets or entered below.")
    
    # Try to get keys from secrets, otherwise use inputs
    claude_key = st.secrets.get("CLAUDE_API_KEY", st.text_input("Claude API Key", type="password"))
    li_token = st.secrets.get("LINKEDIN_ACCESS_TOKEN", st.text_input("LinkedIn Token", type="password"))
    li_urn = st.secrets.get("LINKEDIN_PERSON_URN", st.text_input("LinkedIn URN (e.g., urn:li:person:ID)"))

# Initialize Claude Client
if claude_key:
    client = anthropic.Anthropic(api_key=claude_key)

# --- STATE MANAGEMENT ---
if "step" not in st.session_state: st.session_state.step = 1
if "analysis" not in st.session_state: st.session_state.analysis = ""
if "posts" not in st.session_state: st.session_state.posts = []

# --- AI HELPER FUNCTION ---
def ask_claude(system_prompt, user_prompt):
    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=2000,
        temperature=0.7,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )
    return message.content[0].text

#
