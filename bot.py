from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from fastapi import FastAPI, Request
import logging

# Constants
BOT_TOKEN = "7739378344:AAHRj6VmmmS19xCiIOFrdmyfcJ5_gRGXRHc"
WEBHOOK_URL = "https://bot-1-f2wh.onrender.com/webhook"

# Payment Information
PAYMENT_INFO = {
    "1_month": {"price": "£6.75", "shopify_link": "https://5fbqad-qz.myshopify.com/checkouts/cn/Z2NwLWV1cm9wZS13ZXN0NDowMUpFS05IMkswU0hORTFaUzUzQTgzQlQ4Mw?skip_shop_pay=true"},
    "lifetime": {"price": "£10.00", "shopify_link": "https://5fbqad-qz.myshopify.com/checkouts/cn/Z2NwLWV1cm9wZS13ZXN0NDowMUpFS01ZUVg1S0ZQMFo0U0pCRUVRNzRRRA?skip_shop_pay=true"},
    "paypal_email": "onlyvipfan@outlook.com",
    "crypto_addresses": {"btc": "your-bitcoin-wallet", "eth": "0x9ebeBd89395CaD9C29Ee0B5fC614E6f307d7Ca82"},
}

# Contact Support
SUPPORT_CONTACT = "@ZakiVip1"

# Logging Configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("bot")

# FastAPI App
app = FastAPI()

# Telegram Bot Application
telegram_app = None


@app.on_event("startup")
async def startup_event():
    global telegram_app
    if telegram_app is None:
        telegram_app = Application.builder().token(BOT_TOKEN).build()
        telegram_app.add_handler(CommandHandler("start", start))
        telegram_app.add_handler(CallbackQueryHandler(handle_payment_selection, pattern="select_.*"))
        telegram_app.add_handler(CallbackQueryHandler(handle_payment_method, pattern="paypal_.*|shopify_.*|crypto_.*|back|paid|support"))
        await telegram_app.initialize()
        logger.info("Telegram bot application initialized.")
        await telegram_app.bot.delete_webhook()
        await telegram_app.bot.set_webhook(WEBHOOK_URL)
        await telegram_app.start()


@app.post("/webhook")
async def webhook(request: Request):
    global telegram_app
    if not telegram_app:
        logger.error("Telegram application not initialized.")
        return {"status": "error", "message": "Application not initialized"}
    try:
        update_json = await request.json()
        update = Update.de_json(update_json, telegram_app.bot)
        await telegram_app.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        logger.exception(f"Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/")
async def root():
    return {"status": "ok", "message": "Bot is running!"}


@app.head("/uptime")
async def uptime():
    return {"status": "ok"}


# The rest of the handlers and logic remain unchanged from your script
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("1 Month (£6.75)", callback_data="select_1_month")],
        [InlineKeyboardButton("Lifetime (£10.00)", callback_data="select_lifetime")],
        [InlineKeyboardButton("Support", callback_data="support")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Welcome to the VIP Bot!\n\n"
        "💎 Choose your subscription plan below to proceed:",
        reply_markup=reply_markup,
    )


