import logging
import os
import sys
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot_error.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Telegram Bot Token (replace with your bot token)
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Webhook URL (replace with your hosting URL)
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://your-app-hostname/webhook")

# Initialize FastAPI app
app = FastAPI()

# Verify dependencies are installed
try:
    import requests
except ImportError:
    logger.error("The 'requests' module is not installed. Install it using 'pip install requests'.")
    sys.exit("Dependency missing: 'requests' module.")

try:
    telegram_app = Application.builder().token(BOT_TOKEN).build()
    logger.info("Successfully connected to Telegram Bot API.")
except Exception as e:
    logger.error(f"Failed to connect to Telegram Bot API. Error: {e}")
    sys.exit("Exiting script due to Telegram connection failure.")

# Define /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await update.message.reply_text("Hello! I'm your bot. How can I help you?")
        logger.info(f"/start command handled for user: {update.effective_user.id}")
    except Exception as e:
        logger.error(f"Error handling /start command: {e}")

telegram_app.add_handler(CommandHandler("start", start))

@app.post("/webhook")
async def webhook(request: Request):
    try:
        update_data = await request.json()
        update = Update.de_json(update_data, telegram_app.bot)
        await telegram_app.process_update(update)
        logger.info(f"Processed update: {update_data}")
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/")
async def health_check():
    return {"status": "Bot is running"}

def set_webhook():
    try:
        delete_response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
        if delete_response.status_code == 200:
            logger.info("Existing webhook deleted successfully.")
        else:
            logger.error(f"Failed to delete webhook: {delete_response.text}")
            sys.exit("Exiting script due to webhook deletion failure.")

        set_response = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={WEBHOOK_URL}"
        )
        if set_response.status_code == 200:
            logger.info("Webhook set successfully.")
        else:
            logger.error(f"Failed to set webhook: {set_response.text}")
            sys.exit("Exiting script due to webhook setup failure.")
    except Exception as e:
        logger.error(f"Error during webhook setup: {e}")
        sys.exit("Exiting script due to webhook setup error.")

@app.on_event("startup")
async def startup_event():
    set_webhook()
    logger.info("Startup complete. Webhook configured.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
# Main entry point for local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
