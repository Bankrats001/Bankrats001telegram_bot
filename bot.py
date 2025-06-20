# bot.py
import telebot
import requests
import time
import random
import threading
from config import API_TOKEN, ADMIN_USER_ID, BINANCE_EMAIL, MPESA_NUMBER, USD_KSH_RATE

# In-memory DB (temp — for testing)
users = {}
referrals = {}
banned_users = []

# Set your tiers (USD price — KSH auto calculated)
TIERS = {
    "Monthly": 3,
    "Lifetime": 5
}

# Create bot
bot = telebot.TeleBot(API_TOKEN)

# Auto KSH calc
def usd_to_ksh(usd_amount):
    return round(usd_amount * USD_KSH_RATE, 2)

# Command: /start
@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    if user_id in banned_users:
        bot.reply_to(message, "🚫 You are BANNED from using this bot.")
        return

    if user_id not in users:
        users[user_id] = {
            "credits": 50,
            "plan": "Free",
            "referrals": 0
        }
        bot.reply_to(message, f"👋 Welcome to BANK_RATS CC CHECKER!\n\n💎 You've been awarded 50 credits.\n\nUse /help to see available commands.")

    else:
        bot.reply_to(message, f"👋 Welcome back!\n\nUse /help to see available commands.")

# Command: /help
@bot.message_handler(commands=['help'])
def help_cmd(message):
    user_id = message.from_user.id
    if user_id in banned_users:
        return

    text = "💎 BANK_RATS COMMANDS 💎\n\n"
    text += "👉 /status - View your plan & credits\n"
    text += "👉 /subscribe - View plans & pay\n"
    text += "👉 /fakegen - Generate fake info\n"
    text += "👉 /binchk - BIN lookup (limited)\n"
    text += "👉 /msschk - Mass check (limited)\n"
    text += "👉 /ccgen - Generate CCs (limited)\n"
    text += "👉 /referralrank - Top referrers\n"
    text += "👉 /viprank - VIP user ranks\n"

    if user_id == ADMIN_USER_ID:
        text += "\n👑 ADMIN COMMANDS 👑\n"
        text += "👉 /ban <user_id>\n"
        text += "👉 /unban <user_id>\n"
        text += "👉 /broadcast <msg>\n"
        text += "👉 /setrate <rate>\n"

    bot.reply_to(message, text)

# Command: /status
@bot.message_handler(commands=['status'])
def status_cmd(message):
    user_id = message.from_user.id
    if user_id in banned_users:
        return

    if user_id not in users:
        bot.reply_to(message, "❌ You are not registered. Please /start first.")
        return

    u = users[user_id]
    text = f"👤 User ID: {user_id}\n"
    text += f"💎 Plan: {u['plan']}\n"
    text += f"💰 Credits: {u['credits']}\n"
    text += f"🎁 Referrals: {u['referrals']}"

    bot.reply_to(message, text)

# Command: /subscribe
@bot.message_handler(commands=['subscribe'])
def subscribe_cmd(message):
    text = "💳 Subscription Plans:\n\n"
    for tier, price_usd in TIERS.items():
        price_ksh = usd_to_ksh(price_usd)
        text += f"👉 {tier}: ${price_usd} → Ksh {price_ksh}\n"

    text += "\nPayment Methods:\n"
    text += f"✅ Binance: {BINANCE_EMAIL}\n"
    text += f"✅ M-Pesa: {MPESA_NUMBER}\n"
    text += "\nAfter payment, upload screenshot here to unlock your plan!"

    bot.reply_to(message, text)

# Command: /setrate (ADMIN)
@bot.message_handler(commands=['setrate'])
def setrate_cmd(message):
    user_id = message.from_user.id
    if user_id != ADMIN_USER_ID:
        bot.reply_to(message, "🚫 You don't have admin rights!")
        return

    try:
        rate = float(message.text.split()[1])
        global USD_KSH_RATE
        USD_KSH_RATE = rate
        bot.reply_to(message, f"✅ USD → Ksh rate updated: {USD_KSH_RATE}")
    except:
        bot.reply_to(message, "❌ Usage: /setrate <rate>")

# Command: /ban
@bot.message_handler(commands=['ban'])
def ban_cmd(message):
    user_id = message.from_user.id
    if user_id != ADMIN_USER_ID:
        bot.reply_to(message, "🚫 You don't have admin rights!")
        return

    try:
        target_id = int(message.text.split()[1])
        banned_users.append(target_id)
        bot.reply_to(message, f"✅ User {target_id} has been banned.")
    except:
        bot.reply_to(message, "❌ Usage: /ban <user_id>")

# Command: /unban
@bot.message_handler(commands=['unban'])
def unban_cmd(message):
    user_id = message.from_user.id
    if user_id != ADMIN_USER_ID:
        bot.reply_to(message, "🚫 You don't have admin rights!")
        return

    try:
        target_id = int(message.text.split()[1])
        if target_id in banned_users:
            banned_users.remove(target_id)
            bot.reply_to(message, f"✅ User {target_id} has been unbanned.")
        else:
            bot.reply_to(message, "❌ User is not banned.")
    except:
        bot.reply_to(message, "❌ Usage: /unban <user_id>")

# Background thread: (later will add referrals, fakegen, ccgen etc.)

# Polling loop
print("🤖 BANK_RATS BOT is RUNNING!")
bot.infinity_polling()
