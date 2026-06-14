import streamlit as st
import anthropic
import PyPDF2
import io

# --- APP CONFIG ---
st.set_page_config(page_title="Profile Pro", page_icon="👤")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .post-box { background-color: white; padding: 20px; border-radius: 10px; border-left: 5px solid #0077b5; margin-bottom: 20px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- HELPER: PDF READER ---
def extract_text_from_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# --- HELPER: CLAUDE AI ---
def call_claude(system_prompt, user_prompt, api_key):
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=2000,
        temperature=0.7,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )
    return message.content[0].text

# --- APP HEADER ---
st.title("👤 Profile Pro")
st.subheader("Your AI LinkedIn Ghostwriter")

# Sidebar for API Key
with st.sidebar:
    api_key = st.text_input("Enter Claude API Key", type="password")
    st.divider()
    st.write("### How it works:")
    st.write("1. Upload your LinkedIn PDF")
    st.write("2. Get a Profile Audit")
    st.write("3. Answer 3 Questions")
    st.write("4. Get 3 Ready-to-Post drafts")

# --- STEP 1: UPLOAD & AUDIT ---
if "profile_text" not in st.session_state:
    st.header("Step 1: Upload Profile")
    uploaded_file = st.file_uploader("Upload your LinkedIn PDF (Go to your profile -> More -> Save to PDF)", type="pdf")
    
    if uploaded_file and api_key:
        if st.button("Analyze My Profile"):
            with st.spinner("Reading PDF and Analyzing..."):
                text = extract_text_from_pdf(uploaded_file)
                st.session_state.profile_text = text
                
                audit_prompt = f"Analyze this LinkedIn PDF text: {text}. Identify 3 gaps in branding and suggest 3 content pillars."
                st.session_state.audit = call_claude("You are a LinkedIn strategist.", audit_prompt, api_key)
                st.rerun()
    elif not api_key:
        st.warning("Please enter your Claude API Key in the sidebar.")

# --- STEP 2: THE INTERVIEW ---
elif "answers" not in st.session_state:
    st.header("Step 2: Weekly Interview")
    st.success("Profile Analyzed! Here is your gap analysis:")
    st.info(st.session_state.audit)
    
    st.write("---")
    st.write("### Let's build your posts for this week.")
    with st.form("interview"):
        q1 = st.text_input("What is one specific project or win you worked on this week?")
        q2 = st.text_input("What is a common mistake people in your industry make?")
        q3 = st.text_input("What is one piece of advice you'd give your younger self?")
        
        if st.form_submit_button("Generate 3 Posts"):
            st.session_state.answers = f"Win: {q1}, Mistake: {q2}, Advice: {q3}"
            st.rerun()

# --- STEP 3: THE POSTS ---
else:
    st.header("Step 3: Your LinkedIn Posts for the Week")
    
    with st.spinner("Claude is writing your posts..."):
        if "final_posts" not in st.session_state:
            post_prompt = f"""
            Profile context: {st.session_state.profile_text}
            Weekly Inputs: {st.session_state.answers}
            
            Write 3 LinkedIn posts. 
            - Post 1: Educational/Insightful (based on the win)
            - Post 2: Contrarian/Opinion (based on the mistake)
            - Post 3: Personal/Relatable (based on the advice)
            
            Rules: No hashtags in the middle of sentences. Use line breaks. Keep it human. Use a professional but conversational tone.
            """
            st.session_state.final_posts = call_claude("You are a professional ghostwriter.", post_prompt, api_key)
    
    st.markdown(st.session_state.final_posts)
    
    if st.button("Reset & Start New Week"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
