# """
# AI Video/Meeting Assistant — Streamlit UI
# Wraps the existing run_pipeline() (transcription, summarization,
# extraction, and RAG chat) in a polished, professional web interface.
# """

# import os
# import tempfile
# from datetime import datetime

# import streamlit as st
# from dotenv import load_dotenv

# load_dotenv()

# from utils.audio_processing import process_input
# from core.transcriber import transcribe_all
# from core.summarize import summarize, generate_title
# from core.extractor import extract_action_items, extract_key_decisions, extract_questions
# from core.rag_engine import build_rag_chain, ask_questions

# # --------------------------------------------------------------------------
# # Page config
# # --------------------------------------------------------------------------
# st.set_page_config(
#     page_title="AI Meeting Assistant",
#     page_icon="🎙️",
#     layout="wide",
#     initial_sidebar_state="expanded",
# )

# # --------------------------------------------------------------------------
# # Styling
# # --------------------------------------------------------------------------
# st.markdown(
#     """
#     <style>
#         @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

#         html, body, [class*="css"] {
#             font-family: 'Inter', sans-serif;
#         }

#         :root {
#             --accent: #6C5CE7;
#             --accent-light: #A29BFE;
#             --bg-soft: #F7F7FC;
#             --card-border: #E7E5F5;
#         }

#         #MainMenu, footer, header

#         .block-container {
#             padding-top: 2rem;
#             padding-bottom: 3rem;
#             max-width: 1150px;
#         }

#         /* Hero header */
#         .hero {
#             background: linear-gradient(135deg, #6C5CE7 0%, #8E7CFF 55%, #A29BFE 100%);
#             border-radius: 20px;
#             padding: 2.2rem 2.5rem;
#             color: white;
#             margin-bottom: 1.8rem;
#             box-shadow: 0 12px 30px rgba(108, 92, 231, 0.25);
#         }
#         .hero h1 {
#             font-size: 1.9rem;
#             font-weight: 800;
#             margin: 0 0 0.3rem 0;
#         }
#         .hero p {
#             font-size: 0.98rem;
#             opacity: 0.9;
#             margin: 0;
#         }

#         /* Cards */
#         .card {
#             background: white;
#             border: 1px solid var(--card-border);
#             border-radius: 16px;
#             padding: 1.4rem 1.6rem;
#             box-shadow: 0 2px 10px rgba(30, 20, 90, 0.04);
#             margin-bottom: 1rem;
#         }
#         .card h4 {
#             margin-top: 0;
#             color: #2D2A4A;
#             font-weight: 700;
#         }
#         .meta-title {
#             font-size: 1.5rem;
#             font-weight: 800;
#             color: #2D2A4A;
#         }

#         /* Sidebar */
#         section[data-testid="stSidebar"] {
#             background: var(--bg-soft);
#             border-right: 1px solid var(--card-border);
#         }
#         section[data-testid="stSidebar"] .stButton button {
#             background: var(--accent);
#             color: white;
#             border: none;
#             border-radius: 10px;
#             font-weight: 600;
#             padding: 0.6rem 1rem;
#             width: 100%;
#             transition: 0.2s;
#         }
#         section[data-testid="stSidebar"] .stButton button:hover {
#             background: #5847d9;
#             box-shadow: 0 4px 14px rgba(108, 92, 231, 0.35);
#         }

#         /* Chat bubbles */
#         .chat-user {
#             background: var(--accent);
#             color: white;
#             padding: 0.7rem 1rem;
#             border-radius: 14px 14px 2px 14px;
#             margin: 0.3rem 0;
#             max-width: 80%;
#             margin-left: auto;
#         }
#         .chat-assistant {
#             background: var(--bg-soft);
#             border: 1px solid var(--card-border);
#             color: #2D2A4A;
#             padding: 0.7rem 1rem;
#             border-radius: 14px 14px 14px 2px;
#             margin: 0.3rem 0;
#             max-width: 80%;
#         }

