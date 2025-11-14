import io
import os
from typing import Optional

import requests
import streamlit as st

api_base="http://localhost:8000"

st.set_page_config(page_title="Notary Transcriber", page_icon="📝", layout="centered")
st.title("📝 Notary Transcriber")

uploaded = st.file_uploader("Upload an audio file", type=[
    "mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm", "wma"
])

format_output = st.checkbox("Apply notary-style formatting", value=True)

if uploaded is not None:
    st.audio(uploaded)

if st.button("Transcribe"):
    if uploaded is None:
        st.warning("Please upload a file first.")
        st.stop()

    try:
        endpoint = api_base.rstrip("/") + "/transcribe"
        params = {"format_output": str(format_output).lower()}

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


