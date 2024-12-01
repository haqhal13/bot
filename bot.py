from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler
import logging

# Telegram Bot Token
TOKEN = "7739378344:AAHePCaShSC60pN1VwX9AY4TqD"

# Flask App
app = Flask(__name__)

# Telegram Bot Application
application = Application.builder().token(TOKEN).build()

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Command Handlers
async def start(update: Update, context):
    await update.message.reply_text("Hello! I'm your bot. How can I assist you?")

# Add handlers to the bot
application.add_handler(CommandHandler("start", start))

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    """Handle webhook updates from Telegram."""
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.update_queue.put_nowait(update)  # Properly queues the update for processing
        return "OK", 200
    except Exception as e:
        logger.error(f"Error handling update: {e}")
        return "Internal Server Error", 500

@app.route('/ping', methods=["GET", "HEAD"])
def ping():
    """Health check endpoint."""
    return "PONG", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)