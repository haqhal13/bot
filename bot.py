import os
from flask import Flask, request, jsonify
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
        
        # Send debug message to the user
        await context.bot.send_message(chat_id=chat_id, text="Debug: Your bot is processing the /start command!")
        logger.info(f"Debug message sent to Chat ID: {chat_id}")
        
        # Send actual response
        await context.bot.send_message(chat_id=chat_id, text="Hello! Your bot is running!")
        logger.info(f"Message sent to Chat ID: {chat_id}")
    except Exception as e:
        logger.error(f"Error in start handler: {e}")

# Add the command handler to the Telegram application
application.add_handler(CommandHandler("start", start))

@app.route("/", methods=["GET"])
def index():
    """Base route for debugging."""
    return jsonify({"message": "Bot is live!"}), 200

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    """Webhook route to receive updates from Telegram."""
    try:
        data = request.get_json(force=True)
        logger.info(f"Received update: {data}")  # Debug log for incoming updates
        update = Update.de_json(data, application.bot)
        application.update_queue.put_nowait(update)  # Queue the update for processing
        return "OK", 200
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return "Internal Server Error", 500

@app.route("/ping", methods=["GET"])
def ping():
    """Health check endpoint."""
    return "Pong!", 200

if __name__ == "__main__":
    # Ensure PORT is properly set for deployment environments
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)