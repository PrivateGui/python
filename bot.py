import requests
import time
import re

# Your bot token and API base URL
BOT_TOKEN = "1187305194:RfSzejwFv9JDL3IwWoGv31BSqg97oVvu6oYT9TvX"
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"

# List of offensive words in Persian
offensive_words = [
    "کیر", "کص", "کون", "کونده", "کصده", "جنده", "کصمادر",
    "اوبی", "اوبنه ای", "تاقال", "تاقار", "حروم", "لواط",
    "گی", "سکس", "گایید"
]

# Blacklisted links
blacklisted_links = ["ble.ir", "bale.ai"]

# Dictionary to track warnings
warnings = {}

# Function to send a message
def send_message(chat_id, text, reply_to_message_id=None):
    url = f"{BASE_URL}/sendMessage"
    payload = {'chat_id': chat_id, 'text': text}
    if reply_to_message_id:
        payload['reply_to_message_id'] = reply_to_message_id
    try:
        requests.post(url, json=payload)
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}")

# Function to delete a message
def delete_message(chat_id, message_id):
    url = f"{BASE_URL}/deleteMessage"
    payload = {'chat_id': chat_id, 'message_id': message_id}
    try:
        requests.post(url, json=payload)
    except requests.exceptions.RequestException as e:
        print(f"Error deleting message: {e}")

# Function to ban a user
def ban_user(chat_id, user_id, first_name, username, reply_to_message_id, reason="به دلیل ۳ اخطار از گروه حذف شد"):
    url = f"{BASE_URL}/banChatMember"
    payload = {'chat_id': chat_id, 'user_id': user_id}
    try:
        requests.post(url, json=payload)
        send_message(chat_id, f"کاربر @{username} ({first_name}) {reason}", reply_to_message_id=reply_to_message_id)
    except requests.exceptions.RequestException as e:
        print(f"Error banning user: {e}")

# Function to get chat admins
def get_chat_admins(chat_id):
    url = f"{BASE_URL}/getChatAdministrators"
    try:
        response = requests.post(url, json={'chat_id': chat_id})
        response.raise_for_status()
        return response.json().get('result', [])
    except requests.exceptions.RequestException as e:
        print(f"Error getting admins: {e}")
        return []

# Check if a user is an admin
def is_admin(user_id, chat_id):
    admins = get_chat_admins(chat_id)
    if not admins:
        return False
    return any('user' in admin and admin['user'].get('id') == user_id for admin in admins)

# Check for blacklisted links
def contains_blacklisted_link(text):
    return any(re.search(rf"\b{link}\b", text) for link in blacklisted_links)

# Get bot updates
def get_updates(offset=None):
    url = f"{BASE_URL}/getUpdates"
    try:
        response = requests.get(url, params={'offset': offset, 'timeout': 10})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting updates: {e}")
        return None

# Main function to process updates
def process_check():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if updates and 'result' in updates and updates['result']:
            for update in updates['result']:
                message = update.get('message', {})
                if not message or 'chat' not in message or 'from' not in message:
                    continue

                chat_id = message['chat']['id']
                user_id = message['from']['id']
                first_name = message['from'].get('first_name', 'Unknown')
                username = message['from'].get('username', 'Unknown')
                text = message.get('text', "")
                reply_to_message = message.get('reply_to_message', {})
                admin_message_id = message['message_id']

                # Check for offensive words
                if any(word in text for word in offensive_words):
                    if not is_admin(user_id, chat_id):
                        warnings[user_id] = warnings.get(user_id, 0) + 1
                        if warnings[user_id] < 3:
                            send_message(chat_id, f"کاربر @{username} ({first_name}) به دلیل استفاده از کلمات نامناسب اخطار گرفت. ({warnings[user_id]}/3)", 
                                         reply_to_message_id=admin_message_id)
                        else:
                            ban_user(chat_id, user_id, first_name, username, reply_to_message_id=admin_message_id)
                            del warnings[user_id]

                # Check for blacklisted links
                elif contains_blacklisted_link(text):
                    if not is_admin(user_id, chat_id):
                        warnings[user_id] = warnings.get(user_id, 0) + 1
                        if warnings[user_id] < 3:
                            send_message(chat_id, f"کاربر @{username} ({first_name}) به دلیل ارسال لینک غیرمجاز اخطار گرفت. ({warnings[user_id]}/3)", 
                                         reply_to_message_id=admin_message_id)
                        else:
                            ban_user(chat_id, user_id, first_name, username, reply_to_message_id=admin_message_id)
                            del warnings[user_id]

                # Admin commands
                if is_admin(user_id, chat_id):
                    if text.strip() == "اخطار" and reply_to_message:
                        target_user_id = reply_to_message['from']['id']
                        if is_admin(target_user_id, chat_id):
                            send_message(chat_id, "نمیتونی رو ادمین ها کاری انجام بدی", reply_to_message_id=admin_message_id)
                        else:
                            warnings[target_user_id] = warnings.get(target_user_id, 0) + 1
                            target_username = reply_to_message['from'].get('username', 'Unknown')
                            send_message(chat_id, f"کاربر @{target_username} اخطار گرفت. ({warnings[target_user_id]}/3)", 
                                         reply_to_message_id=admin_message_id)

                    elif text.strip() == "حذف" and reply_to_message:
                        target_user_id = reply_to_message['from']['id']
                        if is_admin(target_user_id, chat_id):
                            send_message(chat_id, "نمیتونی پیام‌های ادمین‌ها رو حذف کنی", reply_to_message_id=admin_message_id)
                        else:
                            delete_message(chat_id, reply_to_message['message_id'])
                            send_message(chat_id, "پیام حذف شد", reply_to_message_id=admin_message_id)

                    elif text.strip() == "ریم" and reply_to_message:
                        target_user_id = reply_to_message['from']['id']
                        if is_admin(target_user_id, chat_id):
                            send_message(chat_id, "نمیتونی ادمین‌ها رو حذف کنی", reply_to_message_id=admin_message_id)
                        else:
                            target_username = reply_to_message['from'].get('username', 'Unknown')
                            ban_user(chat_id, target_user_id, first_name, target_username, reply_to_message_id=admin_message_id,
                                     reason="توسط ادمین از گروه حذف شد")

                # Update last_update_id
                last_update_id = update['update_id'] + 1

        time.sleep(1)

# Start the bot
process_check()
                                                                                                                              
