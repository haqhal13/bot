from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
)
from flask import Flask, request
import logging

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Replace with your bot token and webhook URL
BOT_TOKEN = "YOUR_BOT_TOKEN"
WEBHOOK_URL = "https://bot-1-f2wh.onrender.com/webhook"
ADMIN_CHAT_ID = "YOUR_ADMIN_CHAT_ID"

# Create the Flask app for webhook handling
flask_app = Flask(__name__)

# Telegram application
app = Application.builder().token(BOT_TOKEN).build()

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the /start command is received."""
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

# Fallback handler
async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unrecognized commands or messages."""
    await update.message.reply_text("I'm sorry, I didn't understand that command.")

# Callback query handler for subscriptions
async def subscription_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    context.user_data["subscription"] = query.data.replace('_', ' ').upper()

    text = (
        f"📄 You selected the **{context.user_data['subscription']}** plan.\n\n"
        "Choose your preferred payment method below:\n"
        "💳 **Apple Pay / Google Pay:** Instant VIP access (emailed immediately).\n"
        "⚡ **Crypto:** VIP link will be sent within 30 minutes during BST hours.\n"
        "📧 **PayPal:** VIP link will be sent within 30 minutes during BST hours."
    )
    keyboard = [
        [InlineKeyboardButton("Apple Pay / Google Pay", callback_data="apple_google_pay"),
         InlineKeyboardButton("Crypto", callback_data="crypto")],
        [InlineKeyboardButton("PayPal", callback_data="paypal"),
         InlineKeyboardButton("Go Back", callback_data="go_back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)

# Webhook handler
@flask_app.route('/webhook', methods=['POST'])
def webhook_handler():
    """Handle incoming updates via webhook."""
    update = Update.de_json(request.get_json(force=True), app.bot)
    logger.info(f"Webhook triggered with update: {update}")
    app.update_queue.put(update)
    return "OK"

# Error handler
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

# Main function
def main():
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(subscription_handler, pattern="^(1_month|lifetime)$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback))

    # Add error handler
    app.add_error_handler(error_handler)

    # Set webhook
    app.bot.set_webhook(url=WEBHOOK_URL)

    # Run Flask app for webhook handling
    flask_app.run(host="0.0.0.0", port=8443)

if __name__ == "__main__":
    main()