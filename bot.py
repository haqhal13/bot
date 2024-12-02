from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from fastapi import FastAPI, Request
import logging

# Constants
BOT_TOKEN = "7739378344:AAHRj6VmmmS19xCiIOFrdmyfcJ5_gRGXRHc"
WEBHOOK_URL = "https://bot-1-f2wh.onrender.com/webhook"

# Payment Information
PAYMENT_INFO = {
    "1_month": {"price": "£6.75", "stripe_link": "https://buy.stripe.com/bIYbIMane1pCeY0eUZ"},
    "lifetime": {"price": "£10.00", "stripe_link": "https://buy.stripe.com/aEUeUYaneecoeY03cc"},
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
            "💡 Apple Pay / Google Pay: Instant access sent to your email.\n"
            "💡 PayPal & Crypto: Sent to you within 30 mins between 8 AM - 12 AM BST."
        )
        keyboard = [
            [InlineKeyboardButton("PayPal", callback_data="paypal_1_month")],
            [InlineKeyboardButton("Apple Pay / Google Pay (Media App)", callback_data="stripe_1_month")],
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
            "💡 Apple Pay / Google Pay: Instant access sent to your email.\n"
            "💡 PayPal & Crypto: Sent to you within 30 mins between 8 AM - 12 AM BST."
        )
        keyboard = [
            [InlineKeyboardButton("PayPal", callback_data="paypal_lifetime")],
            [InlineKeyboardButton("Apple Pay / Google Pay (Media App)", callback_data="stripe_lifetime")],
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

    elif query.data.startswith("stripe"):
        if query.data == "stripe_1_month":
            stripe_link = PAYMENT_INFO["1_month"]["stripe_link"]
            amount = PAYMENT_INFO["1_month"]["price"]
        else:
            stripe_link = PAYMENT_INFO["lifetime"]["stripe_link"]
            amount = PAYMENT_INFO["lifetime"]["price"]

        message = (
            f"💳 *Apple Pay / Google Pay Payment ({amount}):*\n\n"
            "Pay securely using Apple Pay or Google Pay within Telegram.\n\n"
            "After payment, check your email for the VIP link.\n"
            f"If the link isn't there, message {SUPPORT_CONTACT}."
        )
        keyboard = [[InlineKeyboardButton(f"Pay Now ({amount})", web_app=WebAppInfo(url=stripe_link))]]
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

    elif query.data == "support":
        message = (
            "💬 *Contact Customer Support:*\n\n"
            "If you need help, message us at:\n\n"
            f"{SUPPORT_CONTACT}\n\n"
            "⏰ Available: 8 AM - 12 AM BST."
        )
        keyboard = [[InlineKeyboardButton("Go Back", callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=message, reply_markup=reply_markup, parse_mode="Markdown")

    elif query.data == "back":
        await start(update.callback_query, context)

    elif query.data == "paid":
        message = f"✅ Provide Screenshot/Other Details Mentioned in Your Payment Instructions Message to {SUPPORT_CONTACT}."
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Go Back", callback_data="back")]])
        await query.edit_message_text(text=message, reply_markup=reply_markup, parse_mode="Markdown")


@app.post("/webhook")
async def webhook(request: Request):
    global telegram_app
    if not telegram_app:
        logger.error("Telegram application not initialized.")
        return {"status": "error", "message": "Application not initialized"}
    try:
        update_json = await request.json()
        update = Update.de_json(update_json, telegram_app.bot)
