import os
import telebot
from telebot import types
import sqlite3

# BOT TOKEN & ADMIN ID
API_TOKEN = os.getenv("BOT_API_TOKEN", "YOUR_BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "123456789"))

bot = telebot.TeleBot(API_TOKEN, parse_mode="HTML")

# PAYMENT INFO
PAYMENT_METHODS = {
    "Binance": "migosblazer4@gmail.com",
    "M-PESA": "+254746362427"
}

# TIER SYSTEM CONFIGURATION
TIERS = {
    "Free": {
        "credits": 50,
        "check_cost": 5,
        "max_commands": 5,
        "features": ["/start", "/check", "/register", "/buy", "/credits", "/referral", "/myreferrals"]
    },
    "Monthly": {
        "credits": 9999,
        "check_cost": 2,
        "max_commands": 50,
        "features": ["/start", "/check", "/masschk", "/generate", "/generateinfo", "/bin", "/buy", "/credits", "/referral", "/myreferrals", "/stats", "/me"]
    },
    "Lifetime": {
        "credits": 99999,
        "check_cost": 1,
        "max_commands": 9999,
        "features": ["/start", "/check", "/masschk", "/generate", "/generateinfo", "/bin", "/deepchk", "/vault", "/autocharge", "/binweekly", "/binstats", "/buy", "/credits", "/referral", "/myreferrals", "/log", "/me"]
    }
}

# STARTUP CREDIT REWARD
START_CREDITS = 50

# DATABASE FILE
DATABASE_NAME = "bankrats_users.db"

# BIN API SOURCES
BIN_LOOKUP_API = "https://lookup.binlist.net/"

# FAKE INFO GENERATOR
FAKEGEN_API = "https://randomuser.me/api/"

# ADDITIONAL CONFIGS
COMMAND_LIMIT_RESET_HOURS = 24

# COMMAND HELP MAP (TIER BASED FOR DYNAMIC CMD LISTS)
ALL_COMMANDS = {
    "/start": "Start the bot",
    "/register": "Register your account",
    "/check": "Single CC checker",
    "/masschk": "Mass CC check (Premium only)",
    "/generate": "Generate CCs (Premium)",
    "/generateinfo": "Generate fake identity info",
    "/bin": "BIN lookup",
    "/deepchk": "Deep CC validation (Lifetime only)",
    "/vault": "Access premium vault",
    "/autocharge": "Auto charging (Lifetime only)",
    "/binweekly": "Weekly BIN drops",
    "/binstats": "BIN statistics (Lifetime)",
    "/buy": "Upgrade to premium tiers",
    "/credits": "Check your current credits",
    "/referral": "Get your referral link",
    "/myreferrals": "Check your referral stats",
    "/log": "Your past checks log",
    "/me": "View your profile",
    "/users": "Admin only - list users",
    "/broadcast": "Admin only - send update to all users"
}

# USD-KSH Converter API (optional)
EXCHANGE_RATE_API = "https://api.exchangerate-api.com/v4/latest/USD"

# LOGGING SETUP
ENABLE_LOGGING = True
