from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from fastapi import FastAPI, Request
import logging
import datetime

# Constants
BOT_TOKEN = "7739378344:AAHRj6VmmmS19xCiIOFrdmyfcJ5_gRGXRHc"
WEBHOOK_URL = "https://bot-1-f2wh.onrender.com/webhook"

# Logging Configuration
# Payment Information
PAYMENT_INFO = {
    "1_month": {"price": "£6.75", "crypto": "$8", "stripe_link": "https://buy.stripe.com/bIYbIMane1pCeY0eUZ"},
    "lifetime": {"price": "£10", "crypto": "$14", "stripe_link": "https://buy.stripe.com/aEUeUYaneecoeY03cc"},
    "paypal_email": "onlyfanvip@outlook.com",
    "crypto_addresses": {"btc": "your-bitcoin-wallet", "eth": "0x9ebeBd89395CaD9C29Ee0B5fC614E6f307d7Ca82"},
}

# Contact Support
SUPPORT_CONTACT = "@ZakiVip1"
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("bot")

# FastAPI App
app = FastAPI()

# Telegram Bot Application
telegram_app = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Responds to the /start command with subscription options.
    """
    keyboard = [
        [InlineKeyboardButton("PayPal", callback_data="paypal")],
        [InlineKeyboardButton("Apple Pay / Google Pay", callback_data="stripe")],
        [InlineKeyboardButton("Crypto (No KYC)", callback_data="crypto")],
        [InlineKeyboardButton("Contact Support", url=f"https://t.me/{SUPPORT_CONTACT[1:]}")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Welcome to the VIP Payment Bot!\n\n💎 Choose your subscription plan below to proceed:",
        reply_markup=reply_markup,
    )


async def handle_payment_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles user selection of payment methods.
    """
    query = update.callback_query
    await query.answer()

    if query.data == "paypal":
        message = (
            f"💳 *PayPal Instructions:*\n"
            f"Send £6.75 for 1 Month or £10 for Lifetime to: `{PAYMENT_INFO['paypal_email']}`\n\n"
            "✅ MUST BE FRIENDS AND FAMILY\n"
            "❌ DO NOT LEAVE A NOTE\n"
            "After payment, click 'I Paid' and send proof of payment."
        )
        keyboard = [
            [InlineKeyboardButton("I Paid", callback_data="paid")],
            [InlineKeyboardButton("Go Back", callback_data="back")],
            [InlineKeyboardButton("Contact Support", url=f"https://t.me/{SUPPORT_CONTACT[1:]}")],
        ]

    elif query.data == "stripe":
        message = (
            "💳 *Stripe Payment:*\n\n"
            f"1 Month: [Pay £6.75]({PAYMENT_INFO['1_month']['stripe_link']})\n"
            f"Lifetime: [Pay £10]({PAYMENT_INFO['lifetime']['stripe_link']})\n\n"
            "Click the appropriate link to pay securely."
        )
        keyboard = [
            [InlineKeyboardButton("Go Back", callback_data="back")],
            [InlineKeyboardButton("Contact Support", url=f"https://t.me/{SUPPORT_CONTACT[1:]}")],
        ]

    elif query.data == "crypto":
        message = (
            "💰 *Crypto Payment:*\n\n"
            f"1 Month: {PAYMENT_INFO['1_month']['crypto']} USD\n"
            f"Lifetime: {PAYMENT_INFO['lifetime']['crypto']} USD\n\n"
            f"BTC Address: `{PAYMENT_INFO['crypto_addresses']['btc']}`\n"
            f"ETH Address: `{PAYMENT_INFO['crypto_addresses']['eth']}`\n\n"
            "After payment, click 'I Paid' and send proof of payment."
        )
        keyboard = [
            [InlineKeyboardButton("I Paid", callback_data="paid")],
            [InlineKeyboardButton("Go Back", callback_data="back")],
            [InlineKeyboardButton("Contact Support", url=f"https://t.me/{SUPPORT_CONTACT[1:]}")],
        ]

    elif query.data == "paid":
        message = (
            "✅ Please send proof of payment (screenshot or transaction ID) to verify your subscription."
        )
        keyboard = [
            [InlineKeyboardButton("Go Back", callback_data="back")],
            [InlineKeyboardButton("Contact Support", url=f"https://t.me/{SUPPORT_CONTACT[1:]}")],
        ]

    elif query.data == "back":
        await start(update.callback_query, context)
        return

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=message, reply_markup=reply_markup, parse_mode="Markdown"
    )


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
        telegram_app.add_handler(CallbackQueryHandler(handle_payment_selection))  # Added handler

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
