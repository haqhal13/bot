from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from fastapi import FastAPI, Request
import logging
import datetime

# Constants
BOT_TOKEN = "7739378344:AAHRj6VmmmS19xCiIOFrdmyfcJ5_gRGXRHc"
WEBHOOK_URL = "https://bot-1-f2wh.onrender.com/webhook"

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

# Logging Configuration
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
        [InlineKeyboardButton("1 Month (£6.75)", callback_data="select_1_month")],
        [InlineKeyboardButton("Lifetime (£10)", callback_data="select_lifetime")],
        [InlineKeyboardButton("Support", callback_data="support")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Welcome to the VIP Bot!\n\n"
        "💎 Choose your subscription plan below to proceed:",
        reply_markup=reply_markup,
    )


async def handle_payment_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles user selection of subscription plans and payment methods.
    """
    query = update.callback_query
    await query.answer()

    if query.data == "select_1_month":
        message = "💳 *1 Month Subscription (£6.75)*:\n\nSelect your preferred payment method:"
        keyboard = [
            [InlineKeyboardButton("PayPal", callback_data="paypal_1_month")],
            [InlineKeyboardButton("Apple Pay / Google Pay", callback_data="stripe_1_month")],
            [InlineKeyboardButton("Crypto", callback_data="crypto_1_month")],
            [InlineKeyboardButton("Go Back", callback_data="back")],
        ]

    elif query.data == "select_lifetime":
        message = "💳 *Lifetime Subscription (£10)*:\n\nSelect your preferred payment method:"
        keyboard = [
            [InlineKeyboardButton("PayPal", callback_data="paypal_lifetime")],
            [InlineKeyboardButton("Apple Pay / Google Pay", callback_data="stripe_lifetime")],
            [InlineKeyboardButton("Crypto", callback_data="crypto_lifetime")],
            [InlineKeyboardButton("Go Back", callback_data="back")],
        ]

    elif query.data == "support":
        message = (
            "💬 *Contact Customer Support:*\n\n"
            "If you're having issues with payment, have questions, or haven’t received your VIP link yet, "
            "we're here to help!\n\n"
            f"Reach out to us at {SUPPORT_CONTACT}."
        )
        keyboard = [
            [InlineKeyboardButton("Go Back", callback_data="back")],
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=message, reply_markup=reply_markup, parse_mode="Markdown"
    )


async def handle_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Provides detailed instructions for each payment method.
    """
    query = update.callback_query
    await query.answer()

    if query.data == "paypal_1_month":
        message = (
            "💳 *PayPal Payment (1 Month - £6.75)*:\n\n"
            f"Send £6.75 to `{PAYMENT_INFO['paypal_email']}`.\n\n"
            "⚠️ *Important:* Use 'Friends & Family' and *DO NOT* include any notes.\n"
            "After payment, click 'I Paid' to confirm."
        )

    elif query.data == "stripe_1_month":
        message = (
            "💳 *Apple Pay / Google Pay (1 Month - £6.75)*:\n\n"
            "Pay securely using Apple Pay or Google Pay within Telegram.\n\n"
            "After payment, click 'I Paid' to confirm."
        )
        keyboard = [
            [InlineKeyboardButton("Pay Now", web_app=WebAppInfo(url=PAYMENT_INFO['1_month']['stripe_link']))],
        ]

    elif query.data == "crypto_1_month":
        message = (
            "💳 *Crypto Payment (1 Month - $8)*:\n\n"
            f"BTC: `{PAYMENT_INFO['crypto_addresses']['btc']}`\n"
            f"ETH: `{PAYMENT_INFO['crypto_addresses']['eth']}`\n\n"
            "After payment, click 'I Paid' to confirm."
        )

    elif query.data == "paypal_lifetime":
        message = (
            "💳 *PayPal Payment (Lifetime - £10)*:\n\n"
            f"Send £10 to `{PAYMENT_INFO['paypal_email']}`.\n\n"
            "⚠️ *Important:* Use 'Friends & Family' and *DO NOT* include any notes.\n"
            "After payment, click 'I Paid' to confirm."
        )

    elif query.data == "stripe_lifetime":
        message = (
            "💳 *Apple Pay / Google Pay (Lifetime - £10)*:\n\n"
            "Pay securely using Apple Pay or Google Pay within Telegram.\n\n"
            "After payment, click 'I Paid' to confirm."
        )
        keyboard = [
            [InlineKeyboardButton("Pay Now", web_app=WebAppInfo(url=PAYMENT_INFO['lifetime']['stripe_link']))],
        ]

    elif query.data == "crypto_lifetime":
        message = (
            "💳 *Crypto Payment (Lifetime - $14)*:\n\n"
            f"BTC: `{PAYMENT_INFO['crypto_addresses']['btc']}`\n"
            f"ETH: `{PAYMENT_INFO['crypto_addresses']['eth']}`\n\n"
            "After payment, click 'I Paid' to confirm."
        )

    elif query.data == "back":
        await start(update.callback_query, context)
        return

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("I Paid", callback_data="paid")], [InlineKeyboardButton("Go Back", callback_data="back")]])
    await query.edit_message_text(
        text=message, reply_markup=reply_markup, parse_mode="Markdown"
    )


@app.get("/")
async def root():
    """
    Root endpoint to confirm the bot's status.
    """
    return {"status": "ok", "message": "Bot is running!"}


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


@app.on_event("startup")
async def startup_event():
    """
    Initializes the Telegram bot and sets the webhook.
    """
    global telegram_app
    if telegram_app is None:
        logger.info("Initializing Telegram bot application...")
        telegram_app = Application.builder().token(BOT_TOKEN).build()
        telegram_app.add_handler(CommandHandler("start", start))
        telegram_app.add_handler(CallbackQueryHandler(handle_payment_selection, pattern="select_.*"))
        telegram_app.add_handler(CallbackQueryHandler(handle_payment_method, pattern="paypal_.*|stripe_.*|crypto_.*|back|paid"))
        await telegram_app.initialize()
        await telegram_app.bot.delete_webhook()
        await telegram_app.bot.set_webhook(WEBHOOK_URL)
        await telegram_app.start()
