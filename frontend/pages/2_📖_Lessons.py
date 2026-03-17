"""
pages/2_📖_Lessons.py
---------------------
Browse lessons per course and create new ones.
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from api_client import get_courses, get_lessons, create_lesson

st.set_page_config(page_title="Lessons | IQ Platform", page_icon="📖", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); min-height: 100vh; }
    [data-testid="stSidebar"] { background: rgba(255,255,255,0.05); backdrop-filter: blur(16px); border-right: 1px solid rgba(255,255,255,0.1); }
    [data-testid="stSidebar"] * { color: #e0e0e0 !important; }

    .page-title { font-size: 2.2rem; font-weight: 800;
        background: linear-gradient(90deg, #60a5fa, #34d399);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
    .section-label { color: #94a3b8; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.5rem; }

    .lesson-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 0.8rem;
        transition: border-color 0.2s;
    }
    .lesson-card:hover { border-color: rgba(96,165,250,0.5); }
    .lesson-title { font-size: 1.05rem; font-weight: 600; color: #e2e8f0; }
    .lesson-content { color: #94a3b8; font-size: 0.88rem; margin-top: 0.5rem; line-height: 1.55; }
    .lesson-id { color: #64748b; font-size: 0.78rem; }
    .empty-state { text-align: center; color: #64748b; padding: 2rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-title">📖 Lessons</div>', unsafe_allow_html=True)
st.markdown("Select a course to view its lessons, or create a new lesson.")
st.markdown("---")

courses, err = get_courses()
if err:
    st.error(err)
    st.stop()

if not courses:
    st.info("No courses found. Create a course first on the 📚 Courses page.")
    st.stop()

course_map = {f"#{c['id']} — {c['title']}": c for c in courses}


col_list, col_form = st.columns([3, 2], gap="large")

with col_list:
    st.markdown('<div class="section-label">Select Course</div>', unsafe_allow_html=True)
    chosen_label = st.selectbox("Course", list(course_map.keys()), label_visibility="collapsed")
    chosen_course = course_map[chosen_label]
    course_id = chosen_course["id"]

    st.markdown('<div class="section-label" style="margin-top:1rem;">Lessons</div>', unsafe_allow_html=True)
    lessons, err2 = get_lessons(course_id)
    if err2:
        st.error(err2)
    elif not lessons:
        st.markdown('<div class="empty-state">📭 No lessons yet. Create one →</div>', unsafe_allow_html=True)
    else:
        for l in lessons:
            content_preview = (l.get("content_text") or "")[:200]
            if len(l.get("content_text") or "") > 200:
                content_preview += "..."
            st.markdown(f"""
            <div class="lesson-card">
                <div class="lesson-id">Lesson ID: {l['id']}</div>
                <div class="lesson-title">{l['title']}</div>
                <div class="lesson-content">{content_preview or '<em>No content text provided.</em>'}</div>
            </div>
            """, unsafe_allow_html=True)


with col_form:
    st.markdown('<div class="section-label">Create New Lesson</div>', unsafe_allow_html=True)

    with st.form("create_lesson_form", clear_on_submit=True):
        st.caption(f"Adding lesson to: **{chosen_course['title']}**")
        title = st.text_input("Lesson Title", placeholder="e.g. Introduction to Pattern Grids")
        content_text = st.text_area("Content Text (optional)", placeholder="Lesson body text...", height=140)
        image_url = st.text_input("Image URL (optional)", placeholder="https://...")
        submitted = st.form_submit_button("📝 Create Lesson", use_container_width=True, type="primary")

    if submitted:
        if not title.strip():
            st.warning("Please enter a lesson title.")
        else:
            with st.spinner("Creating lesson..."):
                result, err3 = create_lesson(
                    course_id,
                    title.strip(),
                    content_text.strip() or None,
                    image_url.strip() or None,
                )
            if err3:
                st.error(err3)
            else:
                st.success(f"✅ Lesson **{result['title']}** created! (ID: `{result['id']}`)")
                st.rerun()