#         .status-pill {
#             display: inline-block;
#             background: #E8F8EE;
#             color: #1E8E4F;
#             padding: 0.2rem 0.7rem;
#             border-radius: 20px;
#             font-size: 0.78rem;
#             font-weight: 600;
#         }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )

# # --------------------------------------------------------------------------
# # Session state
# # --------------------------------------------------------------------------
# defaults = {
#     "result": None,
#     "chat_history": [],
#     "processing": False,
#     "processed_at": None,
#     "upload_temp_path": None,
#     "upload_token": None,
# }
# for key, val in defaults.items():
#     if key not in st.session_state:
#         st.session_state[key] = val


# def cleanup_uploaded_temp() -> None:
#     """Remove this session's cached upload file, if one exists."""
#     temp_path = st.session_state.get("upload_temp_path")
#     if temp_path and os.path.isfile(temp_path):
#         try:
#             os.remove(temp_path)
#         except OSError:
#             pass
#     st.session_state.upload_temp_path = None
#     st.session_state.upload_token = None


# def persist_uploaded_file(uploaded_file) -> str:
#     """Save an uploaded file once per upload rather than once per rerun."""
#     token = (
#         getattr(uploaded_file, "file_id", None),
#         uploaded_file.name,
#         uploaded_file.size,
#     )
#     existing_path = st.session_state.get("upload_temp_path")
#     if (
#         token == st.session_state.get("upload_token")
#         and existing_path
#         and os.path.isfile(existing_path)
#     ):
#         return existing_path

#     cleanup_uploaded_temp()
#     suffix = os.path.splitext(uploaded_file.name)[1]
#     with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
#         temp_file.write(uploaded_file.getvalue())

#     st.session_state.upload_temp_path = temp_file.name
#     st.session_state.upload_token = token
#     return temp_file.name

# # --------------------------------------------------------------------------
# # Pipeline runner (mirrors main.py's run_pipeline, with UI progress)
# # --------------------------------------------------------------------------
# def run_pipeline_with_progress(source: str, language: str) -> dict:
#     progress = st.progress(0, text="Starting AI assistant…")
#     try:
#         progress.progress(10, text="Reading and chunking source audio…")
#         chunks = process_input(source)

#         progress.progress(35, text="Transcribing audio…")
#         transcript = transcribe_all(chunks, language=language)

#         progress.progress(55, text="Generating title…")
#         title = generate_title(transcript)

#         progress.progress(65, text="Summarizing transcript…")
#         summary = summarize(transcript)

#         progress.progress(75, text="Extracting action items…")
#         action_items = extract_action_items(transcript)

#         progress.progress(82, text="Extracting key decisions…")
#         key_decisions = extract_key_decisions(transcript)

#         progress.progress(89, text="Extracting open questions…")
#         questions = extract_questions(transcript)

#         progress.progress(96, text="Building chat engine (RAG)…")
#         rag_chain = build_rag_chain(transcript)

#         progress.progress(100, text="Done!")
#         return {
#             "title": title,
#             "transcript": transcript,
#             "summary": summary,
#             "action_items": action_items,
#             "key_decisions": key_decisions,
#             "open_questions": questions,
#             "rag_chain": rag_chain,
#         }
#     finally:
#         progress.empty()


# # --------------------------------------------------------------------------
# # Sidebar — input controls
# # --------------------------------------------------------------------------
# with st.sidebar:
#     st.markdown("### 🎙️ New Session")
#     st.caption("Provide a YouTube link or upload a local audio/video file.")

#     input_mode = st.radio("Source type", ["YouTube URL", "Upload File"], horizontal=True)

#     source_value = None
#     if input_mode == "YouTube URL":
#         cleanup_uploaded_temp()
#         source_value = st.text_input("YouTube URL", placeholder="https://youtube.com/watch?v=…")
#     else:
#         uploaded_file = st.file_uploader(
#             "Upload audio/video",
#             type=["mp3", "wav", "m4a", "mp4", "mov", "mkv"],
#             key="source_upload",
#         )
#         if uploaded_file is not None:
#             source_value = persist_uploaded_file(uploaded_file)
#             st.caption(f"📁 Ready: {uploaded_file.name}")
#         else:
#             cleanup_uploaded_temp()

