import os
import requests
import streamlit as st

API_BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
st.set_page_config(page_title="MedAssist AI", page_icon="🩺", layout="centered")
st.title("🩺 MedAssist AI")
st.caption("Multi-agent medical imaging education assistant")
st.warning("Educational prototype only. Not for diagnosis, triage, or treatment. A qualified clinician must interpret the complete study.")
mode = st.radio("Choose input", ["Analyze an image", "Ask an educational question"])
if mode == "Analyze an image":
    uploaded = st.file_uploader("Upload PNG, JPG or BMP image (max 10 MB)", type=["png","jpg","jpeg","bmp"])
    question = st.text_area("What should the agents focus on?", "Describe the visible image cautiously and provide educational context.")
    if st.button("Analyze image", type="primary", disabled=uploaded is None):
        with st.spinner("The three-agent team is working..."):
            try:
                response = requests.post(
                    f"{API_BASE}/analyze",
                    files={"file": (uploaded.name, uploaded.getvalue(), uploaded.type or "application/octet-stream")},
                    data={"question": question},
                    timeout=180,
                )
                response.raise_for_status()
                data = response.json()
                st.subheader("Reviewed educational report")
                st.markdown(data["answer"])
                st.caption(data["disclaimer"])
            except requests.RequestException as exc:
                st.error(f"API request failed: {exc}")
else:
    question = st.text_area("Ask a general medical-imaging question", "What is the difference between T1-weighted and T2-weighted MRI?")
    if st.button("Ask agents", type="primary", disabled=len(question.strip()) < 5):
        with st.spinner("The research and review team is working..."):
            try:
                response = requests.post(f"{API_BASE}/ask", json={"question": question}, timeout=180)
                response.raise_for_status()
                data = response.json()
                st.subheader("Agent response")
                st.markdown(data["answer"])
                st.caption(data["disclaimer"])
            except requests.RequestException as exc:
                st.error(f"API request failed: {exc}")
st.divider()
if st.button("Check backend health"):
    try:
        health = requests.get(f"{API_BASE}/health", timeout=10)
        st.json(health.json())
    except requests.RequestException as exc:
        st.error(str(exc))
