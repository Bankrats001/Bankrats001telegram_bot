from telebot import TeleBot, types
from config import API_KEY, ADMIN_ID
import random
import time
import requests

bot = TeleBot(API_KEY)

#========== USER DATABASE & TIER SYSTEM (Temporary memory for now) ==========

users = {}

#Sample tiers: Free, Monthly, Lifetime

def get_user(user_id): if user_id not in users: users[user_id] = { 'tier': 'Free', 'credits': 10, 'username': None } return users[user_id]

#========== /START ==========

@bot.message_handler(commands=['start']) def start(message): uid = message.from_user.id user = get_user(uid) user['username'] = message.from_user.username or "NoUsername" caption = f"<b>💳 WELCOME TO BANK RATS CC CHECKER 💳</b>\n\n" caption += "🚀 Fastest. ⚡ Realistic. 👨‍💻 Admin-Controlled.\n\n" caption += "✅ Use /allcmdlist to see all commands.\n" caption += "🔐 Use /manualpay to upgrade tiers.\n" caption += "🛡 Use /disclaimer to view legal note.\n\n" caption += f"🧑‍💻 You are using: <b>{user['tier']} Tier</b>" bot.send_message(uid, caption, parse_mode='HTML')

#========== /ALLCMDLIST ==========

@bot.message_handler(commands=['allcmdlist']) def allcmds(message): uid = message.from_user.id user = get_user(uid) is_admin = str(uid) == ADMIN_ID

base = "<b>📜 COMMAND LIST</b>\n\n"
base += "/start - Start Bot\n"
base += "/binchk - Check BIN\n"
base += "/fakegen - Generate Fake Info\n"
base += "/chk - Mass Check Cards\n"
base += "/manualpay - Manual Upgrade\n"
base += "/feedback - Submit Feedback\n"
base += "/disclaimer - View Disclaimer\n"
if is_admin:
    base += "\n<b>🛠 ADMIN COMMANDS</b>\n"
    base += "/confirm - Confirm Manual Upgrade\n"
bot.send_message(uid, base, parse_mode='HTML')

#========== /BINCHK ==========

@bot.message_handler(commands=['binchk']) def binchk(message): args = message.text.split() if len(args) < 2: return bot.reply_to(message, "❌ Usage: /binchk <bin>")

bin_input = args[1][:6]
r = requests.get(f"https://lookup.binlist.net/{bin_input}")
if r.status_code != 200:
    return bot.reply_to(message, "⚠️ Invalid BIN or Source unreachable")

data = r.json()
brand = data.get('scheme', 'N/A')
card_type = data.get('type', 'N/A')
bank = data.get('bank', {}).get('name', 'N/A')
country = data.get('country', {}).get('name', 'N/A')
emoji = data.get('country', {}).get('emoji', '')
status = "✅ Live BIN" if brand.lower() != 'N/A' else "❌ Possibly Dead BIN"

result = f"<b>💳 BIN INFO</b>\n\n"
result += f"🏦 Bank: <b>{bank}</b>\n"
result += f"💳 Brand: {brand.upper()}\n"
result += f"🗂 Type: {card_type.upper()}\n"
result += f"🌍 Country: {country} {emoji}\n"
result += f"⚙ Status: <b>{status}</b>"
bot.send_message(message.chat.id, result, parse_mode='HTML')

#========== /FAKEGEN ==========

@bot.message_handler(commands=['fakegen']) def fakegen(message): names = ["Liam Johnson", "Emily Smith", "Noah Brown", "Ava Wilson"] streets = ["221B Baker St", "742 Evergreen Terrace", "1600 Pennsylvania Ave"] cities = ["New York", "Miami", "Dallas", "Los Angeles"] states = ["NY", "FL", "TX", "CA"]

result = f"<b>🎭 FAKE IDENTITY GEN</b>\n\n"
result += f"👤 Name: {random.choice(names)}\n"
result += f"📬 Address: {random.choice(streets)}\n"
result += f"🏙 City: {random.choice(cities)}\n"
result += f"🌆 State: {random.choice(states)}\n"
result += f"📮 ZIP: {random.randint(10000,99999)}\n"
result += f"📱 Phone: +1{random.randint(2000000000, 9999999999)}"
bot.send_message(message.chat.id, result, parse_mode='HTML')

#========== /MANUALPAY ==========

@bot.message_handler(commands=['manualpay']) def manualpay(message): msg = f"<b>💸 MANUAL PAYMENT</b>\n\n" msg += "To upgrade, send payment proof to admin.\n" msg += "Options:\n - Monthly Tier: $5\n - Lifetime Tier: $15\n\n" msg += "📤 Upload your screenshot here.\n🕒 We will confirm ASAP." bot.send_message(message.chat.id, msg, parse_mode='HTML')

#========== /CONFIRM (Admin Only) ==========

@bot.message_handler(commands=['confirm']) def confirm(message): if str(message.from_user.id) != ADMIN_ID: return bot.reply_to(message, "⛔ You're not authorized.")

args = message.text.split()
if len(args) < 3:
    return bot.reply_to(message, "Usage: /confirm <user_id> <tier>")

user_id = int(args[1])
new_tier = args[2].capitalize()
if user_id in users:
    users[user_id]['tier'] = new_tier
    bot.send_message(user_id, f"🎉 Your tier has been upgraded to: <b>{new_tier}</b>!", parse_mode='HTML')
    bot.send_message(message.chat.id, f"✅ User <code>{user_id}</code> upgraded to {new_tier}.", parse_mode='HTML')
else:
    bot.send_message(message.chat.id, "⚠ User not found or hasn't started the bot.")

#========== /FEEDBACK ==========

@bot.message_handler(commands=['feedback']) def feedback(message): bot.send_message(message.chat.id, "💬 Drop your feedback message and we’ll review.") bot.register_next_step_handler(message, save_feedback)

def save_feedback(msg): bot.send_message(ADMIN_ID, f"📩 FEEDBACK from @{msg.from_user.username or 'NoUser'} ({msg.from_user.id}):\n\n{msg.text}") bot.send_message(msg.chat.id, "✅ Thanks! Your feedback has been submitted.")

#========== /DISCLAIMER ==========

@bot.message_handler(commands=['disclaimer']) def disclaimer(message): msg = f"<b>⚠️ DISCLAIMER</b>\n\n" msg += "This bot is for educational and informational purposes only.\n" msg += "We are not affiliated with Telegram, Stripe, or any bank.\n" msg += "Usage of this bot must comply with all applicable laws.\n" msg += "❌ Misuse is strictly prohibited.\n\n" msg += "By using this bot, you agree to this disclaimer." bot.send_message(message.chat.id, msg, parse_mode='HTML')

#========== START BOT ==========

bot.infinity_polling()

