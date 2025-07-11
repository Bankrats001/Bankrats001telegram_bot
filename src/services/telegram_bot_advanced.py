import os
import logging
import hashlib
import time
import asyncio
import random
import re
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.constants import ParseMode
from src.config import Config
from src.models.user import db, User, CreditTransaction, ValidationLog, Payment, AdminNotification, SubscriptionType, PaymentMethod, PaymentStatus, BinCache
from src.services.bin_checker import BinChecker
from src.services.charged_checker import ChargedChecker
from src.services.cc_generator import CCGenerator
from src.services.currency_service import CurrencyService

# Configure logging
logging.basicConfig(
    format=\'%(asctime)s - %(name)s - %(levelname)s - %(message)s\',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class BankRatsCCCheckerBot:
    \"\"\"BANK_RATS CC CHECKER BOT🐀 - Advanced Telegram Bot\"\"\"
    
    def __init__(self, token, flask_app):
        self.token = token
        self.flask_app = flask_app
        self.application = Application.builder().token(token).build()
        
        # Initialize services
        self.bin_checker = BinChecker()
        self.charged_checker = ChargedChecker()
        self.cc_generator = CCGenerator()
        self.currency_service = CurrencyService()
        
        # Bot configuration
        self.bot_name = Config.BOT_NAME
        self.bot_emoji = Config.BOT_EMOJI
        self.owner_username = Config.OWNER_USERNAME
        self.admin_id = Config.ADMIN_ID
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        \"\"\"Setup all command and message handlers\"\"\"
        # Basic commands
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("register", self.register_command))
        
        # Checking commands
        self.application.add_handler(CommandHandler("check", self.check_command))
        self.application.add_handler(CommandHandler("masschk", self.mass_check_command))
        self.application.add_handler(CommandHandler("deepchk", self.deep_check_command))
        
        # Generation commands
        self.application.add_handler(CommandHandler("generate", self.generate_command))
        self.application.add_handler(CommandHandler("generateinfo", self.generate_info_command))
        
        # BIN commands
        self.application.add_handler(CommandHandler("bin", self.bin_command))
        self.application.add_handler(CommandHandler("binstats", self.bin_stats_command))
        self.application.add_handler(CommandHandler("binweekly", self.bin_weekly_command))
        
        # Premium commands
        self.application.add_handler(CommandHandler("vault", self.vault_command))
        self.application.add_handler(CommandHandler("autocharge", self.autocharge_command))
        self.application.add_handler(CommandHandler("log", self.log_command))
        
        # Account commands
        self.application.add_handler(CommandHandler("buy", self.buy_command))
        self.application.add_handler(CommandHandler("credits", self.credits_command))
        self.application.add_handler(CommandHandler("me", self.me_command))
        
        # Referral commands
        self.application.add_handler(CommandHandler("referral", self.referral_command))
        self.application.add_handler(CommandHandler("myreferrals", self.my_referrals_command))
        
        # Utility commands
        self.application.add_handler(CommandHandler("disclaimer", self.disclaimer_command))
        
        # Owner commands
        self.application.add_handler(CommandHandler("users", self.users_command))
        self.application.add_handler(CommandHandler("broadcast", self.broadcast_command))
        
        # Callback and message handlers
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        self.application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    def _get_or_create_user(self, telegram_user):
        \"\"\"Get existing user or create new one\"\"\"
        with self.flask_app.app_context():
            user = User.query.filter_by(telegram_id=telegram_user.id).first()
            if not user:
                user = User(
                    telegram_id=telegram_user.id,
                    username=telegram_user.username,
                    first_name=telegram_user.first_name,
                    last_name=telegram_user.last_name,
                    is_registered=False
                )
                db.session.add(user)
                db.session.commit()
                logger.info(f"New user created: {telegram_user.id}")
            else:
                # Update user info and activity
                user.username = telegram_user.username
                user.first_name = telegram_user.first_name
                user.last_name = telegram_user.last_name
                user.last_activity = datetime.utcnow()
                db.session.commit()
            
            return user
    
    def _check_registration(self, user):
        \"\"\"Check if user is registered\"\"\"
        return user.is_registered
    
    def _check_command_access(self, user, command):
        \"\"\"Check if user can access command\"\"\"
        if not self._check_registration(user) and command != \'register\':
            return False, Config.MESSAGES[\'not_registered\']
        
        if command in Config.OWNER_COMMANDS:
            if user.telegram_id != Config.ADMIN_ID:
                return False, Config.MESSAGES[\'owner_only\']
        
        if not user.can_use_command(command):
            return False, Config.MESSAGES[\'tier_restricted\']
        
        return True, None
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        \"\"\"Handle /start command\"\"\"
        user = self._get_or_create_user(update.effective_user)
        
        # Check for referral code
        if context.args and context.args[0].startswith(\'ref_\'):
            referral_code = context.args[0][4:]  # Remove \'ref_\' prefix
            await self._handle_referral(user, referral_code)
        
        if not self._check_registration(user):
            await update.message.reply_text(
                Config.MESSAGES[\'not_registered\'],
                parse_mode=ParseMode.HTML
            )
        else:
            tier = user.get_tier()
            tier_emoji = "🆓" if tier == "free" else "👑" if tier == "monthly" else "⚡"
            
            welcome_text = f\"\"\"🐀💳 <b>Welcome back to {Config.BOT_NAME}!</b>
            
👤 <b>User:</b> {update.effective_user.first_name}
{tier_emoji} <b>Tier:</b> {Config.TIER_NAMES[tier]}
🪙 <b>Credits:</b> {user.credits}
📅 <b>Member since:</b> {user.created_at.strftime(\'%Y-%m-%d\')}

🔥 Ready to check some cards? Use /check to get started!
💎 Want more features? Use /buy to upgrade!\"\"\"
            
            await update.message.reply_text(welcome_text, parse_mode=ParseMode.HTML)
    
    async def register_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        \"\"\"Handle /register command\"\"\"
        user = self._get_or_create_user(update.effective_user)
        
        if user.is_registered:
            await update.message.reply_text(
                "✅ You are already registered!",
                parse_mode=ParseMode.HTML
            )
            return
        
        # Register user
        user.is_registered = True
        user.credits = Config.REGISTRATION_BONUS_CREDITS
        
        # Add bonus credit transaction
        bonus_transaction = CreditTransaction(
            user=user,
            amount=Config.REGISTRATION_BONUS_CREDITS,
            transaction_type=\'bonus\',
            description=\'Registration bonus\'
        )
        db.session.add(bonus_transaction)
        db.session.commit()
        
        await update.message.reply_text(
            Config.MESSAGES[\'registration_success\'],
            parse_mode=ParseMode.HTML
        )
        
        # Notify admin
        await self._notify_admin(
            \'new_user\',
            \'New User Registration\',
            f"New user registered: @{user.username or user.first_name} (ID: {user.telegram_id})"
        )
    
    async def check_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        \"\"\"Handle /check command\"\"\"
        user = self._get_or_create_user(update.effective_user)
        
        # Check access
        can_access, error_msg = self._check_command_access(user, \'check\')
        if not can_access:
            await update.message.reply_text(error_msg, parse_mode=ParseMode.HTML)
            return
        
        # Check if user has credits
        if not user.has_credits_for_check():
            await update.message.reply_text(
                "❌ Insufficient credits! Use /buy to purchase more credits.",
                parse_mode=ParseMode.HTML
            )
            return
        
        # Check daily limit
        if not user.can_check_today():
            tier = user.get_tier()
            daily_limit = Config.TIER_LIMITS[tier][\'checks_per_day\']
            await update.message.reply_text(
                f"❌ Daily limit reached! You can perform {daily_limit} checks per day on {Config.TIER_NAMES[tier]} tier.",
                parse_mode=ParseMode.HTML
            )
            return
        
        # Parse card details
        if not context.args:
            await update.message.reply_text(
                "❌ Please provide card details!\n\nFormat: /check 4532123456789012|12|2025|123",
                parse_mode=ParseMode.HTML
            )
            return
        
        card_input = \' \'.join(context.args)
        card_data = self._parse_card_input(card_input)
        
        if not card_data:
            await update.message.reply_text(
                "❌ Invalid card format!\n\nFormat: /check 4532123456789012|12|2025|123",
                parse_mode=ParseMode.HTML
            )
            return
        
        # Deduct credits
        if not user.deduct_credits_for_check():
            await update.message.reply_text(
                "❌ Failed to deduct credits. Please try again.",
                parse_mode=ParseMode.HTML
            )
            return
        
        # Perform check
        start_time = time.time()
        
        # Get BIN info
        bin_info = await self._get_bin_info(card_data[\'number\'][:6])
        
        # Simulate check (replace with real API)
        gateway_data = {
            \'name\': \'sitebase\',
            \'amount\': \'1$\'
        }
        
        response_data = {
            \'status\': \'Charged 1$\'
        }
        
        end_time = time.time()
        duration = round(end_time - start_time, 2)
        
        # Create styled response
        styled_response = Config.format_styled_response(
            card_data={
                \'number\': f\"{card_data[\'number\'][:4]}****{card_data[\'number\'][-4:]}\",
                \'month\': card_data[\'month\'],
                \'year\': card_data[\'year\'],
                \'cvv\': card_data[\'cvv\'],
                \'brand\': bin_info.get(\'brand\', \'UNKNOWN\'),
                \'type\': bin_info.get(\'type\', \'UNKNOWN\'),
                \'level\': bin_info.get(\'prepaid\', \'UNKNOWN\'),
                \'bank\': bin_info.get(\'bank\', {}).get(\'name\', \'UNKNOWN\'),
                \'country\': bin_info.get(\'country\', {}).get(\'name\', \'UNKNOWN\'),
                \'flag\': bin_info.get(\'country\', {}).get(\'emoji\', \'🏳️\'),
                \'currency\': bin_info.get(\'country\', {}).get(\'currency\', \'USD\')
            },
            gateway_data=gateway_data,
            response_data=response_data,
            user_data={\'tier\': user.get_tier()},
            timing_data={\'duration\': duration}
        )
        
        # Log validation
        validation_log = ValidationLog(
            user=user,
            card_number=f\"{card_data[\'number\'][:4]}****{card_data[\'number\'][-4:]}\",
            gateway=gateway_data[\'name\'],
            result=\'approved\',
            response_time=duration,
            bin_info=bin_info
        )
        db.session.add(validation_log)
        db.session.commit()
        
        await update.message.reply_text(styled_response, parse_mode=ParseMode.HTML)
    
    async def mass_check_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        \"\"\"Handle /masschk command\"\"\"
        user = self._get_or_create_user(update.effective_user)
        
        can_access, error_msg = self._check_command_access(user, \'masschk\')
        if not can_access:
            await update.message.reply_text(error_msg, parse_mode=ParseMode.HTML)
            return
        
        await update.message.reply_text(
            "🔄 Mass checking feature coming soon! This will allow checking multiple cards at once.",
            parse_mode=ParseMode.HTML
        )
    
    async def deep_check_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        \"\"\"Handle /deepchk command\"\"\"
        user = self._get_or_create_user(update.effective_user)
        
        can_access, error_msg = self._check_command_access(user, \'deepchk\')
        if not can_access:
            await update.message.reply_text(error_msg, parse_mode=ParseMode.HTML)
            return
        
        await update.message.reply_text(
            "🔐 Deep checking feature coming soon! This will provide advanced validation.",
            parse_mode=ParseMode.HTML
        )
    
    async def generate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        \"\"\"Handle /generate command\"\"\"
        user = self._get_or_create_user(update.effective_user)
        
        can_access, error_msg = self._check_command_access(user, \'generate\')
        if not can_access:
            await update.message.reply_text(error_msg, parse_mode=ParseMode.HTML)
            return
        
        # Generate fake CC
        generated_cards = self.cc_generator.generate_cards(bin_number=None, count=10)
        
        response = "💳 <b>Generated Credit Cards</b>\n\n"
        for i, card in enumerate(generated_cards, 1):
            response += f\"{i}. <code>{card[\'number\']}|{card[\'month\']}|{card[\'year\']}|{card[\'cvv\']}</code>\n\"
        
        response += "\n⚠️ <i>These are test cards for educational purposes only!</i>"
        
        await update.message.reply_text(response, parse_mode=ParseMode.HTML)
    
    async def generate_info_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        \"\"\"Handle /generateinfo command\"\"\"
        user = self._get_or_create_user(update.effective_user)
        
        can_access, error_msg = self._check_command_access(user, \'generateinfo\')
        if not can_access:
            await update.message.reply_text(error_msg, parse_mode=ParseMode.HTML)
            return
        
        # Generate fake profile
        fake_profile = self.cc_generator.generate_fake_profile()
        
        response = f\"\"\"👤 <b>Generated Profile</b>

<b>Name:</b> {fake_profile[\'name\']}
<b>Email:</b> {fake_profile[\'email\']}
<b>Phone:</b> {fake_profile[\'phone\']}
<b>Address:</b> {fake_profile[\'address\']}
<b>City:</b> {fake_profile[\'city\']}
<b>State:</b> {fake_profile[\'state\']}
<b>ZIP:</b> {fake_profile[\'zip\']}
<b>Country:</b> {fake_profile[\'country\']}

⚠️ <i>This is fake information for testing purposes only!</i>\"\"\"
        
        await update.message.reply_text(response, parse_mode=ParseMode.HTML)
    
    async def bin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        \"\"\"Handle /bin command\"\"\"
        user = self._get_or_create_user(update.effective_user)
        
        can_access, error_msg = self._check_command_access(user, \'bin\')
        if not can_access:
            await update.message.reply_text(error_msg, parse_mode=ParseMode.HTML)
            return
        
        if not context.args:
            await update.message.reply_text(
                "❌ Please provide a BIN number!\n\nFormat: /bin 453212",
                parse_mode=ParseMode.HTML
            )
            return
        
        bin_number = context.args[0]
        if not bin_number.isdigit() or len(bin_number) < 6:
            await update.message.reply_text(
                "❌ Invalid BIN format! Please provide at least 6 digits.",
                parse_mode=ParseMode.HTML
            )
            return
        
        bin_info = await self._get_bin_info(bin_number)
        
        if not bin_info:
            await update.message.reply_text(
                "❌ BIN information not found!",
                parse_mode=ParseMode.HTML
            )
            return
        
        response = f\"\"\"🔍 <b>BIN Information</b>

<b>BIN:</b> <code>{bin_number}</code>
<b>Brand:</b> {bin_info.get(\'brand\', \'Unknown\')}
<b>Type:</b> {bin_info.get(\'type\', \'Unknown\')}
<b>Level:</b> {bin_info.get(\'prepaid\', \'Unknown\')}
<b>Bank:</b> {bin_info.get(\'bank\', {}).get(\'name\', \'Unknown\')}
<b>Country:</b> {bin_info.get(\'country\', {}).get(\'name\', \'Unknown\')} {bin_info.get(\'country\', {}).get(\'emoji\', \'\')}
<b>Currency:</b> {bin_info.get(\'country\', {}).get(\'currency\', \'Unknown\')}\"\"\"
        
        await update.message.reply_text(response, parse_mode=ParseMode.HTML)
    
    async def bin_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        \"\"\"Handle /binstats command\"\"\"
        user = self._get_or_create_user(update.effective_user)
        
        can_access, error_msg = self._check_command_access(user, \'binstats\')
        if not can_access:
            await update.message.reply_text(error_msg, parse_mode=ParseMode.HTML)
            return
        
        await update.message.reply_text(
            "📊 BIN statistics feature coming soon!",
            parse_mode=ParseMode.HTML
        )
    
    async def bin_weekly_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        \"\"\"Handle /binweekly command\"\"\"
        user = self._get_or_create_user(update.effective_user)
        
        can_access, error_msg = self._check_command_access(user, \'binweekly\')
        if not can_access:
            await update.message.reply_text(error_msg, parse_mode=ParseMode.HTML)
            return
        
        await update.message.reply_text(
            "📅 Weekly BIN drops feature coming soon!",
            parse_mode=ParseMode.HTML
        )
    
    async def vault_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        \"\"\"Handle /vault command\"\"\"
        user = self._get_or_create_user(update.effective_user)
        
        can_access, error_msg = self._check_command_access(user, \'vault\')
        if not can_access:
            await update.message.reply_text(error_msg, parse_mode=ParseMode.HTML)
            return
        
        await update.message.reply_text(
            "🏦 Premium vault feature coming soon!",
            parse_mode=ParseMode.HTML
        )
    
    async def autocharge_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        \"\"\"Handle /autocharge command\"\"\"
        user = self._get_or_create_user(update.effective_user)
        
        can_access, error_msg = self._check_command_access(user, \'autocharge\')
        if not can_access:
            await update.message.reply_text(error_msg, parse_mode=ParseMode.HTML)
            return
        
        await update.message.reply_text(
            "⚡ Auto charge feature coming soon!",
            parse_mode=ParseMode.HTML
        )
    
    async def log_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        \"\"\"Handle /log command\"\"\"
        user = self._get_or_create_user(update.effective_user)
        
        can_access, error_msg = self._check_command_access(user, \'log\')
        if not can_access:
            await update.message.reply_text(error_msg, parse_mode=ParseMode.HTML)
            return
        
        # Get recent validation logs
        recent_logs = ValidationLog.query.filter_by(user_id=user.id).order_by(ValidationLog.created_at.desc()).limit(10).all()
        
        if not recent_logs:
            await update.message.reply_text(
                "📝 No validation logs found!",
                parse_mode=ParseMode.HTML
            )
            return
        
        response = "📝 <b>Recent Validation Logs</b>\n\n"
        for log in recent_logs:
            response += f\"🔸 <code>{log.card_number}</code> - {log.result.upper()} ({log.response_time}s)\n\"
            response += f\"   Gateway: {log.gateway} | {log.created_at.strftime(\'%Y-%m-%d %H:%M\')}\n\n\"
        
        await update.message.reply_text(response, parse_mode=ParseMode.HTML)
    
    async def buy_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        \"\"\"Handle /buy command\"\"\"
        user = self._get_or_create_user(update.effective_user)
        
        can_access, error_msg = self._check_command_access(user, \'buy\')
        if not can_access:
            await update.message.reply_text(error_msg, parse_mode=ParseMode.HTML)
            return
        
        # Get current USD to KSH rate
        usd_to_ksh = await self.currency_service.get_usd_to_ksh_rate()
        
        monthly_ksh = round(Config.PRICING[\'monthly\'] * usd_to_ksh, 2)
        lifetime_ksh = round(Config.PRICING[\'lifetime\'] * usd_to_ksh, 2)
        
        payment_text = f\"\"\"{Config.MESSAGES[\'payment_instructions\']}

💎 <b>Current Pricing:</b>
• Monthly Premium: ${Config.PRICING[\'monthly\']} USD (KSH {monthly_ksh})
• Lifetime Access: ${Config.PRICING[\'lifetime\']} USD (KSH {lifetime_ksh})

💱 <b>Exchange Rate:</b> 1 USD = {usd_to_ksh} KSH\"\"\"
        
        await update.message.reply_text(payment_text, parse_mode=ParseMode.HTML)
    
    async def credits_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        \"\"\"Handle /credits command\"\"\"
        user = self._get_or_create_user(update.effective_user)
        
        can_access, error_msg = self._check_command_access(user, \'credits\')
        if not can_access:
            await update.message.reply_text(error_msg, parse_mode=ParseMode.HTML)
            return
        
        tier = user.get_tier()
        credits_per_check = Config.CREDITS_PER_CHECK[tier]
        remaining_checks = user.credits // credits_per_check if credits_per_check > 0 else "Unlimited"
        
        response = f\"\"\"💰 <b>Credit Balance</b>

👤 <b>User:</b> @{user.username or user.first_name}
🪙 <b>Current Credits:</b> {user.credits}
💳 <b>Cost per Check:</b> {credits_per_check} credits
🔢 <b>Remaining Checks:</b> {remaining_checks}
📊 <b>Tier:</b> {Config.TIER_NAMES[tier]}

💎 Use /buy to purchase more credits or upgrade your tier!\"\"\"
        
        await update.message.reply_text(response, parse_mode=ParseMode.HTML)
    
    async def me_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        \"\"\"Handle /me command\"\"\"
        user = self._get_or_create_user(update.effective_user)
        
        can_access, error_msg = self._check_command_access(user, \'me\')
        if not can_access:
            await update.message.reply_text(error_msg, parse_mode=ParseMode.HTML)
            return
        
        tier = user.get_tier()
        tier_emoji = "🆓" if tier == "free" else "👑" if tier == "monthly" else "⚡"
        
        response = f\"\"\"👤 <b>User Profile</b>

<b>Name:</b> {user.first_name} {user.last_name or \'\'}
<b>Username:</b> @{user.username or \'Not set\'}
<b>Telegram ID:</b> <code>{user.telegram_id}</code>

{tier_emoji} <b>Tier:</b> {Config.TIER_NAMES[tier]}
🪙 <b>Credits:</b> {user.credits}
📊 <b>Total Checks:</b> {user.total_checks}
📅 <b>Member Since:</b> {user.created_at.strftime(\'%Y-%m-%d\')}

👥 <b>Referrals:</b> {user.total_referrals} total, {user.paid_referrals} paid
🔗 <b>Referral Code:</b> <code>{user.referral_code}</code>\"\"\"
        
        await update.message.reply_text(response, parse_mode=ParseMode.HTML)
    
    async def referral_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        \"\"\"Handle /referral command\"\"\"
        user = self._get_or_create_user(update.effective_user)
        
        can_access, error_msg = self._check_command_access(user, \'referral\')
        if not can_access:
            await update.message.reply_text(error_msg, parse_mode=ParseMode.HTML)
            return
        
        referral_link = user.get_referral_link()
        
        response = f\"\"\"🔗 <b>Your Referral Link</b>

<b>Link:</b> <code>{referral_link}</code>

💰 <b>Earn {Config.REFERRAL_BONUS_CREDITS} credits for each paid referral!</b>

📊 <b>Your Stats:</b>
• Total Referrals: {user.total_referrals}
• Paid Referrals: {user.paid_referrals}
• Credits Earned: {user.paid_referrals * Config.REFERRAL_BONUS_CREDITS}

Share your link and earn credits when people upgrade to premium!\"\"\"
        
        await update.message.reply_text(response, parse_mode=ParseMode.HTML)
    
    async def my_referrals_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        \"\"\"Handle /myreferrals command\"\"\"
        user = self._get_or_create_user(update.effective_user)
        
        can_access, error_msg = self._check_command_access(user, \'myreferrals\')
        if not can_access:
            await update.message.reply_text(error_msg, parse_mode=ParseMode.HTML)
            return
        
        # Get referral details
        referrals = user.referrals.all()
        
        response = f\"\"\"👥 <b>My Referrals</b>

📊 <b>Summary:</b>
• Total Invited: {user.total_referrals}
• Paid Users: {user.paid_referrals}
• Credits Earned: {user.paid_referrals * Config.REFERRAL_BONUS_CREDITS}

\"\"\"
        
        if referrals:
            response += "<b>Recent Referrals:</b>\n"
            for ref in referrals[-10:]:  # Last 10 referrals
                status = "💎 Paid" if ref.subscription_type != SubscriptionType.FREE else "🆓 Free"
                response += f\"• @{ref.username or ref.first_name} - {status}\n\"
        else:
            response += "No referrals yet. Share your referral link to start earning!"
        
        await update.message.reply_text(response, parse_mode=ParseMode.HTML)
    
    async def disclaimer_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        \"\"\"Handle /disclaimer command\"\"\"
        user = self._get_or_create_user(update.effective_user)
        
        can_access, error_msg = self._check_command_access(user, \'disclaimer\')
        if not can_access:
            await update.message.reply_text(error_msg, parse_mode=ParseMode.HTML)
            return
        
        await update.message.reply_text(
            Config.MESSAGES[\'disclaimer\'],
            parse_mode=ParseMode.HTML
        )
    
    async def users_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        \"\"\"Handle /users command (Owner only)\
        user = self._get_or_create_user(update.effective_user)
        
        can_access, error_msg = self._check_command_access(user, \'users\')
        if not can_access:
            await update.message.reply_text(error_msg, parse_mode=ParseMode.HTML)
            return
        
        # Get user statistics
        total_users = User.query.count()
        registered_users = User.query.filter_by(is_registered=True).count()
        premium_users = User.query.filter(User.subscription_type != SubscriptionType.FREE).count()
        
        response = f\"\"\"👥 <b>User Statistics</b>

📊 <b>Overview:</b>
• Total Users: {total_users}
• Registered: {registered_users}
• Premium: {premium_users}
• Free: {registered_users - premium_users}

📈 <b>Recent Activity:</b>
• New users today: {User.query.filter(User.created_at >= datetime.utcnow().date()).count()}
• Active today: {User.query.filter(User.last_activity >= datetime.utcnow().date()).count()}\"\"\"
        
        await update.message.reply_text(response, parse_mode=ParseMode.HTML)
    
    async def broadcast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        \"\"\"Handle /broadcast command (Owner only)\
        user = self._get_or_create_user(update.effective_user)
        
        can_access, error_msg = self._check_command_access(user, \'broadcast\')
        if not can_access:
            await update.message.reply_text(error_msg, parse_mode=ParseMode.HTML)
            return
        
        if not context.args:
            await update.message.reply_text(
                "❌ Please provide a message to broadcast!\n\nFormat: /broadcast Your message here",
                parse_mode=ParseMode.HTML
            )
            return
        
        message = \' \'.join(context.args)
        
        # Get all registered users
        users = User.query.filter_by(is_registered=True).all()
        
        sent_count = 0
        failed_count = 0
        
        for target_user in users:
            try:
                await context.bot.send_message(
                    chat_id=target_user.telegram_id,
                    text=f\"📢 <b>Broadcast Message</b>\n\n{message}\",
                    parse_mode=ParseMode.HTML
                )
                sent_count += 1
            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to send broadcast to {target_user.telegram_id}: {e}")
        
        await update.message.reply_text(
            f"📢 Broadcast completed!\n\n✅ Sent: {sent_count}\n❌ Failed: {failed_count}",
            parse_mode=ParseMode.HTML
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        \"\"\"Handle inline keyboard button callbacks\"\"\"
        query = update.callback_query
        await query.answer()
        await query.edit_message_text("🔄 Feature coming soon!")
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        \"\"\"Handle payment screenshot uploads\"\"\"
        user = self._get_or_create_user(update.effective_user)
        
        if not self._check_registration(user):
            await update.message.reply_text(
                Config.MESSAGES[\'not_registered\'],
                parse_mode=ParseMode.HTML
            )
            return
        
        await update.message.reply_text(
            "📸 Payment screenshot received! Our team will review it shortly.",
            parse_mode=ParseMode.HTML
        )
        
        # Notify admin
        await self._notify_admin(
            \'payment\',
            \'Payment Screenshot Received\',
            f"User @{user.username or user.first_name} (ID: {user.telegram_id}) uploaded a payment screenshot."
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        \"\"\"Handle non-command messages\"\"\"
        await update.message.reply_text(
            Config.MESSAGES[\'unknown_command\'],
            parse_mode=ParseMode.HTML
        )
    
    def _parse_card_input(self, card_input):
        \"\"\"Parse card input string\"\"\"
        # Remove spaces and split by |
        parts = card_input.replace(\' \', \'\').split(\'|\')
        
        if len(parts) != 4:
            return None
        
        number, month, year, cvv = parts
        
        # Validate format
        if not (number.isdigit() and len(number) >= 13 and len(number) <= 19):
            return None
        if not (month.isdigit() and 1 <= int(month) <= 12):
            return None
        if not (year.isdigit() and len(year) == 4):
            return None
        if not (cvv.isdigit() and len(cvv) >= 3 and len(cvv) <= 4):
            return None
        
        return {
            \'number\': number,
            \'month\': month.zfill(2),
            \'year\': year,
            \'cvv\': cvv
        }
    
    async def _get_bin_info(self, bin_number):
        \"\"\"Get BIN information from cache or API\"\"\"
        with self.flask_app.app_context():
            # Check cache first
            cached_bin = BinCache.query.filter_by(bin_number=bin_number).first()
            if cached_bin and not cached_bin.is_expired():
                return cached_bin.bin_data
            
            # Fetch from API
            bin_info = await self.bin_checker.lookup_bin(bin_number)
            
            if bin_info:
                # Cache the result
                if cached_bin:
                    cached_bin.bin_data = bin_info
                    cached_bin.expires_at = datetime.utcnow() + timedelta(hours=24)
                else:
                    cached_bin = BinCache(
                        bin_number=bin_number,
                        bin_data=bin_info,
                        expires_at=datetime.utcnow() + timedelta(hours=24)
                    )
                    db.session.add(cached_bin)
                
                db.session.commit()
            
            return bin_info
    
    async def _handle_referral(self, user, referral_code):
        \"\"\"Handle referral code processing\"\"\"
        with self.flask_app.app_context():
            referrer = User.query.filter_by(referral_code=referral_code).first()
            if referrer and referrer.id != user.id:
                user.referred_by_id = referrer.id
                referrer.add_referral(user.id)
                db.session.commit()
    
    async def _notify_admin(self, notification_type, title, message):
        \"\"\"Send notification to admin\"\"\"
        try:
            await self.application.bot.send_message(
                chat_id=Config.ADMIN_ID,
                text=f\"🔔 <b>{title}</b>\n\n{message}\",
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Failed to notify admin: {e}")
    
    def run_polling(self):
        \"\"\"Run bot with polling\"\"\"
        logger.info(f"Starting {self.bot_name} with polling...")
        self.application.run_polling()
    
    def run_webhook(self, webhook_url, port=8443):
        \"\"\"Run bot with webhook\"\"\"
        logger.info(f"Starting {self.bot_name} with webhook...")
        self.application.run_webhook(
            listen="0.0.0.0",
            port=port,
            webhook_url=webhook_url,
            url_path=self.token
        )

