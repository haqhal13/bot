from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler

# Flask app initialization
app = Flask(__name__)

# Telegram bot token
BOT_TOKEN = '7739378344:AAHePCaShSC60pN1VwX9AY4TqD-xZMxQ1gY'

# Initialize Telegram Application
application = Application.builder().token(BOT_TOKEN).build()

# Define the /start command handler
async def start(update: Update, context):
    """Handles the /start command."""
    chat_id = update.effective_chat.id
    print(f"Received /start command from Chat ID: {chat_id}")
    await update.message.reply_text("Hi!")

# Add the /start command handler to the Telegram application
application.add_handler(CommandHandler("start", start))

# Define the webhook route
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    """Processes incoming Telegram updates."""
    try:
        data = request.get_json(force=True)
        print(f"Received update: {data}")  # Debug log
        update = Update.de_json(data, application.bot)
        application.update_queue.put_nowait(update)  # Pass update to the handler
        return "OK", 200
    except Exception as e:
        print(f"Error in webhook: {e}")
        return "Internal Server Error", 500

# Define the root route for basic health checks
@app.route("/", methods=["GET"])
def index():
    return "Bot is live!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
