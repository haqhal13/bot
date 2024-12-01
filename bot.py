from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import os
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables for deployment
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")  # Replace with your bot token
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://your-app-name.onrender.com")  # Replace with Render app URL

# Flask app setup
app = Flask(__name__)

# Telegram bot application
application = Application.builder().token(TOKEN).build()

# --- Core Telegram Bot Logic ---
# Start Command Handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    intro_text = (
        "👋 Welcome to the VIP Payment Bot!\n\n"
        "💎 Choose your subscription plan below to proceed:\n\n"
        "1 Month: £6.75\n"
        "Lifetime: £10"
    )
    keyboard = [
        [InlineKeyboardButton("PayPal", callback_data="paypal")],
        [InlineKeyboardButton("Apple Pay / Google Pay", callback_data="apple_google_pay")],
        [InlineKeyboardButton("Crypto (No KYC)", callback_data="crypto")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(intro_text, reply_markup=reply_markup)

# Payment Method Handlers
async def payment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    if query.data == "paypal":
        await query.edit_message_text(
            text="Send payment to:\n\n"
                 "💳 PayPal: onlyvipfan@outlook.com\n\n"
                 "💎 Pricing:\n"
                 "1 Month: £6.75\n"
                 "Lifetime: £10\n\n"
                 "✅ MUST BE FRIENDS AND FAMILY\n"
                 "❌ DO NOT LEAVE A NOTE\n\n"
                 "After payment, click 'I Paid' and provide your PayPal email.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Go Back", callback_data="go_back")]
            ])
        )
    elif query.data == "apple_google_pay":
        keyboard = [
            [
                InlineKeyboardButton(
                    "1 Month (£6.75)", web_app=WebAppInfo(url="https://buy.stripe.com/8wM0041QI3xK3ficMP")
                )
            ],
            [
                InlineKeyboardButton(
                    "Lifetime (£10)", web_app=WebAppInfo(url="https://buy.stripe.com/aEUeUYaneecoeY03cc")
                )
            ],
            [InlineKeyboardButton("Go Back", callback_data="go_back")],
        ]
        await query.edit_message_text(
            text="💳 Pay using Apple Pay / Google Pay via the links below:\n\n"
                 "💎 Pricing:\n"
                 "1 Month: £6.75\n"
                 "Lifetime: £10",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    elif query.data == "crypto":
        await query.edit_message_text(
            text="Send crypto to the following address:\n\n"
                 "💰 Bitcoin: 1ExampleBTCAddress\n"
                 "💰 Ethereum: 0xExampleETHAddress\n\n"
                 "💎 Pricing:\n"
                 "1 Month: $8\n"
                 "Lifetime: $14\n\n"
                 "After payment, click 'I Paid'.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Go Back", callback_data="go_back")]
            ])
        )

# Go Back Handler
async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start(update, context)

# --- Flask Routes ---
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    """Telegram Webhook Endpoint"""
    json_data = request.get_json()
    update = Update.de_json(json_data, application.bot)
    application.process_update(update)
    return "OK", 200

@app.route("/", methods=["GET"])
def uptime_ping():
    """UptimeRobot Ping Endpoint"""
    return "Bot is active!", 200

# --- Webhook Setup ---
def set_webhook():
    """Set Telegram Webhook"""
    webhook_url = f"{WEBHOOK_URL}/{TOKEN}"
    application.bot.set_webhook(url=webhook_url)
    logger.info(f"Webhook set to {webhook_url}")

# --- Main Entry Point ---
if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))