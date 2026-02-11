import threading
import schedule
import time
from contacts import ContactManager
from bot import WhatsAppBot

def main():
    contacts = ContactManager()
    resume = os.path.exists('session')
    bot = WhatsAppBot(contacts, resume=resume)

    # Schedule daily random chats
    schedule.every().day.at("10:00").do(bot.random_chat_existing)

    while True:
        schedule.run_pending()
        print("\nCommands: import_csv [file], start_outreach [name or all], random_chat, resume, quit")
        cmd = input("> ").strip().split()
        if not cmd:
            continue
        if cmd[0] == 'import_csv':
            contacts.import_csv(cmd[1])
        elif cmd[0] == 'start_outreach':
            target = cmd[1] if len(cmd) > 1 else 'all'
            if target == 'all':
                for name in [c[0] for c in contacts.cursor.execute('SELECT name FROM contacts')]:
                    threading.Thread(target=bot.run_convo, args=(name,)).start()
            else:
                threading.Thread(target=bot.run_convo, args=(target,)).start()
        elif cmd[0] == 'random_chat':
            bot.random_chat_existing()
        elif cmd[0] == 'quit':
            break

    bot.close()
    contacts.close()

if __name__ == '__main__':
    main()
