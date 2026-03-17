"""
pages/4_🤖_AI_Generate.py
--------------------------
AI content generation: questions, full courses, and image puzzles.
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from api_client import (
    get_courses, get_lessons,
    generate_questions, generate_course,
    generate_image_puzzle, generate_lesson,
    check_puzzle_answer,
)

st.set_page_config(page_title="AI Generate | IQ Platform", page_icon="🤖", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); min-height: 100vh; }
    [data-testid="stSidebar"] { background: rgba(255,255,255,0.05); backdrop-filter: blur(16px); border-right: 1px solid rgba(255,255,255,0.1); }
    [data-testid="stSidebar"] * { color: #e0e0e0 !important; }

    .page-title { font-size: 2.2rem; font-weight: 800;
        background: linear-gradient(90deg, #f472b6, #a78bfa, #60a5fa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }

    .job-result {
        background: rgba(52, 211, 153, 0.08);
        border: 1px solid rgba(52, 211, 153, 0.3);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin-top: 1rem;
    }
    .job-id-label { color: #94a3b8; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; }
    .job-id-value { color: #34d399; font-family: monospace; font-size: 0.95rem; margin-top: 0.2rem; word-break: break-all; }

    .puzzle-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 14px;
        padding: 1.5rem;
        text-align: center;
    }
    .puzzle-title { color: #e2e8f0; font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem; }
    .puzzle-desc  { color: #94a3b8; font-size: 0.9rem; }

    .info-chip {
        display: inline-block; background: rgba(167,139,250,0.12);
        color: #a78bfa; border: 1px solid rgba(167,139,250,0.3);
        border-radius: 999px; padding: 0.25rem 0.75rem;
        font-size: 0.78rem; font-weight: 600; margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-title">🤖 AI Content Generator</div>', unsafe_allow_html=True)
st.markdown("Powered by **Groq Llama-3.3-70b-versatile**. Generation runs as a background job via Redis Queue.")
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


tab1, tab2, tab3, tab4 = st.tabs(["💬 Generate Questions", "🎓 Generate Full Course", "📖 Generate Lesson", "🖼️ Image Puzzle"])


# ── Tab 1: Generate Questions ─────────────────────────────────────────────────

with tab1:
    st.markdown('<span class="info-chip">Enqueues a background job → generates 4 MCQs via Groq → saves to DB</span>', unsafe_allow_html=True)

    courses, err = get_courses()
    if err:
        st.error(err)
    elif not courses:
        st.info("Create a course and lesson first before generating questions.")
    else:
        course_map = {f"#{c['id']} — {c['title']}": c["id"] for c in courses}

        with st.form("gen_questions_form"):
            col1, col2 = st.columns(2)
            with col1:
                topic = st.text_input("Topic", placeholder="e.g. Working Memory strategies")
                chosen_course_label = st.selectbox("Course", list(course_map.keys()))
                course_id = course_map[chosen_course_label]
            with col2:
                cognitive_area = st.selectbox("Cognitive Area", COGNITIVE_AREAS)
                difficulty = st.selectbox("Difficulty", DIFFICULTIES, format_func=str.capitalize)

            # Load lessons for selected course
            lessons, _ = get_lessons(course_id)
            if lessons:
                lesson_map = {f"#{l['id']} — {l['title']}": l["id"] for l in lessons}
                chosen_lesson_label = st.selectbox("Attach to Lesson", list(lesson_map.keys()))
                lesson_id = lesson_map[chosen_lesson_label]
            else:
                st.warning("This course has no lessons. Create a lesson first.")
                lesson_id = None

            submitted = st.form_submit_button("⚡ Enqueue Question Generation", use_container_width=True, type="primary")

        if submitted:
            if not topic.strip():
                st.warning("Please enter a topic.")
            elif not lesson_id:
                st.warning("Please select a lesson.")
            else:
                with st.spinner("Enqueueing job with Redis..."):
                    result, err2 = generate_questions(topic.strip(), cognitive_area, difficulty, lesson_id)
                if err2:
                    st.error(err2)
                else:
                    st.success("✅ Job enqueued! The worker will generate questions in the background.")
                    st.markdown(f"""
                    <div class="job-result">
                        <div class="job-id-label">Job ID</div>
                        <div class="job-id-value">{result.get('job_id', '—')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.info(f"📌 Topic: **{result.get('topic')}** · Difficulty: **{result.get('difficulty')}** · Lesson ID: `{result.get('lesson_id')}`")


# ── Tab 2: Generate Full Course ───────────────────────────────────────────────

with tab2:
    st.markdown('<span class="info-chip">Creates a Course + Lesson + 3 Questions all at once via Groq</span>', unsafe_allow_html=True)

    with st.form("gen_course_form"):
        col1, col2 = st.columns(2)
        with col1:
            topic = st.text_input("Course Topic", placeholder="e.g. Spatial Pattern Recognition")
        with col2:
            difficulty = st.selectbox("Difficulty", DIFFICULTIES, key="course_diff", format_func=str.capitalize)

        submitted2 = st.form_submit_button("🚀 Generate Full Course", use_container_width=True, type="primary")

    if submitted2:
        if not topic.strip():
            st.warning("Please enter a topic.")
        else:
            with st.spinner("Enqueueing full course generation job..."):
                result, err3 = generate_course(topic.strip(), difficulty)
            if err3:
                st.error(err3)
            else:
                st.success("✅ Full course generation job enqueued!")
                st.markdown(f"""
                <div class="job-result">
                    <div class="job-id-label">Job ID</div>
                    <div class="job-id-value">{result.get('job_id', '—')}</div>
                </div>
                """, unsafe_allow_html=True)
                st.info(f"📌 Topic: **{result.get('topic')}** · Difficulty: **{result.get('difficulty')}**")
                st.caption("After the worker completes, the new course will appear in 📚 Courses.")


# ── Tab 3: Generate Lesson ──────────────────────────────────────────────────────

with tab3:
    st.markdown('<span class="info-chip">Creates a single AI Lesson and attaches it to an existing Course via Groq</span>', unsafe_allow_html=True)

    courses, err = get_courses()
    if err:
        st.error(err)
    elif not courses:
        st.info("Create a course first before generating a lesson.")
    else:
        course_map = {f"#{c['id']} — {c['title']}": c["id"] for c in courses}

        with st.form("gen_lesson_form"):
            col1, col2 = st.columns(2)
            with col1:
                topic = st.text_input("Lesson Topic", placeholder="e.g. Optical Illusions")
            with col2:
                chosen_course_label = st.selectbox("Attach to Course", list(course_map.keys()), key="lesson_course")
                course_id = course_map[chosen_course_label]

            difficulty = st.selectbox("Difficulty", DIFFICULTIES, key="lesson_diff", format_func=str.capitalize)

            submitted3 = st.form_submit_button("📝 Generate Lesson", use_container_width=True, type="primary")

        if submitted3:
            if not topic.strip():
                st.warning("Please enter a lesson topic.")
            else:
                with st.spinner("Enqueueing lesson generation job..."):
                    result, err5 = generate_lesson(topic.strip(), course_id, difficulty)
                if err5:
                    st.error(err5)
                else:
                    st.success("✅ Lesson generation job enqueued!")
                    st.markdown(f"""
                    <div class="job-result">
                        <div class="job-id-label">Job ID</div>
                        <div class="job-id-value">{result.get('job_id', '—')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.info(f"📌 Topic: **{result.get('topic')}** · Course ID: `{result.get('course_id')}`")
                    st.caption("After the worker completes, the new lesson will appear in 📖 Lessons.")


# ── Tab 4: Image Puzzle ────────────────────────────────────────────────────────

# Session state keys for the puzzle
for _k in ["puzzle_result", "puzzle_err", "puzzle_submitted", "puzzle_feedback", "puzzle_selected_opt"]:
    if _k not in st.session_state:
        st.session_state[_k] = None

with tab4:
    st.markdown('<span class="info-chip">Visual pattern puzzle — study the sequence and pick what comes next</span>', unsafe_allow_html=True)

    # ── Fetch form ────────────────────────────────────────────────────────────
    with st.form("image_puzzle_form"):
        cognitive_area = st.selectbox("Cognitive Area for Puzzle", COGNITIVE_AREAS)
        get_btn = st.form_submit_button("🖼️ Get Puzzle", use_container_width=True, type="primary")

    if get_btn:
        with st.spinner("Fetching puzzle..."):
            result, err4 = generate_image_puzzle(cognitive_area)
        st.session_state.puzzle_result    = result
        st.session_state.puzzle_err       = err4
        st.session_state.puzzle_submitted = False
        st.session_state.puzzle_feedback  = None
        st.session_state.puzzle_selected_opt = None

    BASE_URL = "http://localhost:8005"

    # ── Display puzzle ────────────────────────────────────────────────────────
    if st.session_state.puzzle_err:
        st.error(st.session_state.puzzle_err)

    elif st.session_state.puzzle_result:
        result = st.session_state.puzzle_result

        # Title + description
        st.markdown(f"### 🎯 {result.get('title', 'Puzzle')}")
        st.caption(result.get("description", ""))

        # Sequence strip image
        seq_url = result.get("image_url", "")
        if seq_url:
            full_seq = BASE_URL + seq_url if seq_url.startswith("/static") else seq_url
            st.markdown("**📊 Sequence (study carefully):**")
            st.image(full_seq, use_container_width=True)

        # Hint callout
        if result.get("hint"):
            st.info(f"💡 **Hint:** {result['hint']}")

        # Question
        st.markdown(f"**❓ {result.get('question', 'Which option comes next?')}**")
        st.markdown("---")

        options = result.get("options", [])

        # ── Option grid (2×2) ─────────────────────────────────────────────────
        if options:
            if not st.session_state.puzzle_submitted:
                st.markdown("**Select the correct option:**")

                # Show images in a 2×2 grid
                col_a, col_b = st.columns(2)
                col_c, col_d = st.columns(2)
                grid_cols = [col_a, col_b, col_c, col_d]
                opt_labels = []

                for i, opt in enumerate(options):
                    opt_id    = opt.get("id", chr(97 + i))
                    opt_label = f"Option {opt_id.upper()}"
                    opt_labels.append(opt_label)
                    opt_url = opt.get("image_url", "")
                    full_opt = BASE_URL + opt_url if opt_url.startswith("/static") else opt_url
                    with grid_cols[i]:
                        st.markdown(f"**{opt_label}**")
                        st.image(full_opt, width=160)

                st.markdown("<br>", unsafe_allow_html=True)

                # Radio selector
                selected_label = st.radio(
                    "Your answer:",
                    opt_labels,
                    horizontal=True,
                    key="puzzle_radio",
                )

                # Submit button (outside form so it doesn't re-fetch)
                if st.button("✅ Submit Answer", use_container_width=True, type="primary"):
                    # Map label → option id
                    sel_idx  = opt_labels.index(selected_label)
                    sel_id   = options[sel_idx].get("id", chr(97 + sel_idx))
                    puzzle_id = result.get("puzzle_id", 1)

                    with st.spinner("Checking your answer..."):
                        feedback, ferr = check_puzzle_answer(puzzle_id, sel_id)

                    if ferr:
                        st.error(ferr)
                    else:
                        st.session_state.puzzle_submitted    = True
                        st.session_state.puzzle_feedback     = feedback
                        st.session_state.puzzle_selected_opt = sel_id
                        st.rerun()

            else:
                # ── Results ───────────────────────────────────────────────────
                feedback = st.session_state.puzzle_feedback
                correct  = feedback.get("is_correct", False)
                correct_id = feedback.get("correct_option", "?").upper()
                msg = feedback.get("message", "")
                sel_id = st.session_state.puzzle_selected_opt

                if correct:
                    st.success(msg)
                else:
                    st.error(msg)

                # Show all options with correct highlighted
                st.markdown("**Answer Review:**")
                col_a, col_b = st.columns(2)
                col_c, col_d = st.columns(2)
                grid_cols = [col_a, col_b, col_c, col_d]

                for i, opt in enumerate(options):
                    opt_id    = opt.get("id", chr(97 + i))
                    opt_url   = opt.get("image_url", "")
                    full_opt  = BASE_URL + opt_url if opt_url.startswith("/static") else opt_url
                    is_right  = opt_id == feedback.get("correct_option", "")
                    is_chosen = opt_id == sel_id
                    badge = " ✅" if is_right else (" ❌" if is_chosen and not is_right else "")
                    with grid_cols[i]:
                        st.markdown(f"**Option {opt_id.upper()}{badge}**")
                        st.image(full_opt, width=160)

                st.markdown(f"💡 **Hint reminder:** {feedback.get('hint', '')}")

                if st.button("🔄 Try Another Puzzle", use_container_width=True):
                    st.session_state.puzzle_result    = None
                    st.session_state.puzzle_submitted = False
                    st.session_state.puzzle_feedback  = None
                    st.session_state.puzzle_selected_opt = None
                    st.rerun()

