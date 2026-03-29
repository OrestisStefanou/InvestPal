import streamlit as st
import requests
import uuid
import time

# How to run this
# 1. Activate the virtual environment
# 2. streamlit run app.py

# ── Config ──────────────────────────────────────────────────────────────────
BASE_URL = "http://localhost:8000"
USER_ID = "test_user_2"

st.set_page_config(
    page_title="InvestPal · Dev Console",
    page_icon="📈",
    layout="wide",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Syne:wght@400;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
}

/* Dark background */
.stApp {
    background-color: #0d0f14;
    color: #e8e6df;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #111318;
    border-right: 1px solid #1e2128;
}

/* Header bar */
.header-bar {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0 0 24px 0;
    border-bottom: 1px solid #1e2128;
    margin-bottom: 24px;
}
.header-bar h1 {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1.6rem;
    color: #f0ede6;
    margin: 0;
    letter-spacing: -0.5px;
}
.header-bar .badge {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    background: #c8f542;
    color: #0d0f14;
    padding: 3px 8px;
    border-radius: 3px;
    font-weight: 600;
    letter-spacing: 0.05em;
}

/* Session pill */
.session-pill {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: #6b7280;
    background: #161920;
    border: 1px solid #1e2128;
    border-radius: 4px;
    padding: 6px 12px;
    margin-bottom: 20px;
    word-break: break-all;
}
.session-pill span {
    color: #c8f542;
}

/* Chat messages */
.user-msg {
    background: #161920;
    border: 1px solid #1e2128;
    border-radius: 8px 8px 2px 8px;
    padding: 14px 18px;
    margin: 8px 0;
    margin-left: 60px;
    font-size: 0.92rem;
    color: #e8e6df;
}
.agent-msg {
    background: #13161d;
    border: 1px solid #1e2128;
    border-left: 3px solid #c8f542;
    border-radius: 2px 8px 8px 8px;
    padding: 14px 18px;
    margin: 8px 0;
    margin-right: 60px;
    font-size: 0.92rem;
    color: #e8e6df;
}
.msg-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    margin-bottom: 6px;
    opacity: 0.5;
    text-transform: uppercase;
}

/* Input area */
.stTextInput > div > div > input {
    background-color: #161920 !important;
    border: 1px solid #1e2128 !important;
    border-radius: 6px !important;
    color: #e8e6df !important;
    font-family: 'Syne', sans-serif !important;
}
.stTextInput > div > div > input:focus {
    border-color: #c8f542 !important;
    box-shadow: 0 0 0 1px #c8f54240 !important;
}

/* Buttons */
.stButton > button {
    background: #c8f542 !important;
    color: #0d0f14 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 8px 20px !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.02em;
}
.stButton > button:hover {
    background: #d9f96a !important;
    transform: translateY(-1px);
    transition: all 0.15s ease;
}

/* Sidebar labels */
.sidebar-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #4b5563;
    margin-bottom: 6px;
}

/* Status dot */
.status-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #c8f542;
    margin-right: 6px;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

/* Divider */
hr {
    border-color: #1e2128 !important;
}

/* Metric cards */
.metric-card {
    background: #161920;
    border: 1px solid #1e2128;
    border-radius: 6px;
    padding: 12px 16px;
    margin-bottom: 10px;
}
.metric-card .metric-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.1rem;
    color: #c8f542;
    font-weight: 600;
}
.metric-card .metric-label {
    font-size: 0.7rem;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-family: 'IBM Plex Mono', monospace;
}

