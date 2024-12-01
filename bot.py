import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler

# Initialize Flask App
app = Flask(__name__)

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN", "7739378344:AAHePCaShSC60pN1VwX9AY4TqD-xZMxQ1gY")

# Initialize Telegram Application
application = Application.builder().token(BOT_TOKEN).build()

# Command handler for "/start"
async def start(update: Update, context):
    await update.message.reply_text("Hello! Your bot is running!")

# Add the command handler to the Telegram application
application.add_handler(CommandHandler("start", start))

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    """Webhook route to receive updates from Telegram."""
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.update_queue.put_nowait(update)  # Queue the update for processing
        return "OK", 200
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return "Internal Server Error", 500

@app.route("/ping", methods=["GET"])
def ping():
    """Health check endpoint."""
    return "Pong!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)