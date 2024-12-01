import logging
import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from httpx import AsyncClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Bot Token and Webhook URL
BOT_TOKEN = '7739378344:AAHRj6VmmmS19xCiIOFrdmyfcJ5_gRGXRHc'
WEBHOOK_URL = f'https://bot-1-f2wh.onrender.com/webhook'

# Initialize FastAPI app
app = FastAPI()

# Telegram bot application
telegram_app = Application.builder().token(BOT_TOKEN).build()

# Define /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await update.message.reply_text("Hello! I'm your bot. How can I assist you today?")
        logger.info(f"Handled /start command from user {update.effective_user.id}")
    except Exception as e:
        logger.error(f"Error in /start command: {e}")

# Add /start command handler to Telegram app
telegram_app.add_handler(CommandHandler("start", start))

# Webhook route
@app.post("/webhook")
async def webhook(request: Request):
    try:
        update_data = await request.json()
        update = Update.de_json(update_data, telegram_app.bot)
        await telegram_app.process_update(update)
        logger.info(f"Received update: {update_data}")
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return {"status": "error", "message": str(e)}

# Health check route
@app.get("/")
async def health_check():
    return {"status": "Bot is running"}

# Function to set the webhook automatically
async def set_webhook():
    async with AsyncClient() as client:
        try:
            # Delete any existing webhook
            delete_response = await client.get(
                f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
            )
            logger.info(f"Delete webhook response: {delete_response.json()}")

            # Set the new webhook
            set_response = await client.get(
                f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={WEBHOOK_URL}"
            )
            logger.info(f"Set webhook response: {set_response.json()}")
        except Exception as e:
            logger.error(f"Error setting webhook: {e}")

# Run the webhook setup during app startup
@app.on_event("startup")
async def startup_event():
    await set_webhook()

# Main entry point for local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
    except Exception as e:
        logger.error(f"Failed to start the FastAPI server: {e}")
        traceback.print_exc()
