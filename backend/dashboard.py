import streamlit as st
import requests
import plotly.express as px
import pandas as pd
import os

API = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="DrishtiAI",
    page_icon="🔬",
    layout="wide"
)

st.title("🔬 DrishtiAI — Patient Safety Signal Intelligence")
st.caption("Real-time social listening for adverse drug event detection")


# ---------------- API HELPER ----------------
def safe_get(url, params=None, timeout=20):
    try:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return None


def safe_post(url, timeout=30):
    try:
        response = requests.post(url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return None


# ---------------- STATS ----------------
stats = safe_get(f"{API}/signals/stats")

if not stats:
    st.error("Backend unavailable.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Posts", stats.get("total_posts", 0))
col2.metric("Processed", stats.get("processed", 0))
col3.metric("⚠️ Adverse Events", stats.get("adverse_events", 0))
col4.metric("🔒 PII Flagged", stats.get("pii_flagged", 0))

st.divider()


# ---------------- CONTROLS ----------------
col_a, col_b, col_c = st.columns([2, 1, 1])

with col_a:
    adverse_only = st.toggle("Show adverse events only", value=False)

with col_b:
    if st.button("🔄 Ingest New Posts"):
        result = safe_post(f"{API}/ingest/test")
        if result:
            st.success(
                f"Fetched: {result.get('fetched', 0)}, Saved: {result.get('saved', 0)}"
            )

with col_c:
    if st.button("⚙️ Process Posts"):
        result = safe_post(f"{API}/process", timeout=60)
        if result:
            st.success(f"Processed: {result.get('processed', 0)}")

st.divider()


# ---------------- TRENDS ----------------
trends = safe_get(f"{API}/signals/trends", params={"days": 7})

if trends:
    df_trends = pd.DataFrame(trends)

    fig = px.bar(
        df_trends,
        x="date",
        y=["total", "adverse", "negative"],
        title="Signal Trends (Last 7 Days)",
        barmode="group"
    )

    st.plotly_chart(fig, use_container_width=True)

st.divider()


# ---------------- AGENTIC DISCOVERY ----------------
st.subheader("🤖 Agentic Source Discovery")
st.caption("AI agent discovers new monitoring sources automatically")

topic = st.text_input(
    "Enter health topic to discover sources for:",
    value="ozempic side effects India"
)

if st.button("🔍 Discover Sources"):
    with st.spinner("Agent searching the web for relevant communities..."):
        result = safe_get(
            f"{API}/discover",
            params={"topic": topic},
            timeout=25
        )

    if result:
        sources = result.get("discovered", [])

        st.success(f"Discovered {len(sources)} potential sources")

        if not sources:
            st.info("No sources found.")

        for src in sources:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])

                with col1:
                    st.markdown(f"**{src.get('title', 'Untitled')}**")
                    st.caption(src.get("domain", "unknown"))
                    st.write(src.get("snippet", ""))

                with col2:
                    badge = "🟢 Forum" if src.get("is_forum") else "🔵 Web"
                    st.write(badge)
                    st.caption(src.get("suggested_engine", "unknown"))

                with col3:
                    if st.button(
                        "✅ Add to Project",
                        key=f"add_{src.get('domain', '')}"
                    ):
                        st.success("Added!")

                st.divider()

st.divider()


# ---------------- SIGNAL FEED ----------------
st.subheader("📡 Signal Feed")

feed = safe_get(
    f"{API}/signals/feed",
    params={
        "adverse_only": str(adverse_only).lower(),
        "limit": 20
    },
    timeout=25
)

if feed:
    for post in feed:
        is_adverse = post.get("is_adverse_event", False)
        has_pii = post.get("has_pii", False)

        with st.container():
            cols = st.columns([3, 1, 1, 1])

            with cols[0]:
                content = post.get("content", "")
                source = post.get("source", "unknown").upper()
                timestamp = post.get("timestamp", "")

                st.markdown(f"**{source}** | {timestamp[:10]}")
                st.write(
                    content[:200] + "..."
                    if len(content) > 200
                    else content
                )

                explanation = post.get("shap_explanation", {})
                reasons = explanation.get("reasons", [])

                if reasons:
                    with st.expander("🔍 Why flagged?"):
                        for reason in reasons:
                            st.write(f"• {reason}")

            with cols[1]:
                sentiment = post.get("sentiment", "unknown")

                emoji = (
                    "😟" if sentiment == "negative"
                    else "😊" if sentiment == "positive"
                    else "😐"
                )

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
else:
    st.info("No signal feed data available.")