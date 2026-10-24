# 🤖 AI Meeting Assistant — RAG-Based Meeting Intelligence

An AI-powered meeting assistant that converts meeting audio into structured, searchable information. It transcribes conversations, generates summaries, extracts action items and key decisions, and enables users to ask questions about meeting content using Retrieval-Augmented Generation (RAG).

## 📌 Overview

The AI Meeting Assistant simplifies meeting management by automating the process of understanding and organizing meeting discussions. Instead of manually reviewing long recordings or transcripts, users can obtain concise summaries, identify important decisions, track action items, and interact with meeting content through a conversational interface.

The application combines speech-to-text processing, Large Language Models (LLMs), and RAG to provide an efficient way to retrieve relevant information from meeting transcripts.

## ✨ Features

- **Audio Processing:** Processes uploaded meeting audio files.
- **Speech-to-Text Transcription:** Converts spoken conversations into text using OpenAI Whisper and Sarvam AI.
- **AI-Powered Summarization:** Generates concise summaries of meeting discussions.
- **Action Item Extraction:** Identifies tasks and follow-up activities discussed during meetings.
- **Key Decision Extraction:** Highlights important decisions made during discussions.
- **Question Extraction:** Identifies important questions raised during meetings.
- **Automatic Meeting Titles:** Generates meaningful titles for meeting sessions.
- **Conversational Q&A:** Allows users to ask questions about meeting transcripts using RAG.
- **Interactive UI:** Provides a user-friendly interface built with Streamlit.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Streamlit | Interactive web interface |
| LangChain | LLM orchestration and RAG pipeline |
| Mistral AI | Language model for summarization and question answering |
| OpenAI Whisper | Speech-to-text transcription |
| Sarvam AI | Speech processing and transcription support |
| Vector Store | Stores and retrieves relevant transcript chunks |
| Python-dotenv | Environment variable management |

## 🏗️ System Architecture

The application follows a modular pipeline:

1. **Audio Input:** The user uploads a meeting recording.
2. **Audio Processing:** The recording is processed into a suitable format for transcription.
3. **Transcription:** Speech recognition models convert the audio into text.
4. **Information Extraction:** The LLM generates a summary, meeting title, action items, key decisions, and questions.
5. **RAG Pipeline:** The transcript is divided into chunks, converted into embeddings, and indexed in a vector store.
6. **Context Retrieval:** When a user asks a question, the system retrieves relevant transcript chunks.
7. **Answer Generation:** The retrieved context is passed to the LLM to generate a context-aware response.
8. **Output:** Results are displayed through the Streamlit interface.

## 🔄 How RAG Works

Retrieval-Augmented Generation (RAG) combines information retrieval with text generation.

- **Chunking:** The transcript is divided into smaller text segments.
- **Embedding:** Each segment is represented as a numerical vector.
- **Indexing:** The vectors are stored in a searchable vector database.
- **Retrieval:** Relevant segments are retrieved based on the user's question.
- **Generation:** Mistral AI uses the retrieved context to generate an answer.

This approach helps users retrieve specific information from long meetings without manually searching the entire transcript.

## 📂 Project Structure

```text
AI-Meeting-Assistant/
│
├── app.py
├── main.py
├── requirements.txt
├── .env
│
├── core/
│   ├── transcriber.py
│   ├── summarize.py
│   ├── extractor.py
│   └── rag_engine.py
│
├── utils/
│   └── audio_processing.py
│
└── README.md
```

*Note: Adjust the file names and structure to match your actual repository.*

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd AI-Meeting-Assistant
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment:

**Windows**
```bash
venv\Scripts\activate
```

**macOS / Linux**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root and add the API credentials required by your implementation.

```env
MISTRAL_API_KEY=your_mistral_api_key
SARVAM_API_KEY=your_sarvam_api_key
OPENAI_API_KEY=your_openai_api_key
```

Only configure the keys used by your actual code. Never commit API keys or other secrets to GitHub.

### 5. Run the Application

If your Streamlit entry point is `app.py`, run:

```bash
streamlit run app.py
```

If your application uses `main.py` instead, run:

```bash
streamlit run main.py
```

Open the local URL displayed in the terminal to access the application.

## 💡 Use Cases

- Generating meeting summaries after team discussions.
- Tracking assigned tasks and follow-up activities.
- Reviewing decisions made during project meetings.
- Finding specific information in lengthy meeting recordings.
- Answering questions about previous discussions.
- Improving productivity by reducing manual note-taking.

## 🚀 Future Improvements

- Speaker diarization to identify who said what.
- Timestamp-based retrieval of meeting information.
- Persistent storage of multiple meetings.
- Search across multiple meeting transcripts.
- Export summaries and action items to PDF.
- Integration with Google Meet, Zoom, or Microsoft Teams.
- Support for multilingual meetings and improved language detection.

## 🎯 Key Learning Outcomes

- Building an end-to-end AI application using Python.
- Integrating speech recognition with LLM-based workflows.
- Implementing Retrieval-Augmented Generation using LangChain.
- Designing modular components for transcription, summarization, extraction, and retrieval.
- Connecting external AI APIs to a Streamlit application.
- Developing a conversational interface for document-based question answering.

## 👨‍💻 Author

**Raunak Gupta**

Mechanical Engineering | MNIT Jaipur

[GitHub](<your-github-profile-url>)

---

*Built to make meeting information easier to capture, understand, search, and act upon.*
