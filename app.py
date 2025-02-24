import streamlit as st
import json
import requests
import os
import zipfile
from conversation_analysis import ConversationAnalyzer
from concurrent.futures import ThreadPoolExecutor, as_completed
import plotly.graph_objects as go
from textblob import TextBlob  
import re

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

# run LLM queries in parallel
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

#recommend approach based on content analysis
def recommend_approach(json_data):
    recommendations = []
    for conv in json_data:
        text = conv['text']
        text_length = len(text.split())
        sentiment = TextBlob(text).sentiment
        polarity, subjectivity = sentiment.polarity, sentiment.subjectivity
        
        profanity_count = len(re.findall(r'\b(shit|fuck|damn|bitch|asshole|crap|dick)\b', text, re.IGNORECASE))
        sensitive_info_count = len(re.findall(r'\b(account|ssn|credit card|debit card|bank account)\b', text, re.IGNORECASE))
        keyword_density = (profanity_count + sensitive_info_count) / max(1, text_length)
        
        confidence_score = (abs(polarity) + subjectivity + keyword_density + (text_length / 100)) * 10
        
        if profanity_count > 2 or sensitive_info_count > 1 or confidence_score > 7:
            recommendations.append("Use LLM")
        else:
            recommendations.append("Use Pattern Matching")
    return recommendations

# Prompts
PROFANITY_PROMPT = (
    "You are an AI language model tasked with analyzing conversations. "
    "Please review the following text from a conversation between a customer and an agent. "
    "Identify any instances of profane language, including but not limited to: "
    "swear words, derogatory terms, and offensive language. "
    "Return 'True' if any profanity is found, otherwise return 'False'. "
    "Additionally, provide a brief summary of the context in which the profanity was used: {text}"
)

PRIVACY_PROMPT = (
    "You are an AI language model responsible for ensuring privacy compliance. "
    "Analyze the following text from a conversation and determine if any sensitive information is shared. "
    "Look for information such as account numbers, social security numbers, credit card details, "
    "and personal identifiers like date of birth or address. "
    "Return 'True' if a violation is found, otherwise return 'False'. "
    "If a violation is detected, please explain what sensitive information was shared and the context: {text}"
)

# Streamlit app
def main():
    st.title("Conversation Analysis Tool")

    uploaded_file = st.file_uploader("Upload a zip file containing JSON files", type=["zip"])

    if uploaded_file is not None:
        data = load_json_files_from_zip(uploaded_file)

        # Dropdowns
        analysis_type = st.selectbox("Select Analysis Type", ["Profanity Detection", "Privacy and Compliance Violation", "Call Quality Metrics Analysis"])

        analyzer = ConversationAnalyzer()

        if analysis_type in ["Profanity Detection", "Privacy and Compliance Violation"]:
            approach = st.selectbox("Select Approach", ["Pattern Matching", "LLM"])

            # Analyze each call
            results = []
            for json_data, call_id in data:
                if analysis_type == "Profanity Detection":
                    if approach == "Pattern Matching":
                        result = analyzer.identify_profanity_call_ids(json_data, call_id)
                        results.append(result)
                    else:
                        prompts = [PROFANITY_PROMPT.format(text=conv['text']) for conv in json_data]
                        llm_results = run_llm_queries(prompts)
                        results.append({
                            "call_id": call_id,
                            "profanity_detected": any(result == "True" for result in llm_results),
                        })
                elif analysis_type == "Privacy and Compliance Violation":
                    if approach == "Pattern Matching":
                        result = analyzer.identify_privacy_violation_call_ids(json_data, call_id)
                        results.append(result)
                    else:
                        prompts = [PRIVACY_PROMPT.format(text=conv['text']) for conv in json_data]
                        llm_results = run_llm_queries(prompts)
                        results.append({
                            "call_id": call_id,
                            "privacy_violation_detected": any(result == "True" for result in llm_results),
                        })

            # Button to compare approaches
            if st.button("Compare Approaches"):
                if analysis_type == "Profanity Detection":
                    overall_profanity_recommendation = analyzer.get_overall_recommendation([conv for json_data, _ in data for conv in json_data if analysis_type == "Profanity Detection"])
                    st.write(f"Recommended Approach for Profanity Detection: {overall_profanity_recommendation}")
                elif analysis_type == "Privacy and Compliance Violation":
                    overall_privacy_recommendation = analyzer.get_overall_recommendation([conv for json_data, _ in data for conv in json_data if analysis_type == "Privacy and Compliance Violation"])
                    st.write(f"Recommended Approach for Privacy and Compliance Violation: {overall_privacy_recommendation}")

            st.write("Analysis Results:", results)

        elif analysis_type == "Call Quality Metrics Analysis":
            metrics_results = []
            for json_data, call_id in data:
                metrics = analyzer.calculate_overtalk_and_silence(json_data)
                metrics_results.append({
                    "call_id": call_id,
                    "overtalk_percentage": metrics['overtalk_percentage'],
                    "silence_percentage": metrics['silence_percentage']
                })

            # Visualization
            call_ids = [result['call_id'] for result in metrics_results]
            overtalk_percentages = [result['overtalk_percentage'] for result in metrics_results]
            silence_percentages = [result['silence_percentage'] for result in metrics_results]

            # interactive bar chart
            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=call_ids,
                y=overtalk_percentages,
                name='Overtalk Percentage',
                marker_color='blue'
            ))

            fig.add_trace(go.Bar(
                x=call_ids,
                y=silence_percentages,
                name='Silence Percentage',
                marker_color='red'
            ))

            fig.update_layout(
                title='Call Quality Metrics: Overtalk and Silence Percentages',
                xaxis_title='Call ID',
                yaxis_title='Percentage (%)',
                barmode='group'
            )

            st.plotly_chart(fig)

if __name__ == "__main__":
    main()