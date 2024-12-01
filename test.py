import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot")

# Initialize Flask App
app = Flask(__name__)

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN", "7739378344:AAHePCaShSC60pN1VwX9AY4TqD-xZMxQ1gY")

# Initialize Telegram Application
application = Application.builder().token(BOT_TOKEN).build()

# Command handler for "/start"
async def start(update: Update, context):
    """Handler for the /start command."""
    try:
        chat_id = update.effective_chat.id
        logger.info(f"Processing /start command for Chat ID: {chat_id}")
        await context.bot.send_message(chat_id=chat_id, text="Hello! Your simple bot is running!")
        logger.info(f"Replied to Chat ID: {chat_id}")
    except Exception as e:
        logger.error(f"Error in start handler: {e}")

# Add the command handler to the Telegram application
application.add_handler(CommandHandler("start", start))

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    """Webhook route to receive updates from Telegram."""
    try:
        data = request.get_json(force=True)
        logger.info(f"Received update: {data}")
        update = Update.de_json(data, application.bot)
        application.update_queue.put_nowait(update)
        return "OK", 200
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return "Internal Server Error", 500

if __name__ == "__main__":
    # Use port 5000 locally or set the environment variable PORT in deployment
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)