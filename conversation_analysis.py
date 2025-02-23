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

    def calculate_overtalk_percentage(self, call_data):
        # Calculate the percentage of time where both parties are speaking simultaneously
        total_duration = call_data['duration']
        overtalk_duration = call_data['overtalk_duration']
        return (overtalk_duration / total_duration) * 100 if total_duration > 0 else 0

    def calculate_silence_percentage(self, call_data):
        # Calculate the percentage of time where neither party is speaking
        total_duration = call_data['duration']
        silence_duration = call_data['silence_duration']
        return (silence_duration / total_duration) * 100 if total_duration > 0 else 0
