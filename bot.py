from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Replace with your bot token and webhook URL
BOT_TOKEN = "7739378344:AAHePCaShSC60pN1VwX9AY4TqD-xZMxQ1gY"
WEBHOOK_URL = "https://bot-1-f2wh.onrender.com"

# Initialize Flask app and Telegram bot application
app = Flask(__name__)
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Define the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am your bot, ready to assist!")

# Set up Telegram command handlers
application.add_handler(CommandHandler("start", start))

# Define webhook route
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    """Handle incoming updates from Telegram."""
    data = request.get_json()
    if data:
        update = Update.de_json(data, application.bot)
        application.process_update(update)
    return "OK", 200

if __name__ == "__main__":
    # Set the webhook
    application.bot.set_webhook(f"{WEBHOOK_URL}/{BOT_TOKEN}")

    # Run the Flask server
    app.run(host="0.0.0.0", port=5000)