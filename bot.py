import os
import logging
from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask App
app = Flask(__name__)

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN", "7739378344:AAHePCaShSC60pN1VwX9AY4TqD-xZMxQ1gY")

# Initialize Telegram Bot and Application
bot = Bot(BOT_TOKEN)
application = Application.builder().token(BOT_TOKEN).build()

# Command handler for "/start"
async def start(update: Update, context):
    try:
        logger.info(f"Processing /start for user {update.effective_user.username} (Chat ID: {update.effective_chat.id})")
        await update.message.reply_text("Hello! Your bot is running!")
        logger.info(f"Successfully replied to /start for Chat ID: {update.effective_chat.id}")
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
        if not data:
            logger.warning("No data received in webhook")
            return "Bad Request", 400
        
        logger.info("Received update: %s", data)
        update = Update.de_json(data, application.bot)
        application.update_queue.put_nowait(update)  # Queue the update for processing

        # Debugging: Simulate processing the update manually
        chat_id = 834523364  # Replace with your actual chat ID
        if "message" in data and data["message"].get("text") == "/start":
            bot.send_message(chat_id=chat_id, text="Debug: Your bot is processing the /start command!")
            logger.info(f"Debug message sent to Chat ID: {chat_id}")

        return "OK", 200
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return "Internal Server Error", 500

@app.route("/ping", methods=["GET"])
def ping():
    """Health check endpoint."""
    return "Pong!", 200

@app.errorhandler(404)
def not_found(error):
    """Handle unknown routes."""
    return jsonify({"error": "Route not found"}), 404

if __name__ == "__main__":
    import asyncio

    # Ensure PORT is properly set for deployment environments
    port = int(os.environ.get("PORT", 5000))
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(application.start())
        app.run(host="0.0.0.0", port=port)
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
        loop.run_until_complete(application.stop())