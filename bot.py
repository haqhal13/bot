import os
import logging
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables for bot token and webhook URL
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not BOT_TOKEN or not WEBHOOK_URL:
    raise ValueError("Please set TELEGRAM_BOT_TOKEN and WEBHOOK_URL environment variables.")

# Flask app for webhook handling
flask_app = Flask(__name__)

# Telegram application
telegram_app = Application.builder().token(BOT_TOKEN).build()

# Handlers for the Telegram bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message with subscription options."""
    intro_text = (
        "👋 Welcome to the BADDIES FACTORY VIP Bot!\n\n"
        "💎 Access exclusive VIP content instantly with a growing collection every day.\n"
        "Choose your subscription plan below or contact support for assistance."
    )
    keyboard = [
        [InlineKeyboardButton("1 MONTH (£6.75)", callback_data="1_month"),
         InlineKeyboardButton("LIFETIME (£10)", callback_data="lifetime")],
        [InlineKeyboardButton("Support", callback_data="support")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(intro_text, reply_markup=reply_markup)

async def subscription_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle subscription button presses."""
    query = update.callback_query
    await query.answer()

    if query.data == "1_month":
        response_text = (
            "**Apple Pay / Google Pay Payment:**\n\n"
            "Complete your payment using the links below:\n"
            "- **1 MONTH (£6.75):** [Click Here](https://example.com/1month)\n"
            "- **LIFETIME (£10):** [Click Here](https://example.com/lifetime)\n\n"
            "After payment, your VIP link will be emailed immediately!"
        )
        await query.edit_message_text(response_text, parse_mode="Markdown")
    elif query.data == "support":
        await query.edit_message_text("Contact support at: support@example.com")

async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unrecognized commands or messages."""
    await update.message.reply_text("I'm sorry, I didn't understand that command.")

# Add handlers to the Telegram bot
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(subscription_handler))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback))

# Flask route for webhook
@flask_app.route('/webhook', methods=['POST'])
def webhook_handler():
    """Handle incoming updates from Telegram via webhook."""
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    telegram_app.update_queue.put_nowait(update)
    return "OK", 200

# Error handling
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

telegram_app.add_error_handler(error_handler)

# Main entry point
if __name__ == "__main__":
    # Set webhook for the Telegram bot
    telegram_app.bot.set_webhook(f"{WEBHOOK_URL}/webhook")

    # Start Flask app
    port = int(os.getenv("PORT", 5000))  # Default port for Flask
    flask_app.run(host="0.0.0.0", port=port)