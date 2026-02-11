import sqlite3
import csv
import json
from datetime import date
from config import DAILY_LIMIT, DB_FILE

class ContactManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                number TEXT,
                objective TEXT,
                instructions TEXT,
                state TEXT DEFAULT 'idle',
                history TEXT DEFAULT '[]',
                daily_sent INTEGER DEFAULT 0,
                last_sent DATE
            )
        ''')
        self.conn.commit()

    def import_csv(self, csv_file):
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.cursor.execute('''
                    INSERT OR REPLACE INTO contacts (name, number, objective, instructions)
                    VALUES (?, ?, ?, ?)
                ''', (row['name'], row['number'], row.get('objective', 'default'), row.get('instructions', '')))
        self.conn.commit()

    def get_contact(self, name):
        self.cursor.execute('SELECT * FROM contacts WHERE name = ?', (name,))
        return self.cursor.fetchone()

    def get_all_contacts(self, filter_old=False):
        self.cursor.execute('SELECT name FROM contacts')
        return [row[0] for row in self.cursor.fetchall()]  # Extend for old filter (e.g., based on last_msg_date)

    def update_state(self, name, state, history):
        self.cursor.execute('UPDATE contacts SET state = ?, history = ? WHERE name = ?', (state, json.dumps(history), name))
        self.conn.commit()

    def increment_sent(self, name):
        today = date.today().isoformat()
        contact = self.get_contact(name)
        if contact[7] == today:  # last_sent
            sent = contact[6] + 1  # daily_sent
        else:
            sent = 1
        if sent > DAILY_LIMIT:
            return False
        self.cursor.execute('UPDATE contacts SET daily_sent = ?, last_sent = ? WHERE name = ?', (sent, today, name))
        self.conn.commit()
        return True

    def close(self):
        self.conn.close()
