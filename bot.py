from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler

# Telegram Bot Token
BOT_TOKEN = "7739378344:AAHePCaShSC60pN1VwX9AY4TqD-xZMxQ1gY"

# Initialize Flask app
app = Flask(__name__)

# Initialize Telegram Application
application = Application.builder().token(BOT_TOKEN).build()

# Define a simple command handler for /start
async def start(update: Update, context):
    await update.message.reply_text("Hello! The bot is up and running.")

# Add the /start command to the bot's application
application.add_handler(CommandHandler("start", start))

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    try:
        # Parse incoming updates from Telegram
        update = Update.de_json(request.get_json(force=True), Bot(BOT_TOKEN))
        # Process the update
        application.update_queue.put_nowait(update)
    except Exception as e:
        print(f"Error handling update: {e}")
    return "OK", 200

@app.route("/ping", methods=["GET"])
def ping():
    return "Pong!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)