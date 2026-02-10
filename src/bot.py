import os
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from config import SESSION_DIR, MISSION_STAGES, GROUP_LINK
from ai import AIEngine

class WhatsAppBot:
    def __init__(self, contacts, resume=False):
        self.contacts = contacts
        self.ai = AIEngine()
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'user-data-dir={SESSION_DIR}')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.wait = WebDriverWait(self.driver, 30)
        if not resume or not os.path.exists(SESSION_DIR):
            self.login()

    def login(self):
        self.driver.get('https://web.whatsapp.com')
        print("Scan QR (non-headless first run). Waiting 60s...")
        time.sleep(60)

    def find_chat(self, contact_name):
        search_box = self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')))
        search_box.clear()
        search_box.send_keys(contact_name)
        search_box.send_keys(Keys.ENTER)
        time.sleep(2)

    def send_message(self, message, name):
        if not self.contacts.increment_sent(name):
            print(f"Daily limit reached for {name}")
            return False
        message_box = self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')))
        message_box.send_keys(message)
        message_box.send_keys(Keys.ENTER)
        time.sleep(random.randint(5, 30))  # Anti-ban delay
        return True

    def get_last_message(self):
        messages = self.driver.find_elements(By.CSS_SELECTOR, '.message-in .selectable-text span')
        return messages[-1].text if messages else ''

    def share_group_link(self):
        return GROUP_LINK  # Or per-instructions

    def run_convo(self, name):
        contact = self.contacts.get_contact(name)
        if not contact:
            return
        _, _, _, objective, instructions, state, history_str, _, _ = contact
        history = json.loads(history_str)
        self.find_chat(name)

        while state != 'done':
            last_msg = self.get_last_message()
            if last_msg and (not history or history[-1].get('content') != last_msg):
                history.append({'role': 'user', 'content': last_msg})
                response = self.ai.generate_response(history, objective, instructions, state)
                if '[ACTION]' in response:
                    if 'persuade_join_group' in objective:
                        link = self.share_group_link()
                        response += f"\n{link}"
                    # Other actions...
                    state = 'done'
                if self.send_message(response, name):
                    history.append({'role': 'assistant', 'content': response})
                    current_idx = MISSION_STAGES.index(state)
                    state = MISSION_STAGES[min(current_idx + 1, len(MISSION_STAGES) - 1)]
                    self.contacts.update_state(name, state, history)
                else:
                    break
            time.sleep(10)  # Poll

    def random_chat_existing(self, num=5):
        existing = self.contacts.get_all_contacts(filter_old=True)  # Assume all for now
        random.shuffle(existing)
        for name in existing[:num]:
            self.run_convo(name)  # Uses 'spark_convo' objective if set, else default casual

    def close(self):
        self.driver.quit()
