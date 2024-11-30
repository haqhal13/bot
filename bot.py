from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import os  # Ensure the os module is imported

# Example token and webhook URL
BOT_TOKEN = '7739378344:AAHePCaShSC60pN1VwX9AY4TqD-xZMxQ1gY'
WEBHOOK_URL = 'https://bot-1-f2wh.onrender.com'

if not BOT_TOKEN or not WEBHOOK_URL:
    raise ValueError("BOT_TOKEN and WEBHOOK_URL must be set.")

# Flask app for webhook handling
app = Flask(__name__)

# Telegram bot application
application = Application.builder().token(BOT_TOKEN).build()

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    intro_text = (
        "👋 Welcome to the VIP Bot!💎\n\n"
        "Access exclusive content instantly. Choose your subscription plan or contact support."
    )
    keyboard = [
        [InlineKeyboardButton("1 MONTH (£6.75)", callback_data="1_month"),
         InlineKeyboardButton("3 MONTHS (£19.75)", callback_data="3_months")],
        [InlineKeyboardButton("Support", url="https://t.me/YourSupportHandle")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(intro_text, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Type /start to begin using the bot.")

# Callback query handler
async def handle_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    subscription_message = f"You selected: {query.data.replace('_', ' ').title()}"
    await query.edit_message_text(subscription_message)

# Webhook route for Telegram updates
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.process_update(update)
    return "OK", 200

# Health check route for UptimeRobot
@app.route("/health", methods=["GET"])
def health_check():
    return "OK", 200

# Initialize handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CallbackQueryHandler(handle_subscription))

async def setup_webhook():
    """Set the Telegram bot webhook."""
    await application.bot.set_webhook(f"{WEBHOOK_URL}/{BOT_TOKEN}")

if __name__ == "__main__":
    import asyncio  # Import asyncio for async operations
    # Set up webhook asynchronously
    asyncio.run(setup_webhook())

    # Start Flask app
    port = int(os.environ.get("PORT", 5000))  # Ensure PORT is fetched from environment variables
    app.run(host="0.0.0.0", port=port)