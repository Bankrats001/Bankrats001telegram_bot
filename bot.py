# bot.py

import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from config import TOKEN, ADMIN_USER_ID

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Dictionary to track user states
user_states = {}

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    keyboard = [
        [InlineKeyboardButton("💳 Make Payment", callback_data='make_payment')],
        [InlineKeyboardButton("📜 Bot Disclaimer", callback_data='disclaimer')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"👋 *Welcome to Band$ Premium Bot*\n\n"
        f"_I’m here to assist you with premium services!_\n\n"
        f"*Select an option below 👇:*",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

# Callback for button presses
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'make_payment':
        await query.edit_message_text(
            text="💳 *Payment Instructions:*\n\n"
                 "_Please send your M-Pesa payment screenshot here as an image file or document._\n\n"
                 "Once submitted, I will review it manually and unlock your premium access! 🚀",
            parse_mode='Markdown'
        )
        user_states[query.from_user.id] = 'awaiting_payment'

    elif query.data == 'disclaimer':
        await query.edit_message_text(
            text="⚠️ *Disclaimer*\n\n"
                 "_This bot and its services are provided for educational purposes only._\n\n"
                 "*I do not affiliate, endorse, or take responsibility for how users utilize this bot.*\n\n"
                 "By continuing to use this bot, you agree to this disclaimer.",
            parse_mode='Markdown'
        )

# Handler for images (manual confirm flow)
async def image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if user_states.get(user_id) == 'awaiting_payment':
        # Forward image to admin for manual review
        if update.message.photo:
            file_id = update.message.photo[-1].file_id
            caption = f"🛂 *Payment screenshot received from user:* `{user_id}`\n\n" \
                      "⚡ *Action required:*\n\n" \
                      "✅ /confirm_{user_id}  OR  ❌ /reject_{user_id}"
            await context.bot.send_photo(chat_id=ADMIN_USER_ID, photo=file_id, caption=caption, parse_mode='Markdown')

        elif update.message.document:
            file_id = update.message.document.file_id
            caption = f"🛂 *Payment document received from user:* `{user_id}`\n\n" \
                      "⚡ *Action required:*\n\n" \
                      "✅ /confirm_{user_id}  OR  ❌ /reject_{user_id}"
            await context.bot.send_document(chat_id=ADMIN_USER_ID, document=file_id, caption=caption, parse_mode='Markdown')

        await update.message.reply_text(
            "📥 *Thank you for your submission!*\n\n"
            "_Your payment is under review by admin. You’ll receive an update soon._",
            parse_mode='Markdown'
        )

# Manual confirm command
async def confirm_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.effective_user.id) != str(ADMIN_USER_ID):
        return

    try:
        target_user_id = int(update.message.text.split('_')[1])
        await context.bot.send_message(
            chat_id=target_user_id,
            text="🎉 *Payment confirmed!*\n\n"
                 "_Your premium access is now unlocked._\n\n"
                 "*Enjoy and keep winning!* 🚀",
            parse_mode='Markdown'
        )
        await update.message.reply_text(f"✅ User `{target_user_id}` has been confirmed.", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error confirming user: {e}")
        await update.message.reply_text("❌ Failed to confirm user. Check command format.", parse_mode='Markdown')

# Manual reject command
async def reject_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.effective_user.id) != str(ADMIN_USER_ID):
        return

    try:
        target_user_id = int(update.message.text.split('_')[1])
        await context.bot.send_message(
            chat_id=target_user_id,
            text="❌ *Payment rejected!*\n\n"
                 "_Please ensure you submit a valid payment screenshot._",
            parse_mode='Markdown'
        )
        await update.message.reply_text(f"❌ User `{target_user_id}` has been rejected.", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error rejecting user: {e}")
        await update.message.reply_text("❌ Failed to reject user. Check command format.", parse_mode='Markdown')

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.warning(f"Update {update} caused error {context.error}")

# Main function to run the bot
if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.PHOTO | filters.Document.IMAGE, image_handler))
    application.add_handler(MessageHandler(filters.Regex(r'^/confirm_\d+$'), confirm_command))
    application.add_handler(MessageHandler(filters.Regex(r'^/reject_\d+$'), reject_command))
    application.add_error_handler(error_handler)

    # Run the bot
    application.run_polling()
