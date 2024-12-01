import logging
import os
import sys
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)

# Environment variables for sensitive data
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://your-deployment-url.com/webhook")

# Dependency check for requests
try:
    import requests
except ImportError:
    logger.error("Missing dependency: 'requests' module not installed. Please add it to requirements.txt.")
    sys.exit(1)

# FastAPI instance
app = FastAPI()

# Telegram Bot setup
try:
    telegram_app = Application.builder().token(BOT_TOKEN).build()
    logger.info("Successfully connected to Telegram API.")
except Exception as e:
    logger.error(f"Failed to connect to Telegram API. Error: {e}")
    sys.exit(1)

# Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello! I am your bot!")

telegram_app.add_handler(CommandHandler("start", start))

# Webhook route
@app.post("/webhook")
async def webhook(request: Request):
    try:
        update = Update.de_json(await request.json(), telegram_app.bot)
        await telegram_app.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return {"status": "error", "message": str(e)}

# Webhook setup
@app.on_event("startup")
async def on_startup():
    try:
        delete_response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
        if delete_response.status_code != 200:
            logger.error(f"Failed to delete webhook: {delete_response.text}")
            sys.exit(1)

        set_response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={WEBHOOK_URL}")
        if set_response.status_code == 200:
            logger.info("Webhook set successfully.")
        else:
            logger.error(f"Failed to set webhook: {set_response.text}")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error setting up webhook: {e}")
        sys.exit(1)

# Health check endpoint
@app.get("/")
async def health_check():
    return {"status": "Bot is running"}

# Main function
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
