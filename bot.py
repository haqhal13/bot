import logging
import sys
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from telegram import Update
from telegram.ext import Application, ApplicationBuilder

# Replace with your bot token and webhook URL
BOT_TOKEN = "7739378344:AAHRj6VmmmS19xCiIOFrdmyfcJ5_gRGXRHc"
WEBHOOK_URL = "https://bot-1-f2wh.onrender.com/webhook"

app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("bot")

# Telegram bot application instance
telegram_app = None  # Global application


@app.on_event("startup")
async def startup_event():
    global telegram_app  # Declare global bot application
    try:
        logger.debug("Initializing Telegram bot application...")
        # Build and initialize the bot application
        telegram_app = Application.builder().token(BOT_TOKEN).build()

        # Delete any existing webhook
        logger.debug("Deleting any previous webhook...")
        delete_response = await telegram_app.bot.delete_webhook()
        logger.info(f"Deleted webhook: {delete_response}")

        # Set up a new webhook
        logger.debug(f"Setting new webhook: {WEBHOOK_URL}")
        webhook_response = await telegram_app.bot.set_webhook(WEBHOOK_URL)
        if webhook_response:
            logger.info(f"Webhook set successfully at {WEBHOOK_URL}")
        else:
            logger.error("Failed to set webhook.")
            sys.exit(1)  # Stop deployment if webhook setup fails
    except Exception as e:
        logger.error(f"Error during bot startup: {e}")
        sys.exit(1)  # Exit if bot initialization fails


@app.on_event("shutdown")
async def shutdown_event():
    global telegram_app
    if telegram_app:
        await telegram_app.shutdown()
        logger.info("Bot application shut down.")


@app.get("/")
async def root():
    return JSONResponse(content={"status": "ok", "message": "Telegram bot is running!"})


@app.post("/webhook")
async def webhook(request: Request):
    global telegram_app
    if not telegram_app:
        logger.error("Telegram Application not initialized.")
        return {"status": "error", "message": "Telegram Application not initialized"}

    try:
        # Parse the incoming Telegram update
        update = Update.de_json(await request.json(), telegram_app.bot)
        # Process the update
        await telegram_app.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return {"status": "error", "message": str(e)}
