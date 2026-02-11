import os
from dotenv import load_dotenv

load_dotenv()

XAI_API_KEY = os.getenv('XAI_API_KEY')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3')
DAILY_LIMIT = int(os.getenv('DAILY_LIMIT', 50))
DB_FILE = 'whatsapp_bot.db'
SESSION_DIR = 'session'
GROUP_LINK = 'https://chat.whatsapp.com/YOUR_GROUP_LINK'  # Customize per objective if needed
MISSION_STAGES = ['greet', 'engage', 'convince', 'action', 'done']
