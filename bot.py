import logging
import os
import sys
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)

# Bot and webhook configuration
BOT_TOKEN = "7739378344:AAHRj6VmmmS19xCiIOFrdmyfcJ5_gRGXRHc"
WEBHOOK_URL = "https://bot-1-f2wh.onrender.com/webhook"

# Check if required dependencies are installed
try:
    import requests
except ImportError:
    logger.error("Dependency 'requests' is missing. Please install it using 'pip install requests'.")
    sys.exit(1)

# FastAPI application instance
app = FastAPI()

# Initialize Telegram bot application
try:
    telegram_app = Application.builder().token(BOT_TOKEN).build()
    logger.info("Successfully connected to Telegram API.")
except Exception as e:
    logger.error(f"Failed to connect to Telegram API. Error: {e}")
    sys.exit(1)

# Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello! I am your bot, ready to assist!")

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

# Webhook setup during startup
@app.on_event("startup")
async def on_startup():
    try:
        # Delete any existing webhook
        delete_response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
        if delete_response.status_code == 200:
            logger.info("Deleted previous webhook successfully.")
        else:
            logger.warning(f"Failed to delete webhook: {delete_response.text}")

        # Set up a new webhook
        set_response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={WEBHOOK_URL}")
        if set_response.status_code == 200:
            logger.info("Webhook set successfully.")
        else:
            logger.error(f"Failed to set webhook: {set_response.text}")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error during webhook setup: {e}")
        sys.exit(1)

# Health check endpoint
@app.get("/")
async def health_check():
    return {"status": "Bot is running"}

# Main entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
