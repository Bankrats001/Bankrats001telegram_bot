import telebot
from telebot import types
from config import API_KEY, ADMIN_ID

bot = telebot.TeleBot(API_KEY)

# User database (in-memory)
users = {}

# Sample tiers: Free, Monthly, Lifetime

def get_user(user_id):
    if user_id not in users:
        users[user_id] = {
            'tier': 'Free',
            'credits': 50,
            'username': None
        }
    return users[user_id]

def is_owner(user_id):
    return str(user_id) == str(ADMIN_ID)

# Styled message for unauthorized access
def owner_only_msg():
    return "<b>🚫 This command is restricted to the Owner Only.</b>\n\nFor questions, contact @Bank_Rats."

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if uid not in users:
        bot.send_message(uid, "❌ You are not registered yet!\n\nPlease type /register to activate your account and start using the bot. 🚀\n\nNeed assistance? Contact the owner here: @Bank_Rats")
        return

    user = get_user(uid)
    caption = f"<b>💳 WELCOME TO BANK RATS CC CHECKER 💳</b>\n\n"
    caption += "🚀 Fastest. ⚡ Realistic. 👨‍💻 Admin-Controlled.\n\n"
    caption += "✅ Use /allcmdlist to see all commands.\n"
    caption += "🔐 Use /manualpay to upgrade tiers.\n"
    caption += "🛡 Use /disclaimer to view legal note.\n\n"
    caption += f"🧑‍💻 You are using: <b>{user['tier']} Tier</b>"
    bot.send_message(uid, caption, parse_mode='HTML')

@bot.message_handler(commands=['register'])
def register(message):
    uid = message.from_user.id
    if uid in users:
        bot.send_message(uid, "You are already registered! Use /check or /buy.")
        return

    user = get_user(uid)
    user['username'] = message.from_user.username or "NoUsername"
    user['credits'] = 50
    user['tier'] = 'Free'
    caption = "🎉 Welcome to BANK_RATS 🐀💳\nYou have been registered successfully!\n\n💰 50 free credits have been added to your account.\nUse /check to start checking now.\n🔥 Use /buy to upgrade for full features & unlimited checks!"
    bot.send_message(uid, caption)

@bot.message_handler(commands=['mycredits'])
def mycredits(message):
    uid = message.from_user.id
    if uid not in users:
        bot.send_message(uid, "❌ You are not registered yet! Use /register to continue.")
        return
    user = users[uid]
    bot.send_message(uid, f"💼 Tier: <b>{user['tier']}</b>\n💰 Credits: <b>{user['credits']}</b>", parse_mode='HTML')

@bot.message_handler(commands=['allcmdlist'])
def allcmdlist(message):
    uid = message.from_user.id
    if uid not in users:
        bot.send_message(uid, "❌ You are not registered yet! Use /register.")
        return

    bot.send_message(uid, "📜 Available Commands:\n/start\n/register\n/mycredits\n/buy\n/disclaimer\n")

@bot.message_handler(commands=['buy'])
def buy(message):
    uid = message.from_user.id
    if uid not in users:
        bot.send_message(uid, "❌ You are not registered yet! Use /register.")
        return

    caption = "<b>🛍 UPGRADE PLANS</b>\n\n"
    caption += "1️⃣ Monthly — $3 / ~Ksh\n✔️ BIN Check\n✔️ Mass Check\n✔️ Generators\n✔️ 50 checks/day\n\n"
    caption += "2️⃣ Lifetime — $5 / ~Ksh\n✔️ Everything in Monthly\n✔️ Unlimited Checks\n✔️ Deep Checks\n✔️ Vault\n✔️ Weekly BINs\n\n"
    caption += "<b>✅ Accepted Payments:</b>\n💳 Binance: migosblazer4@gmail.com\n📲 M-PESA: +254746362427\n\nUpload payment screenshot here ⬇️"
    bot.send_message(uid, caption, parse_mode='HTML')

@bot.message_handler(commands=['disclaimer'])
def disclaimer(message):
    uid = message.from_user.id
    bot.send_message(uid, "📜 <b>DISCLAIMER</b>\n\nThis bot is for educational and research purposes only.\n\nWe do not support illegal activities. Use responsibly.\n\nBy continuing, you agree you are fully responsible for how you use this tool.", parse_mode='HTML')

@bot.message_handler(commands=['users'])
def users_list(message):
    uid = message.from_user.id
    if not is_owner(uid):
        bot.send_message(uid, owner_only_msg(), parse_mode='HTML')
        return

    if not users:
        bot.send_message(uid, "No users registered yet.")
        return

    caption = "<b>👥 REGISTERED USERS:</b>\n"
    for i, (user_id, data) in enumerate(users.items(), start=1):
        caption += f"{i}. {data['username']} — Tier: {data['tier']} — Credits: {data['credits']}\n"

    bot.send_message(uid, caption, parse_mode='HTML')

# Block unregistered users from all commands
@bot.message_handler(func=lambda message: True)
def block_others(message):
    uid = message.from_user.id
    if uid not in users and message.text not in ["/start", "/register"]:
        bot.send_message(uid, "❌ You are not registered yet!\nUse /register to continue.")
    else:
        bot.send_message(uid, "❓ Unknown command, use /allcmdlist to see available commands.")

bot.polling(none_stop=True)