/* Scrollable chat area */
.chat-container {
    max-height: 60vh;
    overflow-y: auto;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ── Helpers ──────────────────────────────────────────────────────────────────

def ensure_user_context():
    """Create user context if it doesn't exist yet."""
    try:
        r = requests.post(
            f"{BASE_URL}/user_context",
            json={"user_id": USER_ID},
            timeout=5,
        )
        # 409 = already exists, that's fine
        return r.status_code in (200, 201, 409)
    except Exception as e:
        st.error(f"Could not reach backend: {e}")
        return False


def create_session(session_id: str) -> bool:
    try:
        r = requests.post(
            f"{BASE_URL}/session",
            json={"user_id": USER_ID, "session_id": session_id},
            timeout=5,
        )
        return r.status_code in (200, 201)
    except Exception as e:
        st.error(f"Session creation failed: {e}")
        return False


def send_message(session_id: str, message: str) -> str | None:
    try:
        r = requests.post(
            f"{BASE_URL}/chat",
            json={"session_id": session_id, "message": message},
            timeout=600,
        )
        if r.status_code == 200:
            return r.json().get("response", "")
        else:
            return f"**Error {r.status_code}**: {r.text}"
    except Exception as e:
        return f"**Connection error**: {e}"


def stream_text(text: str):
    """Yield characters with a tiny delay to simulate streaming."""
    for char in text:
        yield char
        time.sleep(0.008)


# ── Session state init ────────────────────────────────────────────────────────

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.session_ready = False
    st.session_state.msg_count = 0

if not st.session_state.session_ready:
    ensure_user_context()
    ok = create_session(st.session_state.session_id)
    st.session_state.session_ready = ok


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="sidebar-label">Connection</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="metric-card">'
        f'<div class="metric-label">Base URL</div>'
        f'<div class="metric-value" style="font-size:0.8rem">{BASE_URL}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-label">User</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="metric-card">'
        f'<div class="metric-label">User ID</div>'
        f'<div class="metric-value" style="font-size:0.75rem">{USER_ID}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-label">Stats</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-label">Messages</div>'
            f'<div class="metric-value">{st.session_state.msg_count}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col2:
        status_color = "#c8f542" if st.session_state.session_ready else "#ef4444"
        status_text = "Live" if st.session_state.session_ready else "Error"
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-label">Status</div>'
            f'<div class="metric-value" style="color:{status_color};font-size:0.85rem">'
            f'● {status_text}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    if st.button("↺  New Session", use_container_width=True):
        for key in ["session_id", "messages", "session_ready", "msg_count"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    st.markdown("---")
    st.markdown('<div class="sidebar-label">Endpoints used</div>', unsafe_allow_html=True)
    for ep in ["POST /user_context", "POST /session", "POST /chat"]:
        st.markdown(
            f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.65rem;'
            f'color:#4b5563;padding:3px 0">{ep}</div>',
            unsafe_allow_html=True,
        )


# ── Main area ─────────────────────────────────────────────────────────────────

st.markdown(
    '<div class="header-bar">'
    '<h1>📈 InvestPal</h1>'
    '<span class="badge">DEV CONSOLE</span>'
    '</div>',
    unsafe_allow_html=True,
)

short_id = st.session_state.session_id[:8] + "…"
st.markdown(
    f'<div class="session-pill">session · <span>{short_id}</span></div>',
    unsafe_allow_html=True,
)

if not st.session_state.session_ready:
    st.error("⚠️ Could not establish session. Make sure the backend is running at **" + BASE_URL + "**.")
    st.stop()

# Render chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f'<div class="user-msg"><div class="msg-label">You</div>{msg["content"]}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<div class="agent-msg"><div class="msg-label">InvestPal</div>', unsafe_allow_html=True)
        st.markdown(msg["content"])
        st.markdown("</div>", unsafe_allow_html=True)

# Input row
st.markdown("---")
col_input, col_btn = st.columns([5, 1])
with col_input:
    user_input = st.text_input(
        label="message",
        placeholder="Ask about your portfolio, market trends, investment ideas…",
        label_visibility="collapsed",
        key="chat_input",
    )
with col_btn:
    send = st.button("Send →", use_container_width=True)

# Handle send
if send and user_input.strip():
    prompt = user_input.strip()

    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.msg_count += 1

    # Show user bubble immediately
    st.markdown(
        f'<div class="user-msg"><div class="msg-label">You</div>{prompt}</div>',
        unsafe_allow_html=True,
    )

    # Call API
    with st.spinner(""):
        response_text = send_message(st.session_state.session_id, prompt)

    if response_text:
        # Stream the response
        st.markdown('<div class="agent-msg"><div class="msg-label">InvestPal</div>', unsafe_allow_html=True)
        st.write_stream(stream_text(response_text))
        st.markdown("</div>", unsafe_allow_html=True)

        st.session_state.messages.append({"role": "agent", "content": response_text})
        st.session_state.msg_count += 1

    st.rerun()
