"""
app.py
------
Main entry point for the Cognitive Training Platform Streamlit frontend.
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from api_client import health_check

st.set_page_config(
    page_title="IQ Content Platform",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        min-height: 100vh;
    }

    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(16px);
        border-right: 1px solid rgba(255,255,255,0.1);
    }

    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }

    .main-header {
        text-align: center;
        padding: 3rem 1rem;
    }

    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        line-height: 1.1;
    }

    .main-sub {
        color: #94a3b8;
        font-size: 1.1rem;
        margin-top: 0.8rem;
    }

    .stat-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        backdrop-filter: blur(8px);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .stat-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 32px rgba(167, 139, 250, 0.2);
    }

    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #a78bfa, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .stat-label {
        color: #94a3b8;
        font-size: 0.9rem;
        margin-top: 0.3rem;
    }

    .pill {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 0.15rem;
    }
    .pill-easy   { background: #064e3b; color: #34d399; }
    .pill-medium { background: #78350f; color: #fbbf24; }
    .pill-hard   { background: #7f1d1d; color: #f87171; }
    .pill-area   { background: rgba(167,139,250,0.15); color: #a78bfa; border: 1px solid rgba(167,139,250,0.3); }

    .health-ok  { color: #34d399; font-weight: 600; }
    .health-err { color: #f87171; font-weight: 600; }

    .feature-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 0.75rem;
    }

    .feature-title { color: #e2e8f0; font-weight: 600; font-size: 1.05rem; }
    .feature-desc  { color: #94a3b8; font-size: 0.9rem; margin-top: 0.3rem; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🧠 IQ Platform")
    st.markdown("---")

    data, err = health_check()
    if data:
        st.markdown(f'<span class="health-ok">● API Online</span> &nbsp; v{data.get("version","—")}', unsafe_allow_html=True)
    else:
        st.markdown('<span class="health-err">● API Offline</span>', unsafe_allow_html=True)
        st.caption("Start the backend with `docker-compose up -d`")

    st.markdown("---")
    st.caption("Navigate using the pages in the sidebar above.")


# ── Home Hero ──────────────────────────────────────────────────────────────────

st.markdown("""
<div class="main-header">
    <div class="main-title">🧠 Cognitive Training Platform</div>
    <div class="main-sub">AI-powered learning. Build sharper thinking, one challenge at a time.</div>
</div>
""", unsafe_allow_html=True)


# ── Stats Row ──────────────────────────────────────────────────────────────────

from api_client import get_courses

courses_data, _ = get_courses()
num_courses = len(courses_data) if courses_data else 0

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class="stat-card">
        <div class="stat-number">{num_courses}</div>
        <div class="stat-label">Courses Available</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown("""<div class="stat-card">
        <div class="stat-number">5</div>
        <div class="stat-label">Cognitive Areas</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown("""<div class="stat-card">
        <div class="stat-number">3</div>
        <div class="stat-label">Difficulty Levels</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown("""<div class="stat-card">
        <div class="stat-number">AI</div>
        <div class="stat-label">Groq Llama-3.3 Powered</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Feature Overview ───────────────────────────────────────────────────────────

st.markdown("### 🚀 What you can do")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">📚 Courses</div>
        <div class="feature-desc">Browse and create structured courses across 5 cognitive areas.</div>
    </div>
    <div class="feature-card">
        <div class="feature-title">📖 Lessons</div>
        <div class="feature-desc">Dive into lesson content linked to any course.</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">🧠 Quiz Mode</div>
        <div class="feature-desc">Test yourself with MCQs and get instant feedback + score.</div>
    </div>
    <div class="feature-card">
        <div class="feature-title">🤖 AI Generator</div>
        <div class="feature-desc">Generate full courses and questions using Groq Llama-3.3-70b.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("Use the navigation pages in the sidebar to get started.")