#     language = st.selectbox("Language", ["english", "hinglish"], index=0)

#     st.divider()
#     run_clicked = st.button("🚀 Run Analysis", use_container_width=True, disabled=not source_value)

#     if st.session_state.result:
#         st.divider()
#         st.markdown(
#             f'<span class="status-pill">✅ Processed at '
#             f'{st.session_state.processed_at}</span>',
#             unsafe_allow_html=True,
#         )
#         if st.button("🗑️ Clear Session", use_container_width=True):
#             st.session_state.result = None
#             st.session_state.chat_history = []
#             st.session_state.processed_at = None
#             cleanup_uploaded_temp()
#             st.rerun()

# # --------------------------------------------------------------------------
# # Header
# # --------------------------------------------------------------------------
# st.markdown(
#     """
#     <div class="hero">
#         <h1>🎙️ AI Meeting &amp; Video Assistant</h1>
#         <p>Transcribe, summarize, extract action items, and chat with any meeting or video — powered by your GenAI pipeline.</p>
#     </div>
#     """,
#     unsafe_allow_html=True,
# )

# # --------------------------------------------------------------------------
# # Run pipeline
# # --------------------------------------------------------------------------
# if run_clicked and source_value:
#     st.session_state.chat_history = []
#     with st.spinner("Processing your source — this can take a bit for longer recordings…"):
#         try:
#             result = run_pipeline_with_progress(source_value, language)
#             st.session_state.result = result
#             st.session_state.processed_at = datetime.now().strftime("%b %d, %Y · %H:%M")
#             st.success("Analysis complete! Scroll down to explore results and chat.")
#         except Exception as e:
#             st.error(f"Something went wrong while processing your source:\n\n**{e}**")

# # --------------------------------------------------------------------------
# # Results
# # --------------------------------------------------------------------------
# result = st.session_state.result

# if not result:
#     st.info("👈 Add a YouTube URL or upload a file in the sidebar, then click **Run Analysis** to get started.")
#     st.markdown("### 💬 Chat with your video")
#     st.caption("Run an analysis first. Then ask questions about the transcript here.")
# else:
#     st.markdown(f'### 📌 {result["title"]}')
#     st.caption("Ask questions about this video or meeting. Answers use its transcript.")

#     # Keep the conversation as the primary view, like a standard chatbot.
#     if not st.session_state.chat_history:
#         with st.chat_message("assistant"):
#             st.markdown("Analysis is ready. What would you like to know about this conversation?")

#     for msg in st.session_state.chat_history:
#         with st.chat_message(msg["role"]):
#             st.markdown(msg["content"])

#     question = st.chat_input("Message about this video…", key="meeting_chat_input")
#     if question:
#         st.session_state.chat_history.append({"role": "user", "content": question})
#         with st.chat_message("user"):
#             st.markdown(question)
#         with st.chat_message("assistant"):
#             with st.spinner("Thinking…"):
#                 try:
#                     answer = ask_questions(result["rag_chain"], question)
#                 except Exception as e:
#                     answer = f"⚠️ Error getting an answer: {e}"
#             st.markdown(answer)
#         st.session_state.chat_history.append({"role": "assistant", "content": answer})

#     with st.expander("📋 Analysis results", expanded=False):
#         st.markdown("#### Summary")
#         st.markdown(result["summary"])
#         st.markdown("#### Action items")
#         st.markdown(result["action_items"])
#         st.markdown("#### Key decisions")
#         st.markdown(result["key_decisions"])
#         st.markdown("#### Open questions")
#         st.markdown(result["open_questions"])
#         with st.expander("Full transcript"):
#             st.write(result["transcript"])
# app.py

