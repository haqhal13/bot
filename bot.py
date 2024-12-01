from telegram.ext import Application, CommandHandler
from telegram import Update
from telegram.ext import ContextTypes
from fastapi import FastAPI, Request
import logging
import datetime

# Constants
BOT_TOKEN = "7739378344:AAHRj6VmmmS19xCiIOFrdmyfcJ5_gRGXRHc"
WEBHOOK_URL = "https://bot-1-f2wh.onrender.com/webhook"

# Logging Configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("bot")

# FastAPI App
app = FastAPI()

# Telegram Bot Application
telegram_app = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Responds to the /start command with a welcome message.
    """
    logger.debug(f"Received /start command from user {update.effective_user.id}.")
    user = update.effective_user
    if user:
        message = f"Hello, {user.first_name}! 👋 Welcome to the bot. How can I assist you today?"
    else:
        message = "Hello! 👋 Welcome to the bot. How can I assist you today?"
    await update.message.reply_text(message)
    logger.info(f"Sent welcome message to {user.first_name if user else 'unknown user'}.")


@app.on_event("startup")
async def startup_event():
    """
    Initializes the Telegram bot and sets the webhook.
    """
    global telegram_app

    if telegram_app is None:
        logger.info("Initializing Telegram bot application...")
        telegram_app = Application.builder().token(BOT_TOKEN).build()

        # Add command handlers
        telegram_app.add_handler(CommandHandler("start", start))

        # Initialize the bot
        await telegram_app.initialize()

        # Delete previous webhook
        logger.info("Deleting previous webhook (if any)...")
        deleted = await telegram_app.bot.delete_webhook()
        if deleted:
            logger.info("Previous webhook deleted successfully.")
        else:
            logger.warning("No previous webhook found or failed to delete.")

        # Set new webhook
        logger.info(f"Setting new webhook to {WEBHOOK_URL}...")
        webhook_set = await telegram_app.bot.set_webhook(WEBHOOK_URL)
        if not webhook_set:
            logger.error("Failed to set webhook. Exiting startup.")
            raise RuntimeError("Webhook setup failed!")

        # Start the bot
        await telegram_app.start()
        logger.info("Telegram bot application started successfully.")
    else:
        logger.warning("Telegram bot application is already initialized.")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Stops the Telegram bot application cleanly on shutdown.
    """
    global telegram_app

    if telegram_app:
        logger.info("Stopping Telegram bot application...")
        await telegram_app.stop()
        logger.info("Telegram bot application stopped successfully.")


@app.get("/")
async def root():
    """
    Root endpoint to confirm the bot's status.
    """
    return {"status": "ok", "message": "Bot is running!"}


@app.head("/")
async def root_head():
    """
    HEAD request handler for health checks.
    """
    return {"status": "ok"}


@app.post("/webhook")
async def webhook(request: Request):
    """
    Handles incoming Telegram updates via the webhook.
    """
    global telegram_app

    if not telegram_app:
        logger.error("Telegram application not initialized.")
        return {"status": "error", "message": "Application not initialized"}

    try:
        update_json = await request.json()
        logger.debug(f"Received update from webhook: {update_json}")
        update = Update.de_json(update_json, telegram_app.bot)  # Parse the update JSON
        await telegram_app.process_update(update)  # Process the update
        logger.info("Update processed successfully.")
        return {"status": "ok"}
    except Exception as e:
        logger.exception(f"Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}

# Add a global variable to track the last uptime check
# Add a global variable to track the last uptime check
import datetime

last_ping = None

@app.api_route("/uptime", methods=["GET", "HEAD"])
async def uptime_check():
    """
    Endpoint to respond to uptime monitoring pings.
    """
    global last_ping
    if last_ping is None:
        last_ping = datetime.datetime.utcnow()
    return {
        "status": "ok",
        "message": "Uptime check successful.",
        "last_ping": last_ping.isoformat()
    }
