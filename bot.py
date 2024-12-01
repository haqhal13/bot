from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import logging
import asyncio

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot")

# Telegram Bot Token
BOT_TOKEN = '7739378344:AAHePCaShSC60pN1VwX9AY4TqD-xZMxQ1gY'

# Flask app setup
app = Flask(__name__)

# Telegram bot application
application = Application.builder().token(BOT_TOKEN).build()

# Telegram Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for the /start command."""
    logger.info(f"Processing /start command from user: {update.effective_user.id}")
    await update.message.reply_text("Welcome! The bot is working!")

# Add Command Handlers
application.add_handler(CommandHandler("start", start))

@app.route("/", methods=["GET"])
def uptime_home():
    """Root route to confirm the bot is live."""
    return "Bot is active at root!", 200

@app.route("/ping", methods=["GET", "HEAD"])
def uptime_ping():
    """UptimeRobot Ping Endpoint"""
    return "Bot is active at ping!", 200

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def telegram_webhook():
    """Telegram Webhook Endpoint"""
    json_data = request.get_json()
    logger.info(f"Webhook received update: {json_data}")  # Log the raw JSON
    try:
        update = Update.de_json(json_data, application.bot)
        # Await the coroutine to process the update
        await application.process_update(update)
    except Exception as e:
        logger.error(f"Error processing update: {e}")  # Log any errors
    return "OK", 200

if __name__ == "__main__":
    # Set Webhook
    webhook_url = f"https://bot-1-f2wh.onrender.com/{BOT_TOKEN}"
    asyncio.run(application.bot.set_webhook(url=webhook_url))
    logger.info(f"Webhook set to {webhook_url}")
    app.run(host="0.0.0.0", port=5000)