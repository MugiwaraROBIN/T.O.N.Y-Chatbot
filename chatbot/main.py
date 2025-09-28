import streamlit as st
import os
from datetime import datetime
import time
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import PyPDF2
from io import BytesIO

# Load environment variables
load_dotenv()

# Page configuration - minimal sidebar for Claude-like experience
st.set_page_config(
    page_title="T.O.N.Y",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"  # Start with collapsed sidebar
)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'context_messages' not in st.session_state:
    st.session_state.context_messages = []
if 'model_provider' not in st.session_state:
    st.session_state.model_provider = "⚡ Groq Llama 3.1 8B (FASTEST)"
if 'sidebar_collapsed' not in st.session_state:
    st.session_state.sidebar_collapsed = True

# Claude-inspired CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

    .main {
        font-family: 'Inter', sans-serif;
        background: #f9fafb;
    }
    .block-container {
        max-width: 850px !important;
        margin: auto !important;
        padding-top: 1rem !important;
    }

    /* Hide Streamlit branding */
    #MainMenu, footer, .stDeployButton {visibility: hidden;}

    /* Chat bubbles */
    .chat-container {
        display: flex;
        flex-direction: column;
        margin-bottom: 1rem;
    }
    .message-user {
        align-self: flex-end;
        background: #2563eb;
        color: #fff;
        padding: 0.9rem 1.2rem;
        border-radius: 16px 16px 4px 16px;
        max-width: 70%;
        font-size: 0.95rem;
        line-height: 1.5;
        animation: fadeIn 0.3s ease-in-out;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }
    .message-assistant {
        align-self: flex-start;
        background: #f3f4f6;
        color: #111827;
        padding: 0.9rem 1.2rem;
        border-radius: 16px 16px 16px 4px;
        max-width: 70%;
        font-size: 0.95rem;
        line-height: 1.6;
        animation: fadeIn 0.3s ease-in-out;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }
    .message-meta {
        font-size: 0.75rem;
        opacity: 0.7;
        margin-bottom: 0.4rem;
    }

    /* Input bar fixed at bottom */
    .stTextInput input {
        border-radius: 12px !important;
        border: 2px solid #d1d5db !important;
        padding: 0.9rem 1.2rem !important;
        font-size: 0.95rem !important;
    }
    .stTextInput input:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37,99,235,0.1) !important;
    }

    .stButton button {
        background: #2563eb !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 0.7rem 1.4rem !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    .stButton button:hover {
        background: #1d4ed8 !important;
        transform: scale(1.04);
        box-shadow: 0 3px 8px rgba(37,99,235,0.25);
    }

    /* Smooth fade */
    @keyframes fadeIn {
        from {opacity: 0; transform: translateY(5px);}
        to {opacity: 1; transform: translateY(0);}
    }

    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 3rem 2rem;
        background: white;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        margin: 2rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .empty-state-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }
    .empty-state-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .empty-state-text {
        font-size: 0.9rem;
        color: #6b7280;
    }
</style>

""", unsafe_allow_html=True)

# Claude-style header with hamburger menu
st.markdown("""
<div class="claude-header">
    <div>
        <div class="claude-title">
            🤖 T.O.N.Y
        </div>
        <div class="claude-subtitle">Text-Oriented Neural Yield</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Collapsible sidebar with Claude-style controls
