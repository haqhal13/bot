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
ADMIN_CONTACT = "@telehaq"
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
        [InlineKeyboardButton("1 MONTH (£6.75)", callback_data="1_month")],
        [InlineKeyboardButton("LIFETIME (£10)", callback_data="lifetime")],
        [InlineKeyboardButton("Support", callback_data="support")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Welcome to the VIP Bot!\n\n"
        "💎 Get access to 1000’s of creators every month!\n\n"
        "⚡️ INSTANT ACCESS TO VIP LINK SENT TO EMAIL!\n\n"
        "⭐️ If we don’t have the model you're looking for, we’ll add them within 24–72 hours!\n\n"
        "Select your subscription plan below or contact support for assistance if you have questions about anything! 🔍 👀",
        reply_markup=reply_markup,
    )


async def handle_payment_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles user selection of payment methods.
    """
    query = update.callback_query
    await query.answer()

    if query.data == "1_month":
        message = (
            "💳 *1 Month Subscription (£6.75):*\n\n"
            "Choose your preferred payment method below:\n"
            "⏱ *Delivery:* Apple Pay/Google Pay instant, PayPal and Crypto: ~30 mins\n\n"
            "💰£6.75 - 1 month\n\n"
            f"🔗 [Apple Pay / Google Pay](miniapp://stripe-1-month)\n"
            f"📧 *PayPal:* Send £6.75 to `{PAYMENT_INFO['paypal_email']}` (Friends & Family, No Notes)\n"
            f"💰 *Crypto (BTC/ETH):*\nBTC: `{PAYMENT_INFO['crypto_addresses']['btc']}`\nETH: `{PAYMENT_INFO['crypto_addresses']['eth']}`\n\n"
            "✅ *Update I Paid Description:*\n"
            "Make sure to screenshot once you've paid. Provide @ZakiVip1 with a screenshot + name paid under."
        )
        keyboard = [
            [InlineKeyboardButton("I Paid", callback_data="paid")],
            [InlineKeyboardButton("Go Back", callback_data="back")],
        ]

    elif query.data == "lifetime":
        message = (
            "💳 *Lifetime Subscription (£10):*\n\n"
            "Choose your preferred payment method below:\n"
            "⏱ *Delivery:* Apple Pay/Google Pay instant, PayPal and Crypto: ~30 mins\n\n"
            "💰£10 - Lifetime\n\n"
            f"🔗 [Apple Pay / Google Pay](miniapp://stripe-lifetime)\n"
            f"📧 *PayPal:* Send £10 to `{PAYMENT_INFO['paypal_email']}` (Friends & Family, No Notes)\n"
            f"💰 *Crypto (BTC/ETH):*\nBTC: `{PAYMENT_INFO['crypto_addresses']['btc']}`\nETH: `{PAYMENT_INFO['crypto_addresses']['eth']}`\n\n"
            "✅ *Update I Paid Description:*\n"
            "Make sure to screenshot once you've paid. Provide @ZakiVip1 with a screenshot + name paid under."
        )
        keyboard = [
            [InlineKeyboardButton("I Paid", callback_data="paid")],
            [InlineKeyboardButton("Go Back", callback_data="back")],
        ]

    elif query.data == "support":
        message = (
            "💬 *Contact Customer Support:*\n\n"
            "If you're having issues with payment, have questions, or haven’t received your VIP link yet, "
            "we're here to help!\n\n"
            "⏰ We operate between 7 AM and 12 AM BST to ensure prompt assistance.\n\n"
            f"Reach out to us at {SUPPORT_CONTACT}."
        )
        keyboard = [
            [InlineKeyboardButton("Go Back", callback_data="back")],
        ]

    elif query.data == "paid":
        message = (
            "✅ Please send proof of payment (screenshot or transaction ID) to verify your subscription. "
            "We will process your verification as soon as possible!"
        )
        # Notify admin
        user = query.from_user
        await context.bot.send_message(
            chat_id=ADMIN_CONTACT,
            text=(
                f"💸 Payment Alert!\n\n"
                f"👤 *User:* @{user.username}\n"
                f"🕒 *Time:* {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} BST\n"
                f"🔔 *Subscription:* {query.data}"
            ),
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
        return {"status": "error", "message": str
