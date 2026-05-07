import streamlit as st
import requests
import plotly.express as px
import pandas as pd

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="DrishtiAI", page_icon="🔬", layout="wide")
st.title("🔬 DrishtiAI — Patient Safety Signal Intelligence")
st.caption("Real-time social listening for adverse drug event detection")

# ── STATS ROW ──────────────────────────────────────────
stats = requests.get(f"{API}/signals/stats").json()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Posts", stats["total_posts"])
col2.metric("Processed", stats["processed"])
col3.metric("⚠️ Adverse Events", stats["adverse_events"])
col4.metric("🔒 PII Flagged", stats["pii_flagged"])

st.divider()

# ── CONTROLS ───────────────────────────────────────────
col_a, col_b, col_c = st.columns([2, 1, 1])
with col_a:
    adverse_only = st.toggle("Show adverse events only", value=False)
with col_b:
    if st.button("🔄 Ingest New Posts"):
        r = requests.post(f"{API}/ingest/test")
        st.success(f"Fetched: {r.json()['fetched']}, Saved: {r.json()['saved']}")
with col_c:
    if st.button("⚙️ Process Posts"):
        r = requests.post(f"{API}/process")
        st.success(f"Processed: {r.json()['processed']}")

st.divider()

# ── TREND CHART ────────────────────────────────────────
trends = requests.get(f"{API}/signals/trends?days=7").json()
if trends:
    df_trends = pd.DataFrame(trends)
    fig = px.bar(
        df_trends, x="date", y=["total", "adverse", "negative"],
        title="Signal Trends (Last 7 Days)",
        barmode="group",
        color_discrete_map={
            "total": "#4A90D9",
            "adverse": "#E74C3C",
            "negative": "#F39C12"
        }
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("🤖 Agentic Source Discovery")
st.caption("AI agent discovers new monitoring sources automatically")

topic = st.text_input(
    "Enter health topic to discover sources for:",
    value="ozempic side effects India"
)

if st.button("🔍 Discover Sources"):
    with st.spinner("Agent searching the web for relevant communities..."):
        r = requests.get(f"{API}/discover?topic={topic}")
        sources = r.json().get("discovered", [])

    st.success(f"Discovered {len(sources)} potential sources")

    for src in sources:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{src['title'][:60]}**")
                st.caption(src['domain'])
                st.write(src['snippet'])
            with col2:
                badge = "🟢 Forum" if src['is_forum'] else "🔵 Web"
                st.write(badge)
                st.caption(src['suggested_engine'])
            with col3:
                if st.button("✅ Add to Project", key=src['domain']):
                    st.success("Added!")
            st.divider()
# ── SIGNAL FEED ────────────────────────────────────────
st.subheader("📡 Signal Feed")

feed = requests.get(
    f"{API}/signals/feed?adverse_only={str(adverse_only).lower()}&limit=20"
).json()

for post in feed:
    is_adverse = post.get("is_adverse_event", False)
    has_pii = post.get("has_pii", False)

    border_color = "#E74C3C" if is_adverse else "#2ECC71"
    
    with st.container():
        cols = st.columns([3, 1, 1, 1])
        
        with cols[0]:
            content = post.get("content", "")
            st.markdown(f"**{post['source'].upper()}** | {post.get('timestamp', '')[:10]}")
            st.write(content[:200] + "..." if len(content) > 200 else content)
            
            if post.get("shap_explanation") and post["shap_explanation"].get("reasons"):
                with st.expander("🔍 Why flagged?"):
                    for reason in post["shap_explanation"]["reasons"]:
                        st.write(f"• {reason}")
        
        with cols[1]:
            sentiment = post.get("sentiment", "unknown")
            emoji = "😟" if sentiment == "negative" else "😊" if sentiment == "positive" else "😐"
            st.metric("Sentiment", f"{emoji} {sentiment}")
        
        with cols[2]:
            if is_adverse:
                conf = post.get("adverse_confidence", 0)
                st.metric("⚠️ Adverse", f"{conf:.0%}")
            else:
                st.metric("Status", "✅ Safe")
        
        with cols[3]:
            if has_pii:
                st.metric("🔒 PII", "Detected")
            else:
                st.metric("🔒 PII", "Clean")
        
        st.divider()