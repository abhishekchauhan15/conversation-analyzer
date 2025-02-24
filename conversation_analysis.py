import re
from textblob import TextBlob

class ConversationAnalyzer:
    def __init__(self):
        self.profanity_pattern = re.compile(r'\b(shit|fuck|damn|hell|bitch|asshole|bastard|piss|crap|dick|pussy|fag|whore|slut|wanker|arse)\b', re.IGNORECASE)
        self.sensitive_info_pattern = re.compile(r'\b(account|balance|ssn|social security|credit card|debit card|bank account)\b', re.IGNORECASE)
        self.verification_pattern = re.compile(r'\b(date of birth|dob|address|ssn|social security)\b', re.IGNORECASE)

    from textblob import TextBlob

    def get_overall_recommendation(self, conversations):
        total_text_length = 0
        total_confidence_score_pattern = 0
        total_confidence_score_llm = 0
        total_profanity_pattern = 0
        total_profanity_llm = 0
        total_sensitive_info_pattern = 0
        total_sensitive_info_llm = 0

        for conv in conversations:
            text = conv['text']
            text_length = len(text.split())
            total_text_length += text_length

            # Pattern Matching Approach
            profanity_count_pattern = len(re.findall(self.profanity_pattern, text))
            sensitive_info_count_pattern = len(re.findall(self.sensitive_info_pattern, text))
            confidence_score_pattern = (profanity_count_pattern + sensitive_info_count_pattern) / max(1, text_length) * 10

            # LLM-Based Approach (Sentiment & Context Analysis)
            sentiment = TextBlob(text).sentiment
            polarity, subjectivity = sentiment.polarity, sentiment.subjectivity
            confidence_score_llm = (abs(polarity) + subjectivity + (text_length / 100)) * 10

            # Aggregate counts and scores
            total_profanity_pattern += profanity_count_pattern
            total_profanity_llm += profanity_count_pattern  # Assuming LLM also detects the same profanities
            total_sensitive_info_pattern += sensitive_info_count_pattern
            total_sensitive_info_llm += sensitive_info_count_pattern  # Adjust based on LLM results
            total_confidence_score_pattern += confidence_score_pattern
            total_confidence_score_llm += confidence_score_llm

        # Compute overall confidence scores
        overall_confidence_score_pattern = total_confidence_score_pattern / max(1, total_text_length)
        overall_confidence_score_llm = total_confidence_score_llm / max(1, total_text_length)

        # Determine which approach is better
        if overall_confidence_score_llm > overall_confidence_score_pattern:
            return "LLM will more effective"
        elif overall_confidence_score_pattern > overall_confidence_score_llm:
            return "Pattern Matching will be more effective"
        else:
            return "Both approaches perform similarly"


    def identify_profanity_call_ids(self, conversations, call_id):
        agent_call_ids = set()
        borrower_call_ids = set()
        agent_profanity_detected = False
        borrower_profanity_detected = False

        for utterance in conversations:
            if self.profanity_pattern.search(utterance['text']):
                if utterance['speaker'] == 'Agent':
                    agent_call_ids.add(call_id)
                    agent_profanity_detected = True
                elif utterance['speaker'] == 'Borrower':
                    borrower_call_ids.add(call_id)
                    borrower_profanity_detected = True

        return {
            'call_id': call_id,
            'agent_profanity_detected': agent_profanity_detected,
            'borrower_profanity_detected': borrower_profanity_detected
        }

    def identify_privacy_violation_call_ids(self, conversations, call_id):
        if self.detect_privacy_violations(conversations):
            return {
                'call_id': call_id,
                'privacy_violation_detected': True
            }
        return {
            'call_id': call_id,
            'privacy_violation_detected': False
        }

    def detect_privacy_violations(self, conversations):
        has_sensitive_info = any(self.sensitive_info_pattern.search(utterance['text']) for utterance in conversations)
        has_verification = any(self.verification_pattern.search(utterance['text']) for utterance in conversations)
        return has_sensitive_info and not has_verification

    def calculate_overtalk_and_silence(self, conversations):
        total_duration = 0
        overtalk_duration = 0
        previous_end_time = 0

        for utterance in conversations:
            start_time = utterance['stime']
            end_time = utterance['etime']
            duration = end_time - start_time
            total_duration += duration

            if previous_end_time > start_time:
                overtalk_duration += min(end_time, previous_end_time) - start_time
            previous_end_time = end_time

        silence_duration = max(0, total_duration - overtalk_duration)
        overtalk_percentage = (overtalk_duration / total_duration) * 100 if total_duration else 0
        silence_percentage = (silence_duration / total_duration) * 100 if total_duration else 0

        return {
            'overtalk_percentage': round(overtalk_percentage, 2),
            'silence_percentage': round(silence_percentage, 2)
        }
