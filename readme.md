# Conversation Analysis Tool

## Description
The Conversation Analysis Tool is a Streamlit application designed to analyze conversations for profanity detection and privacy compliance violations. It leverages natural language processing (NLP) techniques to provide insights into customer-agent interactions, helping organizations ensure compliance and maintain a professional communication standard.

## Features
- **Profanity Detection**: Identifies instances of profane language in conversations.
- **Privacy Compliance**: Detects sensitive information shared without proper verification.
- **Call Quality Metrics**: Analyzes call quality metrics such as overtalk and silence percentages.
- **Parallel Processing**: Utilizes threading to run LLM queries concurrently for faster analysis.

## Requirements
- Python 3.7 or higher
- Streamlit
- TextBlob
- Requests
- Plotly
- Other dependencies as specified in `requirements.txt`

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/abhishekchauhan15/conversation-analyzer.git
   cd conversation-analysis-tool
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

2. Open your web browser and navigate to `http://localhost:8501` to access the application.

3. Upload a zip file containing JSON files with conversation data.

4. Select the analysis type (Profanity Detection or Privacy and Compliance Violation) and the approach (Pattern Matching or LLM).

5. Click the "Compare Approaches" button to see the recommended approach based on the analysis.

## Prompts
The application uses predefined prompts for the LLM to analyze conversations:
- **Profanity Detection Prompt**: Analyzes the text for profane language and provides context.
- **Privacy Compliance Prompt**: Analyzes the text for sensitive information and checks for compliance.


## Overall Recommendation Method

The `get_overall_recommendation` method analyzes conversations to determine the most effective approach for detecting profanity and sensitive information. It compares two methods: Pattern Matching and LLM (Language Model) analysis. Here’s how the method works:

### Analysis Process

1. **Pattern Matching Analysis**:
   - **Profanity Count**: Counts the number of profane words detected in the text.
   - **Sensitive Info Count**: Counts the number of sensitive information instances detected.
   - **Confidence Score**: Calculated based on the counts of profanity and sensitive information relative to the total text length.

2. **LLM Analysis**:
   - **Profanity Understanding**: Evaluates the context in which profanity is used, providing a more nuanced understanding.
   - **Sensitive Info Detection**: Assesses sensitive information with a focus on context and relevance.
   - **Sentiment Score**: Analyzes the sentiment of the text to provide additional context.
   - **Confidence Score**: Calculated based on sentiment and text length, providing a score that reflects the LLM's confidence in its analysis.

### Example of How recomendation analysis works

For a given conversation, the analysis might yield the following results:

#### Pattern Matching Analysis
- **Profanity Count**: ✅ Detected
- **Sensitive Info Count**: ✅ Detected
- **Confidence Score**: 7.5

#### LLM Analysis
- **Profanity Understanding**: ✅ Contextual
- **Sensitive Info Detection**: ✅ More nuanced
- **Sentiment Score**: Negative
- **Confidence Score**: 8.2

### Final Decision
Based on the analysis, the final decision is made as follows:
- 🔹 **LLM is better** (Score: 8.2 > 7.5)

This method provides a comprehensive evaluation of the conversation, allowing users to make informed decisions about which approach to use for further analysis.


