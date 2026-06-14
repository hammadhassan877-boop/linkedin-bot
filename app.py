import streamlit as st
import openai
import requests
import json

# --- INITIAL CONFIG ---
st.set_page_config(page_title="LinkedIn AI Ghostwriter", page_icon="📝")
st.title("🚀 LinkedIn AI Ghostwriter & Strategist")

# Sidebar: Credentials
with st.sidebar:
    st.header("🔑 API Credentials")
    openai_key = st.text_input("OpenAI API Key", type="password")
    li_access_token = st.text_input("LinkedIn Access Token", type="password")
    li_member_id = st.text_input("LinkedIn Member ID (URN)", help="Format: urn:li:person:XXXX")

# --- STEP 1: DATA INGESTION & GAP ANALYSIS ---
if "step" not in st.session_state: st.session_state.step = 1

if st.session_state.step == 1:
    st.header("1. Profile Gap Analysis")
    profile_text = st.text_area("Paste your LinkedIn 'About' and 'Experience' text here:")
    goal = st.selectbox("What is your goal?", ["Build Authority", "Generate Leads", "Find a Job"])

    if st.button("Analyze My Profile"):
        if not openai_key: st.error("Please enter OpenAI Key")
        else:
            client = openai.OpenAI(api_key=openai_key)
            prompt = f"Act as a LinkedIn coach. Analyze this profile: {profile_text}. Identify 3 gaps compared to a {goal} goal. Provide a weekly 5-item checklist."
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            st.session_state.analysis = response.choices[0].message.content
            st.session_state.step = 2
            st.rerun()

# --- STEP 2: CONTENT INTERVIEW ---
if st.session_state.step == 2:
    st.header("2. Weekly Content Interview")
    st.info("The AI needs 'fuel' to make your posts sound like you.")
    
    with st.form("interview"):
        q1 = st.text_input("What is one specific win or lesson from your work this week?")
        q2 = st.text_input("What is a common myth in your industry you want to debunk?")
        q3 = st.text_input("What is one resource or tool that helped you lately?")
        
        if st.form_submit_button("Generate Weekly Content"):
            client = openai.OpenAI(api_key=openai_key)
            gen_prompt = f"Based on these answers: {q1}, {q2}, {q3}. Write 3 LinkedIn posts. Post 1: Authority. Post 2: Opinion. Post 3: Resource. Use hooks and line breaks."
            
            resp = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": gen_prompt}]
            )
            st.session_state.posts = resp.choices[0].message.content
            st.session_state.step = 3
            st.rerun()

# --- STEP 3: REVIEW & POST ---
if st.session_state.step == 3:
    st.header("3. Your Weekly Plan & Posts")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📋 Weekly Checklist")
        st.markdown(st.session_state.analysis)
        
    with col2:
        st.subheader("✍️ Drafted Posts")
        # Split posts by keyword 'Post' to show them individually
        post_list = st.session_state.posts.split("Post ")
        for i, p in enumerate(post_list[1:]):
            content = st.text_area(f"Edit Post {i+1}", value=p, height=200)
            
            if st.button(f"🚀 Publish Post {i+1} to LinkedIn"):
                # LINKEDIN API CALL
                url = "https://api.linkedin.com/v2/ugcPosts"
                headers = {
                    "Authorization": f"Bearer {li_access_token}",
                    "X-Restli-Protocol-Version": "2.0.0",
                    "Content-Type": "application/json"
                }
                post_data = {
                    "author": li_member_id,
                    "lifecycleState": "PUBLISHED",
                    "specificContent": {
                        "com.linkedin.ugc.ShareContent": {
                            "shareCommentary": {"text": content},
                            "shareMediaCategory": "NONE"
                        }
                    },
                    "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
                }
                res = requests.post(url, headers=headers, json=post_data)
                if res.status_code == 201: st.success("Post live!")
                else: st.error(f"Error: {res.text}")

    if st.button("Start Over"):
        st.session_state.step = 1
        st.rerun()
