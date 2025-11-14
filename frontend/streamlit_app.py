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

            # Store in session state
            st.session_state["text"] = text
            st.session_state["formatted"] = formatted

    except Exception as e:
        st.exception(e)

# Display transcripts from session state
if st.session_state.get("text") or st.session_state.get("formatted"):
    st.subheader("Raw transcript")
    st.text_area("text", value=st.session_state.get("text") or "", height=200, key="raw_text_area")

    if st.session_state.get("formatted"):
        st.subheader("Formatted transcript")
        st.text_area("formatted", value=st.session_state.get("formatted") or "", height=300, key="formatted_text_area")

# Show export button if there's formatted text
if st.session_state.get("formatted"):
    st.divider()
    if st.button("Export to DOCX", type="primary"):
        try:
            endpoint = api_base.rstrip("/") + "/export"
            with st.spinner("Exporting to DOCX..."):
                resp = requests.post(endpoint, json={"content": st.session_state["formatted"]}, timeout=60)
            if resp.status_code != 200:
                st.error(f"Error {resp.status_code}: {resp.text}")
            else:
                # Create download button
                st.download_button(
                    label="Download DOCX",
                    data=resp.content,
                    file_name="transcript.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                st.success("Export successful! Click the download button above.")
        except Exception as e:
            st.exception(e)


