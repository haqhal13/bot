import logging
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
import os

# Constants
BOT_TOKEN = '7739378344:AAHePCaShSC60pN1VwX9AY4TqD-xZMxQ1gY'
WEBHOOK_URL = 'https://bot-1-f2wh.onrender.com'

# Flask App Setup
app = Flask(__name__)

# Telegram Application Setup
application = Application.builder().token(BOT_TOKEN).build()

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Handlers
async def start(update: Update, context):
    """Handles the /start command."""
    keyboard = [
        [InlineKeyboardButton("1 MONTH (£6.75)", callback_data="1_month")],
        [InlineKeyboardButton("LIFETIME (£10)", callback_data="lifetime")],
        [InlineKeyboardButton("Support", callback_data="support")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        text=(
            "👋 Welcome to the BADDIES FACTORY VIP Bot!\n\n"
            "💎 Access exclusive VIP content instantly with a growing collection every day. "
            "Choose your subscription plan below or contact support for assistance."
        ),
        reply_markup=reply_markup,
    )

async def button_callback(update: Update, context):
    """Handles button clicks from the InlineKeyboardMarkup."""
    query = update.callback_query
    await query.answer()
    if query.data == "1_month":
        await query.edit_message_text(
            text=(
                "**Apple Pay / Google Pay Payment:**\n\n"
                "Complete your payment using the links below:\n\n"
                "• **1 MONTH (£6.75):** [Click Here](https://buy.stripe.com/eVa9AE7b23xK036eUW)\n"
                "• **LIFETIME (£10):** [Click Here](https://buy.stripe.com/eVa9AE7b23xK036eUW)\n\n"
                "After payment, your VIP link will be emailed immediately!"
            ),
            parse_mode="Markdown",
        )
    elif query.data == "lifetime":
        await query.edit_message_text(
            text=(
                "**Apple Pay / Google Pay Payment:**\n\n"
                "Complete your payment using the links below:\n\n"
                "• **1 MONTH (£6.75):** [Click Here](https://buy.stripe.com/eVa9AE7b23xK036eUW)\n"
                "• **LIFETIME (£10):** [Click Here](https://buy.stripe.com/eVa9AE7b23xK036eUW)\n\n"
                "After payment, your VIP link will be emailed immediately!"
            ),
            parse_mode="Markdown",
        )
    elif query.data == "support":
        await query.edit_message_text(
            text=(
                "📩 For assistance, please contact our support team at: "
                "[Support Email](mailto:support@example.com)."
            ),
            parse_mode="Markdown",
        )

# Add Handlers to Telegram Application
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_callback))

# Webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    """Handles incoming updates from Telegram."""
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "OK", 200

# Root Endpoint
@app.route('/')
def index():
    """Root endpoint for testing."""
    return "Bot is running!", 200

if __name__ == '__main__':
    # Set webhook
    application.run_polling()  # Fallback for local testing
    application.bot.set_webhook(f"{WEBHOOK_URL}/webhook")
    # Run Flask App
    port = int(os.environ.get("PORT", 8443))
    app.run(host="0.0.0.0", port=port)