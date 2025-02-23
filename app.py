import streamlit as st
import json
import requests

def main():
    st.title("Conversation Analysis Tool")

    # Upload JSON file
    uploaded_file = st.file_uploader("Upload JSON File", type=["json"])

    if uploaded_file is not None:
        data = load_json(uploaded_file)

        # Dropdowns
        approach = st.selectbox("Select Approach", ["Pattern Matching", "LLM"])
        entity = st.selectbox("Select Entity", ["Profanity Detection", "Privacy and Compliance Violation"])

        # Analyze
        if entity == "Profanity Detection":
            if approach == "Pattern Matching":
                result = any(detect_profanity(conv) for conv in data["conversations"])
            else:  # LLM
                result = any(query_llama(PROFANITY_PROMPT.format(text=conv)) == "True" for conv in data["conversations"])
        elif entity == "Privacy and Compliance Violation":
            if approach == "Pattern Matching":
                result = any(detect_privacy_violation(conv) for conv in data["conversations"])
            else:  # LLM
                result = any(query_llama(PRIVACY_PROMPT.format(text=conv)) == "True" for conv in data["conversations"])

        # Output
        st.write(f"Entity Detected: {result}")

if __name__ == "__main__":
    main()