from telebot import TeleBot, types
from config import API_KEY, ADMIN_ID
import random
import time
import requests

bot = TeleBot(API_KEY)

# ========== USER DATABASE & TIER SYSTEM ==========
users = {}

def get_user(user_id):
    if user_id not in users:
        users[user_id] = {'tier': 'Free', 'credits': 50, 'username': None}
    return users[user_id]

# ========== /start COMMAND ========== 
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    user = get_user(uid)
    user['username'] = message.from_user.username or "NoUsername"
    caption = f"<b>💳 WELCOME TO BANK RATS CC CHECKER 💳</b>\n\n"
    caption += "🚀 <i>Fastest.</i> ⚡ <i>Realistic.</i> 👨‍💻 <i>Admin-Controlled.</i>\n\n"
    caption += "✅ Use /allcmdlist to see all commands.\n"
    caption += "🔐 Use /manualpay to upgrade tiers.\n"
    caption += "🛡 Use /disclaimer to view legal note.\n\n"
    caption += f"🧑‍💻 <b>You are using:</b> <code>{user['tier']} Tier</code>"
    bot.send_message(uid, caption, parse_mode='HTML')

# ========== /register COMMAND ==========
@bot.message_handler(commands=['register'])
def register(message):
    uid = message.from_user.id
    if uid in users:
        bot.reply_to(message, "✅ You are already registered!")
    else:
        users[uid] = {'tier': 'Free', 'credits': 50, 'username': message.from_user.username or "NoUsername"}
        bot.reply_to(message, "🎉 Welcome to BANK_RATS 🐀💳\nYou have been registered successfully!\n\n💰 50 free credits have been added to your account.\nUse /check to start checking now.\n🔥 Use /buy to upgrade for full features & unlimited checks!")

# ========== /credits COMMAND ==========
@bot.message_handler(commands=['credits'])
def show_credits(message):
    uid = message.from_user.id
    user = get_user(uid)
    bot.reply_to(message, f"💰 You have <b>{user['credits']} credits</b> remaining.", parse_mode='HTML')

# ========== OWNER-ONLY: /users COMMAND ==========
@bot.message_handler(commands=['users'])
def list_users(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "🚫 <b>This command is restricted to the Owner Only.</b>\n\nContact @Bank_Rats for any assistance.", parse_mode='HTML')
        return
    text = "📋 <b>REGISTERED USERS LIST</b>\n\n"
    count = 0
    for uid, data in users.items():
        text += f"👤 <b>Username:</b> @{data['username']}\n🆔 <b>ID:</b> {uid}\n🏷️ <b>Tier:</b> {data['tier']}\n💰 <b>Credits:</b> {data['credits']}\n\n"
        count += 1
    text += f"👑 <i>Total Users:</i> {count}"
    bot.send_message(message.chat.id, text, parse_mode='HTML')

# ========== /disclaimer COMMAND ==========
@bot.message_handler(commands=['disclaimer'])
def disclaimer(message):
    disclaimer_text = "⚠️ <b>DISCLAIMER</b>\n\n"
    disclaimer_text += "This bot is created strictly for educational purposes only.\n"
    disclaimer_text += "The developer does not promote, support, or engage in any illegal activities.\n"
    disclaimer_text += "Use of this bot is at your own risk.\n\n"
    disclaimer_text += "👮‍♂️ All activities are logged."
    bot.reply_to(message, disclaimer_text, parse_mode='HTML')

# ========== HANDLE ALL OTHER COMMANDS ==========
@bot.message_handler(func=lambda m: True)
def unknown_command(message):
    if message.text.startswith('/') and message.text != '/start':
        uid = message.from_user.id
        if uid not in users:
            bot.reply_to(message, "❌ You are not registered yet!\n\nPlease type /register to activate your account and start using the bot. 🚀\n\nNeed assistance? Contact the owner here: @Bank_Rats")
        else:
            bot.reply_to(message, "❓ Unknown command. Please use /allcmdlist to see available commands.")

bot.infinity_polling()