async def handle_payment_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "select_1_month":
        message = (
            "💳 *1 Month Subscription (£6.75):*\n\n"
            "Select your preferred payment method:\n\n"
            "💡 Shopify: Instant access sent to your email.\n"
            "💡 PayPal & Crypto: Sent to you within 30 mins between 8 AM - 12 AM BST."
        )
        keyboard = [
            [InlineKeyboardButton("PayPal", callback_data="paypal_1_month")],
            [InlineKeyboardButton("Shopify (Secure Payment)", callback_data="shopify_1_month")],
            [InlineKeyboardButton("Crypto", callback_data="crypto_1_month")],
            [InlineKeyboardButton("Support", callback_data="support")],
            [InlineKeyboardButton("Go Back", callback_data="back")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=message, reply_markup=reply_markup, parse_mode="Markdown")

    elif query.data == "select_lifetime":
        message = (
            "💳 *Lifetime Subscription (£10.00):*\n\n"
            "Select your preferred payment method:\n\n"
            "💡 Shopify: Instant access sent to your email.\n"
            "💡 PayPal & Crypto: Sent to you within 30 mins between 8 AM - 12 AM BST."
        )
        keyboard = [
            [InlineKeyboardButton("PayPal", callback_data="paypal_lifetime")],
            [InlineKeyboardButton("Apple Pay/Google Pay", callback_data="shopify_lifetime")],
            [InlineKeyboardButton("Crypto", callback_data="crypto_lifetime")],
            [InlineKeyboardButton("Support", callback_data="support")],
            [InlineKeyboardButton("Go Back", callback_data="back")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=message, reply_markup=reply_markup, parse_mode="Markdown")


async def handle_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("paypal"):
        message = (
            "💰 *PayPal Payment:*\n\n"
            "💰£10.00 GBP for LIFETIME\n"
            "💰£6.75 GBP for 1 MONTH\n\n"
            f"➡️ PayPal: {PAYMENT_INFO['paypal_email']}\n"
            "✅ MUST BE FRIENDS AND FAMILY\n"
            "✅ IF YOU DON'T HAVE FAMILY AND FRIENDS USE CARD/CRYPTO\n"
            "❌ DON'T LEAVE A NOTE\n\n"
            "➡️ CLICK 'I PAID'\n"
            f"✅ SEND PAYMENT SCREENSHOT TO {SUPPORT_CONTACT} AND PROVIDE YOUR FULL PAYPAL NAME"
        )
        keyboard = [
            [InlineKeyboardButton("I Paid", callback_data="paid")],
            [InlineKeyboardButton("Go Back", callback_data="back")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=message, reply_markup=reply_markup, parse_mode="Markdown")

    elif query.data.startswith("shopify"):
        if query.data == "shopify_1_month":
            shopify_link = PAYMENT_INFO["1_month"]["shopify_link"]
            amount = PAYMENT_INFO["1_month"]["price"]
        else:
            shopify_link = PAYMENT_INFO["lifetime"]["shopify_link"]
            amount = PAYMENT_INFO["lifetime"]["price"]

        # Inject CSS to hide the Shopify shop name
        custom_script_link = f"https://yourserver.com/custom-css-loader?url={shopify_link}"

        message = (
            f"🛒 *Shopify Payment ({amount}):*\n\n"
            "Pay securely on our Shopify store.\n\n"
            "After payment, check your email for the VIP link.\n"
            f"If you face any issues, contact {SUPPORT_CONTACT}."
        )
        keyboard = [[InlineKeyboardButton(f"Pay Now ({amount})", web_app=WebAppInfo(url=custom_script_link))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=message, reply_markup=reply_markup, parse_mode="Markdown")

    elif query.data.startswith("crypto"):
        if query.data == "crypto_1_month":
            amount = "$8"
        else:
            amount = "$14"

        message = (
            f"💰 *Crypto Payment ({amount}):*\n\n"
            f"BTC: `{PAYMENT_INFO['crypto_addresses']['btc']}`\n"
            f"ETH: `{PAYMENT_INFO['crypto_addresses']['eth']}`\n\n"
            f"After payment, click 'I Paid' and send a screenshot or transaction ID to {SUPPORT_CONTACT}."
        )
        keyboard = [
            [InlineKeyboardButton("I Paid", callback_data="paid")],
            [InlineKeyboardButton("Go Back", callback_data="back")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=message, reply_markup=reply_markup, parse_mode="Markdown")


@app.post("/webhook")
async def webhook(request: Request):
    global telegram_app
    if not telegram_app:
        logger.error("Telegram application not initialized.")
        return {"status": "error", "message": "Application not initialized"}
    try:
        update_json = await request.json()  # Corrected line
        update = Update.de_json(update_json, telegram_app.bot)
        await telegram_app.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        logger.exception(f"Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}
