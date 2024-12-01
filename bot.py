import logging
from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import os

# Constants
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")  # Replace with your bot token
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://your-app-name.onrender.com")  # Replace with your Render app's URL

# Flask App Setup
app = Flask(__name__)

# Telegram Application Setup
application = Application.builder().token(BOT_TOKEN).build()

# Logging for debugging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,  # Set to DEBUG for detailed logs
)
logger = logging.getLogger(__name__)

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
                    "1 Month (£6.75)",
                    web_app=WebAppInfo(url="https://buy.stripe.com/8wM0041QI3xK3ficMP"),
                )
            ],
            [
                InlineKeyboardButton(
                    "Lifetime (£10)",
                    web_app=WebAppInfo(url="https://buy.stripe.com/aEUeUYaneecoeY03cc"),
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

    elif query.data == "i_paid":
        await query.edit_message_text(
            text="Thank you! Please send a screenshot of your payment or provide the transaction ID for verification.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Go Back", callback_data="go_back")]
            ])
        )

# Go Back Handler
async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
    query = update.callback_query
    await query.edit_message_text(intro_text, reply_markup=reply_markup)

# Debug Command Handler
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Pong!")

application.add_handler(CommandHandler("ping", ping))

# Webhook Route
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    """Handle incoming webhook requests from Telegram."""
    json_data = request.get_json()
    update = Update.de_json(json_data, application.bot)
    application.process_update(update)
    return "OK", 200

if __name__ == "__main__":
    # Set Webhook for Telegram
    application.bot.set_webhook(f"{WEBHOOK_URL}/{BOT_TOKEN}")

    # Start Flask server
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)