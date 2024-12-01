from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from fastapi import FastAPI, Request
import logging
import datetime

# Constants
BOT_TOKEN = "7739378344:AAHRj6VmmmS19xCiIOFrdmyfcJ5_gRGXRHc"
WEBHOOK_URL = "https://bot-1-f2wh.onrender.com/webhook"
ADMIN_TELEGRAM_HANDLE = "@telehaq"

# Payment Information
PAYMENT_INFO = {
    "1_month": {"price": "£6.75", "crypto": "$8"},
    "lifetime": {"price": "£10", "crypto": "$14"},
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


async def notify_admin(context, user, subscription):
    """
    Notifies the admin when a user pays for a subscription.
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = (
        f"💰 *New Payment Received!*\n\n"
        f"📅 *Time Paid:* {now}\n"
        f"👤 *User:* @{user.username if user.username else 'Unknown'}\n"
        f"💎 *Subscription:* {subscription}\n"
    )
    await context.bot.send_message(chat_id=ADMIN_TELEGRAM_HANDLE, text=message, parse_mode="Markdown")


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

    # Payment method selection
    if query.data in ["1_month", "lifetime"]:
        subscription = "1 Month (£6.75)" if query.data == "1_month" else "Lifetime (£10)"
        message = (
            f"💰 *{subscription} Subscription*\n\n"
            "Choose your preferred payment method below:\n\n"
            "📱 *Apple Pay / Google Pay (Instant Delivery)*\n"
            "💳 *PayPal (30 mins delivery)*\n"
            "💰 *Crypto (ETH/BTC) (30 mins delivery)*\n"
        )
        keyboard = [
            [InlineKeyboardButton("Apple Pay / Google Pay", callback_data=f"stripe_{query.data}")],
            [InlineKeyboardButton("PayPal", callback_data=f"paypal_{query.data}")],
            [InlineKeyboardButton("Crypto", callback_data=f"crypto_{query.data}")],
            [InlineKeyboardButton("Go Back", callback_data="back")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=message, reply_markup=reply_markup, parse_mode="Markdown")

    # Stripe (Apple Pay / Google Pay)
    elif query.data.startswith("stripe_"):
        subscription = "1 Month (£6.75)" if "1_month" in query.data else "Lifetime (£10)"
        message = (
            f"💳 *Apple Pay / Google Pay:*\n\n"
            f"To pay for your {subscription}, click the button below:\n\n"
            "Delivery: *Instant via email*\n\n"
            "Make sure to screenshot the confirmation and send it to @ZAKIVIP1 for verification."
        )
        keyboard = [
            [InlineKeyboardButton("Pay Now", url="https://buy.stripe.com")],  # Replace with your Stripe mini-app link
            [InlineKeyboardButton("Go Back", callback_data="back")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=message, reply_markup=reply_markup, parse_mode="Markdown")

    # Other handlers...

    elif query.data == "back":
        await start(update.callback_query, context)


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
        telegram_app.add_handler(CallbackQueryHandler(handle_payment_selection))

        # Initialize the bot
        await telegram_app.initialize()

        # Delete previous webhook
        logger.info("Deleting previous webhook (if any)...")  # Fixed string literal issue
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

# Other event handlers and API routes...
