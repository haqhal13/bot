import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application

# Telegram Bot Token
BOT_TOKEN = '7739378344:AAHePCaShSC60pN1VwX9AY4TqD-xZMxQ1gY'

# Flask App
app = Flask(__name__)

# Telegram Bot Application
application = Application.builder().token(BOT_TOKEN).build()

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    """Handle incoming webhook requests."""
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.update_queue.put_nowait(update)  # Properly queues the update for processing
        return "OK", 200
    except Exception as e:
        print(f"Error handling webhook: {e}")
        return "Internal Server Error", 500

if __name__ == "__main__":
    # Get the PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    # Start Flask application on the specified port
    app.run(host="0.0.0.0", port=port)
    app.run(host="0.0.0.0", port=5000)