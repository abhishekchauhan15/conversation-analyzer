import json
import os
import re
from datetime import datetime

class ConversationAnalyzer:
    def __init__(self):
        self.profanity_pattern = re.compile(r'\b(shit|fuck|damn|hell|bitch|asshole|bastard|piss|crap|dick|pussy|fag|whore|slut|wanker|arse)\b', re.IGNORECASE)
        self.sensitive_info_pattern = re.compile(r'\b(account|balance|ssn|social security|credit card|debit card|bank account)\b', re.IGNORECASE)

    def identify_profanity_call_ids(self, conversations, call_id):
        agent_call_ids = []
        borrower_call_ids = []

        for utterance in conversations:
            if self.profanity_pattern.search(utterance['text']):
                if utterance['speaker'] == 'Agent':
                    agent_call_ids.append(call_id)
                elif utterance['speaker'] == 'Borrower':
                    borrower_call_ids.append(call_id)

        return {
            'agent_call_ids': agent_call_ids,
            'borrower_call_ids': borrower_call_ids
        }

    def identify_privacy_violation_call_ids(self, conversations, call_id):
        violation_call_ids = []

        for conv in conversations:
            if self.detect_privacy_violations([conv]):
                violation_call_ids.append(call_id)

        return violation_call_ids if violation_call_ids else []

    def detect_privacy_violations(self, conversations):
        has_sensitive_info = False
        has_verification = False

        for utterance in conversations:
            if self.sensitive_info_pattern.search(utterance['text']):
                has_sensitive_info = True
            if re.search(r'\b(date of birth|dob|address|ssn|social security)\b', utterance['text'], re.IGNORECASE):
                has_verification = True

        return has_sensitive_info and not has_verification

    def calculate_overtalk_and_silence(self, conversations):
        total_duration = 0
        overtalk_duration = 0
        silence_duration = 0

        previous_end_time = 0

        for utterance in conversations:
            start_time = utterance['stime']
            end_time = utterance['etime']
            duration = end_time - start_time

            total_duration += duration

            if previous_end_time > start_time:
                # Overtalk detected
                overtalk_duration += min(end_time, previous_end_time) - start_time

            previous_end_time = end_time

        # Calculate silence duration
        silence_duration = total_duration - overtalk_duration

        # Calculate percentages
        overtalk_percentage = (overtalk_duration / total_duration) * 100 if total_duration > 0 else 0
        silence_percentage = (silence_duration / total_duration) * 100 if total_duration > 0 else 0

        return {
            'overtalk_percentage': overtalk_percentage,
            'silence_percentage': silence_percentage
        }
