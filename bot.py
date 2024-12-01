from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler

# Telegram Bot Token
BOT_TOKEN = "7739378344:AAHePCaShSC60pN1VwX9AY4TqD-xZMxQ1gY"

# Flask App
app = Flask(__name__)

# Telegram Bot Application
application = Application.builder().token(BOT_TOKEN).build()

# /start command handler
async def start(update: Update, context):
    await update.message.reply_text("Hello! Your bot is working.")

# Add the /start handler
application.add_handler(CommandHandler("start", start))

# Webhook route
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    try:
        # Parse the update from Telegram
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.update_queue.put_nowait(update)  # Queue the update for processing
        app.logger.info("Received update: %s", update)
        return "OK", 200
    except Exception as e:
        app.logger.error("Error processing update: %s", str(e))
        return "Internal Server Error", 500

# Status route for debugging
@app.route("/status", methods=["GET"])
def status():
    return "Bot is live and responding!", 200

# Ping route for UptimeRobot
@app.route("/ping", methods=["HEAD", "GET"])
def ping():
    return "Pong!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)