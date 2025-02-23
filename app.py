import streamlit as st
import json
import requests
import os
import zipfile
import tempfile
from conversation_analysis import ConversationAnalyzer
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load JSON file
def load_json(file):
    return json.load(file)

# Load JSON files from a zip file
def load_json_files_from_zip(zip_file):
    json_data = []
    with zipfile.ZipFile(zip_file, 'r') as z:
        for filename in z.namelist():
            if filename.endswith('.json'):
                with z.open(filename) as f:
                    json_data.append((load_json(f), os.path.splitext(filename)[0]))
    return json_data

# Query Llama 3.1 model
def query_llama(prompt):
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model = os.getenv("OLLAMA_MODEL", "llama3.1:latest")

    response = requests.post(
        f"{ollama_base_url}/generate",
        json={"model": ollama_model, "prompt": prompt}
    )
    if response.status_code == 200:
        return response.json().get("response", "")
    return ""

# Function to run LLM queries in parallel
def run_llm_queries(prompts):
    results = []
    with ThreadPoolExecutor() as executor:
        future_to_prompt = {executor.submit(query_llama, prompt): prompt for prompt in prompts}
        for future in as_completed(future_to_prompt):
            prompt = future_to_prompt[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                st.error(f"Error occurred while processing prompt: {prompt} - {exc}")
    return results

# prompts for Llama 3.1
PROFANITY_PROMPT = "Analyze the following text and detect any profane language. Return 'True' if profanity is found, otherwise 'False': {text}"
PRIVACY_PROMPT = "Analyze the following text and detect if sensitive information (balance, account, SSN, date of birth, address) is shared without proper verification. Return 'True' if a violation is found, otherwise 'False': {text}"

# Streamlit app
def main():
    st.title("Conversation Analysis Tool")

    # Upload zip file
    uploaded_file = st.file_uploader("Upload a zip file containing JSON files", type=["zip"])

    if uploaded_file is not None:
        data = []

        # Load JSON files from the zip file
        data = load_json_files_from_zip(uploaded_file)

        # Dropdowns
        approach = st.selectbox("Select Approach", ["Pattern Matching", "LLM"])
        entity = st.selectbox("Select Entity", ["Profanity Detection", "Privacy and Compliance Violation"])

        analyzer = ConversationAnalyzer()

        # Analyze
        results = []
        for json_data, call_id in data:
            print("processing file...", call_id)
            if entity == "Profanity Detection":
                if approach == "Pattern Matching":
                    result = analyzer.identify_profanity_call_ids(json_data, call_id)
                    results.append({
                        "call_id": call_id,
                        "agent_profanity_detected": len(result['agent_call_ids']) > 0,
                        "borrower_profanity_detected": len(result['borrower_call_ids']) > 0
                    })
                else:  # LLM
                    prompts = [PROFANITY_PROMPT.format(text=conv['text']) for conv in json_data]
                    llm_results = run_llm_queries(prompts)
                    results.append({
                        "call_id": call_id,
                        "profanity_detected": any(result == "True" for result in llm_results)
                    })
            elif entity == "Privacy and Compliance Violation":
                if approach == "Pattern Matching":
                    result = analyzer.identify_privacy_violation_call_ids(json_data, call_id)
                    results.append({
                        "call_id": call_id,
                        "privacy_violation_detected": len(result) > 0
                    })
                else:  # LLM
                    prompts = [PRIVACY_PROMPT.format(text=conv['text']) for conv in json_data]
                    llm_results = run_llm_queries(prompts)
                    results.append({
                        "call_id": call_id,
                        "privacy_violation_detected": any(result == "True" for result in llm_results)
                    })

        # Output
        st.write("Analysis Results:", results)

if __name__ == "__main__":
    main()