import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler

# Initialize Flask App
app = Flask(__name__)

# Telegram Bot Token (Replace with your actual bot token)
BOT_TOKEN = "7739378344:AAHePCaShSC60pN1VwX9AY4TqD-xZMxQ1gY"

# Initialize Telegram Application
application = Application.builder().token(BOT_TOKEN).build()

# Command handler for "/start"
async def start(update: Update, context):
    """Handler for the /start command."""
    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text="Hi!")

# Add the command handler to the Telegram application
application.add_handler(CommandHandler("start", start))

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    """Webhook route to receive updates from Telegram."""
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)
        application.update_queue.put_nowait(update)
        return "OK", 200
    except Exception as e:
        print(f"Error in webhook: {e}")
        return "Internal Server Error", 500

@app.route("/", methods=["GET"])
def index():
    """Base route."""
    return "Bot is live!", 200

if __name__ == "__main__":
    # Run the Flask app on the specified port
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