import os
import sys
import tempfile
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Handle UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Import your existing project modules
from utils.audio_processing import process_input
from core.transcriber import transcribe_all
from core.summarize import summarize, generate_title
from core.extractor import (
    extract_action_items,
    extract_key_decisions,
    extract_questions,
)
from core.rag_engine import build_rag_chain, ask_questions


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI Video & Meeting Assistant",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# PIPELINE
# --------------------------------------------------

def run_pipeline(source: str, language: str = "english") -> dict:
    """Process a video/audio source and prepare meeting insights."""

    chunks = process_input(source)

    transcript = transcribe_all(chunks, language=language)

    title = generate_title(transcript)
    summary = summarize(transcript)
    action_items = extract_action_items(transcript)
    key_decisions = extract_key_decisions(transcript)
    questions = extract_questions(transcript)

    rag_chain = build_rag_chain(transcript)

    return {
        "title": title,
        "transcript": transcript,
        "summary": summary,
        "action_items": action_items,
        "key_decisions": key_decisions,
        "open_questions": questions,
        "rag_chain": rag_chain,
    }


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "result" not in st.session_state:
    st.session_state.result = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        .main-title {
            font-size: 2.3rem;
            font-weight: 750;
            margin-bottom: 0.2rem;
        }

        .subtitle {
            color: #9CA3AF;
            font-size: 1rem;
            margin-bottom: 1.5rem;
        }

        div[data-testid="stMetric"] {
            background-color: rgba(128, 128, 128, 0.08);
            border: 1px solid rgba(128, 128, 128, 0.2);
            padding: 15px;
            border-radius: 12px;
        }

        div[data-testid="stChatMessage"] {
            border-radius: 12px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.title("🎙️ AI Assistant")
    st.caption("Your personal video and meeting companion")

    st.divider()

    st.subheader("⚙️ Settings")

    language = st.selectbox(
        "Transcription language",
        options=["english", "hinglish"],
        format_func=lambda x: {
            "english": "English",
            "hinglish": "Hinglish",
        }[x],
    )

    st.info(
        "Enter a YouTube URL or upload a local audio/video file "
        "to generate meeting insights."
    )

    if st.button("🗑️ Clear Session", use_container_width=True):
        st.session_state.result = None
        st.session_state.chat_history = []
        st.rerun()

    st.divider()

    st.caption("AI Video & Meeting Assistant")


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    '<div class="main-title">🎬 AI Video & Meeting Assistant</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'Summarize videos, extract action items, identify decisions, '
    'and chat with your meeting.'
    '</div>',
    unsafe_allow_html=True,
)


# --------------------------------------------------
# INPUT SECTION
# --------------------------------------------------

st.subheader("📥 Add a video or meeting recording")

input_mode = st.radio(
    "Choose your input method",
    ["YouTube URL", "Upload Audio/Video"],
    horizontal=True,
)

source = None
uploaded_file = None

if input_mode == "YouTube URL":

    youtube_url = st.text_input(
        "YouTube video URL",
        placeholder="https://www.youtube.com/watch?v=...",
    )

    if youtube_url.strip():
        source = youtube_url.strip()

else:

    uploaded_file = st.file_uploader(
        "Upload an audio or video file",
        type=[
            "mp3",
            "wav",
            "m4a",
            "aac",
            "ogg",
            "flac",
            "mp4",
            "mov",
            "mkv",
            "webm",
            "mpeg",
            "mpga",
        ],
        help="Upload a supported audio or video recording.",
    )


# --------------------------------------------------
# PROCESSING
# --------------------------------------------------

if st.button(
    "🚀 Process Recording",
    type="primary",
    use_container_width=True,
):

    if input_mode == "YouTube URL" and not source:
        st.warning("Please enter a YouTube URL.")

    elif input_mode == "Upload Audio/Video" and uploaded_file is None:
        st.warning("Please upload an audio or video file.")

    else:

        temp_path = None

        try:
            if input_mode == "Upload Audio/Video":

                # Save the uploaded file temporarily so that
                # process_input can receive a local file path.
                suffix = os.path.splitext(uploaded_file.name)[1]

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=suffix,
                ) as temp_file:

                    temp_file.write(uploaded_file.getvalue())
                    temp_path = temp_file.name

                source = temp_path

            # Clear old results before processing a new source.
            st.session_state.result = None
            st.session_state.chat_history = []

            with st.spinner(
                "Processing your recording... This may take a few minutes."
            ):

                result = run_pipeline(source, language=language)

            st.session_state.result = result

            st.success("Your recording has been processed successfully!")
            st.rerun()

        except Exception as e:
            st.error(f"Processing failed: {str(e)}")

            with st.expander("Technical error details"):
                st.exception(e)

        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass


