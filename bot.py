from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, ApplicationBuilder
import logging

# Define FastAPI app
app = FastAPI()

# Logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Telegram bot token and webhook URL
BOT_TOKEN = "7739378344:AAHRj6VmmmS19xCiIOFrdmyfcJ5_gRGXRHc"
WEBHOOK_URL = "https://bot-1-f2wh.onrender.com/webhook"

telegram_app = None  # Global bot application


@app.on_event("startup")
async def startup_event():
    global telegram_app
    try:
        logger.debug("Initializing Telegram bot application...")
        telegram_app = Application.builder().token(BOT_TOKEN).build()

        logger.debug("Deleting any previous webhook...")
        delete_response = await telegram_app.bot.delete_webhook()
        logger.info(f"Deleted webhook: {delete_response}")

        logger.debug(f"Setting new webhook: {WEBHOOK_URL}")
        webhook_response = await telegram_app.bot.set_webhook(WEBHOOK_URL)
        if webhook_response:
            logger.info(f"Webhook set successfully at {WEBHOOK_URL}")
        else:
            logger.error("Failed to set webhook.")
            raise Exception("Failed to set webhook")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise


@app.post("/webhook")
async def webhook(request: Request):
    global telegram_app
    if not telegram_app:
        logger.error("Telegram Application not initialized.")
        return {"status": "error", "message": "Telegram Application not initialized"}

    try:
        update = Update.de_json(await request.json(), telegram_app.bot)
        await telegram_app.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return {"status": "error", "message": str(e)}


@app.on_event("shutdown")
async def shutdown_event():
    global telegram_app
    if telegram_app:
        await telegram_app.shutdown()
        logger.info("Telegram application shut down.")
