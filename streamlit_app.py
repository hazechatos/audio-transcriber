import io
import os
from typing import Optional

import requests
import streamlit as st


st.set_page_config(page_title="Notary Transcriber", page_icon="📝", layout="centered")
st.title("📝 Notary Transcriber - Frontend Test")

default_api = os.environ.get("API_BASE_URL", "http://localhost:8000")
api_base = st.text_input("API base URL", value=default_api, help="Base URL of FastAPI service")

uploaded = st.file_uploader("Upload an audio file", type=[
    "mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm", "wma"
])

col1, col2 = st.columns(2)
with col1:
    format_output = st.checkbox("Apply notary-style formatting", value=True)
with col2:
    language = st.selectbox(
        "Language (optional)", ["", "fr", "en", "es", "de", "it"], index=1,
        help="Provide a hint to the ASR model"
    )

if uploaded is not None:
    st.audio(uploaded)

if st.button("Transcribe"):
    if uploaded is None:
        st.warning("Please upload a file first.")
        st.stop()

    try:
        endpoint = api_base.rstrip("/") + "/transcribe"
        params = {"format_output": str(format_output).lower()}
        if language:
            params["language"] = language

        files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type or "application/octet-stream")}
        with st.spinner("Transcribing..."):
            resp = requests.post(endpoint, params=params, files=files, timeout=600)
        if resp.status_code != 200:
            st.error(f"Error {resp.status_code}: {resp.text}")
        else:
            data = resp.json()
            text: Optional[str] = data.get("text")
            formatted: Optional[str] = data.get("formattedText")

            st.subheader("Raw transcript")
            st.text_area("text", value=text or "", height=200)

            if formatted is not None:
                st.subheader("Formatted transcript")
                st.text_area("formatted", value=formatted or "", height=300)

    except Exception as e:
        st.exception(e)


