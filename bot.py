from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler
import logging
import os

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Telegram Bot Token
BOT_TOKEN = "7739378344:AAHePCaShSC60pN1VwX9AY4TqD-xZMxQ1gY"

# Flask App
app = Flask(__name__)

# Telegram Bot Application
application = Application.builder().token(BOT_TOKEN).build()

# Define the /start command handler
async def start(update: Update, context):
    logger.info(f"Received /start from {update.effective_user.username}")
    await update.message.reply_text("Hello! Your bot is working perfectly.")

# Add the command handler to the bot
application.add_handler(CommandHandler("start", start))

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    """Handle incoming webhook requests from Telegram."""
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        logger.info(f"Webhook received update: {update.to_dict()}")
        application.update_queue.put_nowait(update)  # Queue the update for processing
        return "OK", 200
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        return "Internal Server Error", 500

@app.route("/ping", methods=["GET"])
def ping():
    """Health check endpoint for uptime monitoring."""
    return "Pong!", 200

if __name__ == "__main__":
    # Flask app for local testing
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))