with st.sidebar:
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)

    # Status indicator
    st.markdown("""
    <div class="status-indicator">
        <div class="status-dot"></div>
        <div class="status-text">T.O.N.Y Online</div>
    </div>
    """, unsafe_allow_html=True)

    # Model selection section
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">Model Selection</div>', unsafe_allow_html=True)

    model_provider = st.selectbox(
        "",
        ["⚡ Groq Llama 3.1 8B (FASTEST)", "🧠 Groq Llama 3.3 70B (BEST)", "⚖️ Groq Gemma2 9B (BALANCED)",
         "OpenAI GPT-3.5", "OpenAI GPT-4"],
        index=0,
        label_visibility="collapsed"
    )
    st.session_state.model_provider = model_provider

    # Model mapping
    model_map = {
        "⚡ Groq Llama 3.1 8B (FASTEST)": ("groq", "llama-3.1-8b-instant"),
        "🧠 Groq Llama 3.3 70B (BEST)": ("groq", "llama-3.3-70b-versatile"),
        "⚖️ Groq Gemma2 9B (BALANCED)": ("groq", "gemma2-9b-it"),
        "OpenAI GPT-3.5": ("openai", "gpt-3.5-turbo"),
        "OpenAI GPT-4": ("openai", "gpt-4")
    }

    provider, model_name = model_map[model_provider]
    st.markdown('</div>', unsafe_allow_html=True)

    # Settings section
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">Settings</div>', unsafe_allow_html=True)

    temperature = st.slider("Creativity", 0.0, 1.0, 0.7, 0.1, label_visibility="visible")
    max_context = st.slider("Context Memory", 1, 5, 3, label_visibility="visible")
    enable_context = st.checkbox("Enable Chat Context", value=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Statistics section
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">Session Stats</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{len(st.session_state.chat_history)}</div>
        <div class="metric-label">Messages</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{len(st.session_state.context_messages)}</div>
        <div class="metric-label">Context Size</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{model_name.upper()}</div>
        <div class="metric-label">Current Model</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Clear chat section
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    if st.button("Clear Conversation", type="secondary", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.context_messages = []
        st.success("Conversation cleared!")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# Document processing function
def process_document(file):
    try:
        if file.type == "application/pdf":
            reader = PyPDF2.PdfReader(BytesIO(file.read()))
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text[:8000]
        else:
            return str(file.read(), "utf-8")[:8000]
    except Exception as e:
        st.error(f"Error processing document: {str(e)}")
        return None


# LLM initialization with speed optimization
@st.cache_resource
def get_llm(provider, model, temp):
    try:
        if provider == "groq":
            return ChatGroq(
                groq_api_key=os.getenv("GROQ_API_KEY"),
                model_name=model,
                temperature=temp,
                max_tokens=500,
                request_timeout=30
            )
        elif provider == "openai":
            return ChatOpenAI(
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                model=model,
                temperature=temp,
                max_tokens=500,
                request_timeout=30
            )
    except Exception as e:
        st.error(f"Error initializing LLM: {str(e)}")
        return None


# Enhanced prompt with context
def create_contextual_prompt():
    context_str = ""
    if enable_context and st.session_state.context_messages:
        context_str = "\n\nPrevious conversation context:\n"
        for msg in st.session_state.context_messages[-max_context:]:
            context_str += f"User: {msg['user']}\nAssistant: {msg['assistant']}\n\n"

    return ChatPromptTemplate.from_messages([
        ("system", f"""You are T.O.N.Y (Text-Oriented Neural Yield), an advanced AI assistant. You are helpful, intelligent, and conversational. Provide clear, well-structured responses that are both informative and engaging.

        Key traits:
        - Be concise but thorough
        - Use markdown formatting when appropriate
        - Suggest visual aids when helpful
        - Maintain conversation flow naturally
        - Be professional yet approachable

        {context_str}"""),
        ("user", "{question}")
    ])


# File upload section
uploaded_file = st.file_uploader(
    "📎 Attach a document (PDF, TXT)",
    type=['pdf', 'txt'],
    help="Upload documents for analysis and discussion",
    label_visibility="visible"
)

# Main chat input - Claude style
st.markdown("### Send a message")
user_input = st.text_input(
    "",
    placeholder="Message T.O.N.Y...",
    key="user_input",
    label_visibility="collapsed"
)

# Send button
send_button = st.button("Send", type="primary", use_container_width=False)

# Process input
if user_input and send_button:
    try:
        # Add document context if available
        context = ""
        if uploaded_file:
            doc_content = process_document(uploaded_file)
            if doc_content:
                context = f"\n\nDocument content: {doc_content}"

        # Show loading animation - Claude style
        loading_placeholder = st.empty()
        with loading_placeholder.container():
            st.markdown("""
            <div class="loading-container">
                <div class="loading-dots">
                    <div class="loading-dot"></div>
                    <div class="loading-dot"></div>
                    <div class="loading-dot"></div>
                </div>
                <div class="loading-text">T.O.N.Y is thinking...</div>
            </div>
            """, unsafe_allow_html=True)

        # Get LLM and generate response
        llm = get_llm(provider, model_name, temperature)

        if llm:
            prompt = create_contextual_prompt()
            chain = prompt | llm | StrOutputParser()

            enhanced_question = user_input + context
            response = chain.invoke({"question": enhanced_question})

            # Clear loading
            loading_placeholder.empty()

            # Add to chat history
            timestamp = datetime.now().strftime("%H:%M")
            chat_entry = {
                "user": user_input,
                "assistant": response,
                "timestamp": timestamp,
                "model": model_name
            }

            st.session_state.chat_history.append(chat_entry)

            # Update context
            if enable_context:
                st.session_state.context_messages.append({
                    "user": user_input,
                    "assistant": response[:500]
                })

            # Clear input and refresh
            st.rerun()
        else:
            loading_placeholder.empty()
            st.error("Could not initialize AI model. Please check your API keys.")

    except Exception as e:
        loading_placeholder.empty()
        st.error(f"Error: {str(e)}")

# Display chat history - Claude style
if st.session_state.chat_history:
    st.markdown("---")

    for i, chat in enumerate(reversed(st.session_state.chat_history)):
        st.markdown(f"""
        <div class="chat-container">
            <div class="message-user">
                <div class="message-meta">You • {chat['timestamp']}</div>
                {chat['user']}
            </div>
            <div class="message-assistant">
                <div class="message-meta">T.O.N.Y • {chat['model']}</div>
                {chat['assistant']}
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    # Empty state
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">💬</div>
        <div class="empty-state-title">Start a conversation</div>
        <div class="empty-state-text">
            Ask me anything! I can help with explanations, analysis, coding, writing, and more.
            <br>Try: "Explain quantum computing" or upload a document to discuss.
        </div>
    </div>
    """, unsafe_allow_html=True)