from telegram.ext import Application, ApplicationBuilder
from fastapi import FastAPI, Request
import logging

# Bot Token and Webhook URL
BOT_TOKEN = "7739378344:AAHRj6VmmmS19xCiIOFrdmyfcJ5_gRGXRHc"
WEBHOOK_URL = "https://bot-1-f2wh.onrender.com/webhook"

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("bot")

# Create FastAPI instance
app = FastAPI()

# Global variable for the Telegram application
telegram_app = None


@app.on_event("startup")
async def startup_event():
    """
    FastAPI startup event: Initialize the Telegram bot application,
    set webhook, and manage its lifecycle.
    """
    global telegram_app

    if telegram_app is None:
        logger.debug("Initializing Telegram bot application...")
        telegram_app = Application.builder().token(BOT_TOKEN).build()

        # Initialize the bot
        await telegram_app.initialize()

        # Delete any previous webhook
        logger.debug("Deleting any previous webhook...")
        webhook_deleted = await telegram_app.bot.delete_webhook()
        if webhook_deleted:
            logger.info("Previous webhook deleted successfully.")
        else:
            logger.warning("No previous webhook found or failed to delete.")

        # Set the new webhook
        logger.debug(f"Setting new webhook: {WEBHOOK_URL}")
        webhook_set = await telegram_app.bot.set_webhook(WEBHOOK_URL)
        if webhook_set:
            logger.info(f"Webhook set successfully at {WEBHOOK_URL}")
        else:
            logger.error("Failed to set webhook.")
            raise RuntimeError("Failed to set webhook.")

        # Start the Telegram application
        await telegram_app.start()
        logger.info("Telegram application started successfully.")
    else:
        logger.warning("Telegram bot application is already initialized.")


@app.on_event("shutdown")
async def shutdown_event():
    """
    FastAPI shutdown event: Stop the Telegram bot application cleanly.
    """
    global telegram_app

    if telegram_app:
        logger.info("Stopping Telegram bot application...")
        await telegram_app.stop()
        logger.info("Telegram bot application stopped successfully.")


@app.get("/")
async def root():
    """
    Root route to confirm the bot's status.
    """
    return {"status": "ok", "message": "Bot is running!"}


@app.head("/")
async def root_head():
    """
    Handle HEAD requests for the root route.
    """
    return {"status": "ok"}


@app.post("/webhook")
async def webhook(request: Request):
    """
    Webhook route to process incoming Telegram updates.
    """
    global telegram_app

    if not telegram_app:
        logger.error("Telegram Application is not initialized.")
        return {"status": "error", "message": "Application not initialized"}

    try:
        update = await request.json()
        logger.debug(f"Received update: {update}")
        await telegram_app.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        logger.exception(f"Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}
