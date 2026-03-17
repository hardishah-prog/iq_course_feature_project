"""
pages/3_🧠_Quiz.py
------------------
Interactive quiz mode: pick a lesson, answer MCQs, see score.
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from api_client import get_courses, get_lessons, get_questions, submit_answer

st.set_page_config(page_title="Quiz | IQ Platform", page_icon="🧠", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); min-height: 100vh; }
    [data-testid="stSidebar"] { background: rgba(255,255,255,0.05); backdrop-filter: blur(16px); border-right: 1px solid rgba(255,255,255,0.1); }
    [data-testid="stSidebar"] * { color: #e0e0e0 !important; }

    .page-title { font-size: 2.2rem; font-weight: 800;
        background: linear-gradient(90deg, #34d399, #60a5fa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
    .section-label { color: #94a3b8; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.5rem; }

    .q-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
    }
    .q-number { color: #64748b; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
    .q-text { color: #e2e8f0; font-size: 1.05rem; font-weight: 600; margin: 0.5rem 0 1rem; line-height: 1.5; }
    .pill { display: inline-block; padding: 0.2rem 0.65rem; border-radius: 999px; font-size: 0.72rem; font-weight: 600; }
    .pill-easy   { background: #064e3b; color: #34d399; }
    .pill-medium { background: #78350f; color: #fbbf24; }
    .pill-hard   { background: #7f1d1d; color: #f87171; }

    .score-box {
        text-align: center;
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
    }
    .score-num { font-size: 4rem; font-weight: 800;
        background: linear-gradient(90deg, #a78bfa, #34d399);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
    .score-label { color: #94a3b8; margin-top: 0.4rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-title">🧠 Quiz Mode</div>', unsafe_allow_html=True)
st.markdown("Select a lesson, answer the MCQs, and see your score.")
st.markdown("---")

# ── Session State ─────────────────────────────────────────────────────────────

if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False
if "quiz_results" not in st.session_state:
    st.session_state.quiz_results = {}  # question_id -> {is_correct, message, chosen_id}
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}  # question_id -> option_id selected


# ── Course / Lesson Selectors ─────────────────────────────────────────────────

courses, err = get_courses()
if err:
    st.error(err)
    st.stop()
if not courses:
    st.info("No courses yet. Head to 📚 Courses to create one.")
    st.stop()

course_map = {f"#{c['id']} — {c['title']}": c["id"] for c in courses}

col_sel1, col_sel2 = st.columns(2, gap="medium")
with col_sel1:
    chosen_course_label = st.selectbox("📚 Course", list(course_map.keys()))
    course_id = course_map[chosen_course_label]

lessons, err2 = get_lessons(course_id)
if err2:
    st.error(err2)
    st.stop()
if not lessons:
    st.info("This course has no lessons yet. Create one on the 📖 Lessons page.")
    st.stop()

lesson_map = {f"#{l['id']} — {l['title']}": l["id"] for l in lessons}

with col_sel2:
    chosen_lesson_label = st.selectbox("📖 Lesson", list(lesson_map.keys()))
    lesson_id = lesson_map[chosen_lesson_label]


# Reset quiz state when lesson changes
if st.session_state.get("active_lesson_id") != lesson_id:
    st.session_state.active_lesson_id = lesson_id
    st.session_state.quiz_submitted = False
    st.session_state.quiz_results = {}
    st.session_state.quiz_answers = {}


# ── Load Questions ────────────────────────────────────────────────────────────

questions, err3 = get_questions(lesson_id)
if err3:
    st.error(err3)
    st.stop()
if not questions:
    st.info("This lesson has no questions yet. Use 🤖 AI Generator to create some!")
    st.stop()

st.markdown(f"**{len(questions)} question{'s' if len(questions)>1 else ''} found** for this lesson.")
st.markdown("---")


# ── Quiz UI ───────────────────────────────────────────────────────────────────

if not st.session_state.quiz_submitted:
    with st.form("quiz_form"):
        for idx, q in enumerate(questions):
            diff = q.get("difficulty", "medium")
            options = q.get("options", [])
            option_labels = [o["option_text"] for o in options]
            option_ids    = [o["id"] for o in options]

            st.markdown(f"""
            <div class="q-card">
                <div class="q-number">Question {idx + 1} &nbsp;·&nbsp;
                    <span class="pill pill-{diff}">{diff.upper()}</span>
                </div>
                <div class="q-text">{q['question_text']}</div>
            </div>
            """, unsafe_allow_html=True)

            chosen_label = st.radio(
                f"q_{q['id']}",
                option_labels,
                key=f"radio_{q['id']}",
                label_visibility="collapsed"
            )
            if chosen_label:
                chosen_idx = option_labels.index(chosen_label)
                st.session_state.quiz_answers[q["id"]] = option_ids[chosen_idx]

            st.markdown("<hr style='border-color:rgba(255,255,255,0.06);'>", unsafe_allow_html=True)

        submitted = st.form_submit_button("🚀 Submit Quiz", use_container_width=True, type="primary")

    if submitted:
        results = {}
        for q in questions:
            qid = q["id"]
            oid = st.session_state.quiz_answers.get(qid)
            if oid is None:
                results[qid] = {"is_correct": False, "message": "⚠️ Not answered."}
                continue
            res, err4 = submit_answer(qid, oid)
            if err4:
                results[qid] = {"is_correct": False, "message": err4}
            else:
                results[qid] = res
        st.session_state.quiz_results = results
        st.session_state.quiz_submitted = True
        st.rerun()


else:
    # ── Results ───────────────────────────────────────────────────────────────
    results = st.session_state.quiz_results
    correct = sum(1 for r in results.values() if r.get("is_correct"))
    total   = len(questions)
    pct     = int(correct / total * 100) if total else 0

    emoji = "🏆" if pct == 100 else ("🎯" if pct >= 70 else ("📈" if pct >= 40 else "💪"))

    st.markdown(f"""
    <div class="score-box">
        <div style="font-size:2.5rem;">{emoji}</div>
        <div class="score-num">{correct} / {total}</div>
        <div class="score-label">{pct}% — {'Perfect score!' if pct==100 else 'Keep it up!'}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📋 Answer Review")
    for idx, q in enumerate(questions):
        qid = q["id"]
        res = results.get(qid, {})
        is_correct = res.get("is_correct", False)
        msg = res.get("message", "")
        icon = "✅" if is_correct else "❌"

        with st.expander(f"{icon} Q{idx+1}: {q['question_text'][:80]}..."):
            st.markdown(f"**Result:** {msg}")

    if st.button("🔄 Retake Quiz", use_container_width=True):
        st.session_state.quiz_submitted = False
        st.session_state.quiz_results = {}
        st.session_state.quiz_answers = {}
        st.rerun()
