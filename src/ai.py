import requests
import ollama
from config import XAI_API_KEY, OLLAMA_MODEL

class AIEngine:
    def __init__(self):
        self.use_local = False  # Toggle based on limits; monitor usage here if needed

    def generate_response(self, history, objective, instructions, current_state):
        prompt = f"""
        You are a natural conversationalist. Objective: {objective}. Instructions: {instructions}.
        Stage: {current_state}. History: {json.dumps(history)}.
        Generate a human-like response to advance towards the objective.
        For 'action' stage, include '[ACTION]' (e.g., [SEND_LINK] or [INTRODUCE]).
        Keep ethical, no deception.
        """
        if self.use_local or not XAI_API_KEY:
            response = ollama.chat(model=OLLAMA_MODEL, messages=[{'role': 'user', 'content': prompt}])['message']['content']
        else:
            try:
                api_resp = requests.post(
                    'https://api.x.ai/v1/chat/completions',
                    headers={'Authorization': f'Bearer {XAI_API_KEY}'},
                    json={'model': 'grok-beta', 'messages': [{'role': 'user', 'content': prompt}], 'max_tokens': 150}
                ).json()
                response = api_resp['choices'][0]['message']['content'].strip()
            except Exception:
                self.use_local = True  # Fallback
                response = ollama.chat(model=OLLAMA_MODEL, messages=[{'role': 'user', 'content': prompt}])['message']['content']
        return response
