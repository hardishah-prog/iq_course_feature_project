"""
pages/1_📚_Courses.py
---------------------
Browse and create courses.
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from api_client import get_courses, create_course

st.set_page_config(page_title="Courses | IQ Platform", page_icon="📚", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); min-height: 100vh; }
    [data-testid="stSidebar"] { background: rgba(255,255,255,0.05); backdrop-filter: blur(16px); border-right: 1px solid rgba(255,255,255,0.1); }
    [data-testid="stSidebar"] * { color: #e0e0e0 !important; }

    .page-title { font-size: 2.2rem; font-weight: 800;
        background: linear-gradient(90deg, #a78bfa, #60a5fa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
    .section-label { color: #94a3b8; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.5rem; }

    .course-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 0.8rem;
        transition: border-color 0.2s, transform 0.2s;
    }
    .course-card:hover { border-color: rgba(167,139,250,0.5); transform: translateY(-2px); }
    .course-title { font-size: 1.1rem; font-weight: 600; color: #e2e8f0; }
    .course-desc  { color: #94a3b8; font-size: 0.88rem; margin-top: 0.3rem; }
    .pill { display: inline-block; padding: 0.2rem 0.65rem; border-radius: 999px; font-size: 0.72rem; font-weight: 600; margin-right: 0.4rem; }
    .pill-easy   { background: #064e3b; color: #34d399; }
    .pill-medium { background: #78350f; color: #fbbf24; }
    .pill-hard   { background: #7f1d1d; color: #f87171; }
    .pill-area   { background: rgba(167,139,250,0.15); color: #a78bfa; border: 1px solid rgba(167,139,250,0.3); }
    .empty-state { text-align: center; color: #64748b; padding: 2rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-title">📚 Courses</div>', unsafe_allow_html=True)
st.markdown("Browse all courses or create a new one below.")
st.markdown("---")

# These are the exact enum VALUES the API accepts (not the Python attribute names)
COGNITIVE_AREAS = [
    "Analytical Reasoning",
    "Pattern Recognition",
    "Spatial Awareness",
    "Logical Thinking",
    "Memory Evaluation",
]
DIFFICULTIES = ["easy", "medium", "hard"]


# ── Course List ────────────────────────────────────────────────────────────────

col_list, col_form = st.columns([3, 2], gap="large")

with col_list:
    st.markdown('<div class="section-label">All Courses</div>', unsafe_allow_html=True)

    courses, err = get_courses()
    if err:
        st.error(err)
    elif not courses:
        st.markdown('<div class="empty-state">📭 No courses yet. Create one →</div>', unsafe_allow_html=True)
    else:
        for c in courses:
            diff = c.get("difficulty", "medium")
            area = c.get("cognitive_area", "")
            pill_cls = f"pill-{diff}"
            st.markdown(f"""
            <div class="course-card">
                <div class="course-title">#{c['id']} — {c['title']}</div>
                <div class="course-desc">{c.get('description') or 'No description provided.'}</div>
                <div style="margin-top: 0.6rem;">
                    <span class="pill {pill_cls}">{diff.upper()}</span>
                    <span class="pill pill-area">{area.replace('_', ' ').title()}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ── Create Course Form ─────────────────────────────────────────────────────────

with col_form:
    st.markdown('<div class="section-label">Create New Course</div>', unsafe_allow_html=True)

    with st.form("create_course_form", clear_on_submit=True):
        title = st.text_input("Title", placeholder="e.g. Spatial Reasoning Basics")
        description = st.text_area("Description (optional)", placeholder="What is this course about?", height=80)
        cognitive_area = st.selectbox("Cognitive Area", COGNITIVE_AREAS)
        difficulty = st.selectbox("Difficulty", DIFFICULTIES, format_func=str.capitalize)
        submitted = st.form_submit_button("✨ Create Course", use_container_width=True, type="primary")

    if submitted:
        if not title.strip():
            st.warning("Please enter a title.")
        else:
            with st.spinner("Creating course..."):
                result, err = create_course(title.strip(), description.strip() or None, cognitive_area, difficulty)
            if err:
                st.error(err)
            else:
                st.success(f"✅ Course **{result['title']}** created! (ID: `{result['id']}`)")
                st.rerun()
