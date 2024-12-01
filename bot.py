from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os

# Telegram Bot Token
TOKEN = os.getenv('7739378344:AAHePCaShSC60pN1VwX9AY4TqD-xZMxQ1gY', '7739378344:AAHePCaShSC60pN1VwX9AY4TqD-xZMxQ1gY')  # Replace with your bot token

# Flask app setup
app = Flask(__name__)

# Telegram bot application
application = Application.builder().token(TOKEN).build()

# Telegram Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Welcome! The bot is working!")

# Add Command Handlers
application.add_handler(CommandHandler("start", start))

@app.route("/", methods=["GET"])
def uptime_home():
    """Root route to confirm the bot is live."""
    return "Bot is active at root!", 200

@app.route("/ping", methods=["GET", "HEAD"])
def uptime_ping():
    """UptimeRobot Ping Endpoint"""
    return "Bot is active at ping!", 200

@app.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook():
    """Telegram Webhook Endpoint"""
    json_data = request.get_json()
    update = Update.de_json(json_data, application.bot)
    application.process_update(update)
    return "OK", 200

if __name__ == "__main__":
    # Set Webhook
    application.bot.set_webhook(url=f"https://your-app-name.onrender.com/{TOKEN}")
    app.run(host="0.0.0.0", port=5000)