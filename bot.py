from telebot import TeleBot, types
from config import API_KEY, ADMIN_ID
import random
import time
import requests

bot = TeleBot(API_KEY)

========== USER DATABASE & TIER SYSTEM (Temporary memory for now) ==========

users = {}

Sample tiers: Free, Monthly, Lifetime

def get_user(user_id): if user_id not in users: users[user_id] = {'tier': 'Free', 'credits': 10, 'username': None} return users[user_id]

========== /START ==========

@bot.message_handler(commands=['start']) def start(message): uid = message.from_user.id user = get_user(uid) user['username'] = message.from_user.username or "NoUsername" caption = f"<b>\ud83d\udcb3 WELCOME TO BANK RATS CC CHECKER \ud83d\udcb3</b>\n\n" caption += "\ud83d\ude80 Fastest. \u26a1 Realistic. \ud83d\udc68\u200d\ud83d\udcbb Admin-Controlled.\n\n" caption += "\u2705 Use /allcmdlist to see all commands.\n" caption += "\ud83d\udd10 Use /manualpay to upgrade tiers.\n" caption += "\ud83d\udee1 Use /disclaimer to view legal note.\n\n" caption += f"\ud83e\uddd1\u200d\ud83d\udcbb You are using: <b>{user['tier']} Tier</b>" bot.send_message(uid, caption, parse_mode='HTML')

========== /ALLCMDLIST ==========

@bot.message_handler(commands=['allcmdlist']) def allcmds(message): uid = message.from_user.id user = get_user(uid) is_admin = str(uid) == ADMIN_ID

base = "<b>\ud83d\udcdc COMMAND LIST</b>\n\n"
base += "/start - Start Bot\n"
base += "/binchk - Check BIN\n"
base += "/fakegen - Generate Fake Info\n"
base += "/chk - Mass Check Cards\n"
base += "/manualpay - Manual Upgrade\n"
base += "/feedback - Submit Feedback\n"
base += "/disclaimer - View Disclaimer\n"
if is_admin:
    base += "\n<b>\ud83d\udee0 ADMIN COMMANDS</b>\n"
    base += "/confirm - Confirm Manual Upgrade\n"
bot.send_message(uid, base, parse_mode='HTML')

========== /BINCHK ==========

@bot.message_handler(commands=['binchk']) def binchk(message): args = message.text.split() if len(args) < 2: return bot.reply_to(message, "\u274c Usage: /binchk <bin>")

bin_input = args[1][:6]
r = requests.get(f"https://lookup.binlist.net/{bin_input}")
if r.status_code != 200:
    return bot.reply_to(message, "\u26a0\ufe0f Invalid BIN or Source unreachable")

data = r.json()
brand = data.get('scheme', 'N/A')
card_type = data.get('type', 'N/A')
bank = data.get('bank', {}).get('name', 'N/A')
country = data.get('country', {}).get('name', 'N/A')
emoji = data.get('country', {}).get('emoji', '')
status = "\u2705 Live BIN" if brand.lower() != 'N/A' else "\u274c Possibly Dead BIN"

result = f"<b>\ud83d\udcb3 BIN INFO</b>\n\n"
result += f"\ud83c\udfe6 Bank: <b>{bank}</b>\n"
result += f"\ud83d\udcb3 Brand: {brand.upper()}\n"
result += f"\ud83d\uddc2 Type: {card_type.upper()}\n"
result += f"\ud83c\udf0d Country: {country} {emoji}\n"
result += f"\u2699 Status: <b>{status}</b>"
bot.send_message(message.chat.id, result, parse_mode='HTML')

========== /FAKEGEN ==========

@bot.message_handler(commands=['fakegen']) def fakegen(message): names = ["Liam Johnson", "Emily Smith", "Noah Brown", "Ava Wilson"] streets = ["221B Baker St", "742 Evergreen Terrace", "1600 Pennsylvania Ave"] cities = ["New York", "Miami", "Dallas", "Los Angeles"] states = ["NY", "FL", "TX", "CA"]

result = f"<b>\ud83c\udfad FAKE IDENTITY GEN</b>\n\n"
result += f"\ud83d\udc64 Name: {random.choice(names)}\n"
result += f"\ud83d\udcec Address: {random.choice(streets)}\n"
result += f"\ud83c\udf03 City: {random.choice(cities)}\n"
result += f"\ud83c\udf06 State: {random.choice(states)}\n"
result += f"\ud83d\udcec ZIP: {random.randint(10000,99999)}\n"
result += f"\ud83d\udcf1 Phone: +1{random.randint(2000000000, 9999999999)}"
bot.send_message(message.chat.id, result, parse_mode='HTML')

========== /MANUALPAY ==========

@bot.message_handler(commands=['manualpay']) def manualpay(message): msg = f"<b>\ud83d\udcb8 MANUAL PAYMENT</b>\n\n" msg += "To upgrade, send payment proof to admin.\n" msg += "Options:\n - Monthly Tier: $5\n - Lifetime Tier: $15\n\n" msg += "\ud83d\udcec Upload your screenshot here.\n\ud83d\udd52 We will confirm ASAP." bot.send_message(message.chat.id, msg, parse_mode='HTML')

========== /CONFIRM (Admin Only) ==========

@bot.message_handler(commands=['confirm']) def confirm(message): if str(message.from_user.id) != ADMIN_ID: return bot.reply_to(message, "\u26d4 You're not authorized.")

args = message.text.split()
if len(args) < 3:
    return bot.reply_to(message, "Usage: /confirm <user_id> <tier>")

user_id = int(args[1])
new_tier = args[2].capitalize()
if user_id in users:
    users[user_id]['tier'] = new_tier
    bot.send_message(user_id, f"\ud83c\udf89 Your tier has been upgraded to: <b>{new_tier}</b>!", parse_mode='HTML')
    bot.send_message(message.chat.id, f"\u2705 User <code>{user_id}</code> upgraded to {new_tier}.", parse_mode='HTML')
else:
    bot.send_message(message.chat.id, "\u26a0 User not found or hasn't started the bot.")

========== /FEEDBACK ==========

@bot.message_handler(commands=['feedback']) def feedback(message): bot.send_message(message.chat.id, "\ud83d\udcac Drop your feedback message and we’ll review.") bot.register_next_step_handler(message, save_feedback)

def save_feedback(msg): bot.send_message(ADMIN_ID, f"\ud83d\udce9 FEEDBACK from @{msg.from_user.username or 'NoUser'} ({msg.from_user.id}):\n\n{msg.text}") bot.send_message(msg.chat.id, "\u2705 Thanks! Your feedback has been submitted.")

========== /DISCLAIMER ==========

@bot.message_handler(commands=['disclaimer']) def disclaimer(message): msg = "<b>\u26d4 DISCLAIMER</b>\n\n" msg += "This bot is for educational and testing purposes only.\n" msg += "We do not promote or support any illegal activity.\n" msg += "We are not affiliated with Telegram, banks, or payment services.\n\n" msg += "By using this bot, you agree to take full responsibility for your actions." bot.send_message(message.chat.id, msg, parse_mode='HTML')

========== START BOT ==========

bot.infinity_polling()

