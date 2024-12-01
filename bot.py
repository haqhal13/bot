from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import os
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot Token and Webhook URL
TOKEN = os.getenv("7739378344:AAHePCaShSC60pN1VwX9AY4TqD-xZMxQ1gY", "7739378344:AAHePCaShSC60pN1VwX9AY4TqD-xZMxQ1gY")  # Replace with your bot token
WEBHOOK_URL = os.getenv("https://bot-1-f2wh.onrender.com", "https://your-app-name.onrender.com")  # Replace with Render app URL

# Flask app for webhook handling
app = Flask(__name__)

# Initialize Telegram Bot Application
application = Application.builder().token(TOKEN).build()

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

# Payment Handlers
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
                 "After payment, click 'I Paid'.",
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
            text="💳 Pay using Apple Pay / Google Pay:\n\n"
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
                 "Lifetime: $14",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Go Back", callback_data="go_back")]
            ])
        )

# Go Back Handler
async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start(update, context)

# Webhook Route
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_data = request.get_json()
    update = Update.de_json(json_data, application.bot)
    application.process_update(update)
    return "OK", 200

# UptimeRobot Route
@app.route("/", methods=["GET"])
def uptime_ping():
    return "Bot is active!", 200

# Set Webhook
def set_webhook():
    webhook_url = f"{WEBHOOK_URL}/{TOKEN}"
    application.bot.set_webhook(url=webhook_url)
    logger.info(f"Webhook set to {webhook_url}")

# Main Function
if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))