# --------------------------------------------------
# RESULTS DASHBOARD
# --------------------------------------------------

if st.session_state.result is not None:

    result = st.session_state.result

    st.divider()

    st.header(f"📌 {result['title']}")

    # Summary metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Status", "Completed")

    with col2:
        transcript_text = str(result["transcript"])
        st.metric(
            "Transcript length",
            f"{len(transcript_text):,} characters",
        )

    with col3:
        st.metric(
            "Language",
            language.capitalize(),
        )

    st.divider()

    # Tabs for meeting insights
    summary_tab, transcript_tab, actions_tab, decisions_tab, questions_tab = (
        st.tabs(
            [
                "📝 Summary",
                "📄 Transcript",
                "✅ Action Items",
                "🔑 Key Decisions",
                "❓ Open Questions",
            ]
        )
    )

    with summary_tab:
        st.subheader("Meeting Summary")
        st.markdown(str(result["summary"]))

    with transcript_tab:
        st.subheader("Full Transcript")

        st.text_area(
            "Transcript",
            value=transcript_text,
            height=450,
            disabled=True,
            label_visibility="collapsed",
        )

        st.download_button(
            label="⬇️ Download Transcript",
            data=transcript_text,
            file_name="meeting_transcript.txt",
            mime="text/plain",
        )

    with actions_tab:
        st.subheader("Action Items")
        st.markdown(str(result["action_items"]))

    with decisions_tab:
        st.subheader("Key Decisions")
        st.markdown(str(result["key_decisions"]))

    with questions_tab:
        st.subheader("Open Questions")
        st.markdown(str(result["open_questions"]))

    # --------------------------------------------------
    # CHAT WITH YOUR MEETING
    # --------------------------------------------------

    st.divider()

    st.header("💬 Chat with Your Meeting")

    st.caption(
        "Ask questions about the recording, its decisions, "
        "important points, or action items."
    )

    # Display previous messages
    for message in st.session_state.chat_history:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    user_question = st.chat_input(
        "Ask something about your meeting..."
    )

    if user_question and user_question.strip():

        question = user_question.strip()

        # Display and store the user's message
        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": question,
            }
        )

        with st.chat_message("user"):
            st.markdown(question)

        # Ask the existing RAG pipeline
        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                try:
                    answer = ask_questions(
                        result["rag_chain"],
                        question,
                    )

                    answer = str(answer)

                    st.markdown(answer)

                    st.session_state.chat_history.append(
                        {
                            "role": "assistant",
                            "content": answer,
                        }
                    )

                except Exception as e:

                    error_message = (
                        f"Sorry, I couldn't answer that question. "
                        f"Error: {str(e)}"
                    )

                    st.error(error_message)

                    st.session_state.chat_history.append(
                        {
                            "role": "assistant",
                            "content": error_message,
                        }
                    )

else:

    # Empty state shown before processing
    st.divider()

    st.markdown(
        """
        ### 👋 Welcome!

        Get started by providing a YouTube URL or uploading a recording.

        **Your assistant will generate:**

        - 📝 An AI-generated summary
        - 📄 A complete transcript
        - ✅ Action items and tasks
        - 🔑 Key decisions
        - ❓ Unresolved questions
        - 💬 An interactive chatbot powered by your RAG pipeline
        """
    )

    st.caption(
        "Tip: Longer recordings may take more time to transcribe "
        "and analyze, depending on your models and API response times."
    )
