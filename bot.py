from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import logging

# Constants
BOT_TOKEN = "7739378344:AAHRj6VmmmS19xCiIOFrdmyfcJ5_gRGXRHc"
WEBHOOK_URL = "https://bot-1-f2wh.onrender.com/webhook"

# Payment Information
PAYMENT_INFO = {
    "stripe": "https://your-stripe-payment-link.com",
    "crypto": {"eth": "0x9ebeBd89395CaD9C29Ee0B5fC614E6f307d7Ca82"},
    "paypal": "onlyvipfan@outlook.com",
}

SUPPORT_CONTACT = "@ZakiVip1"

# Logging Configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("bot")

# FastAPI App
app = FastAPI()
telegram_app = None


@app.on_event("startup")
async def startup_event():
    global telegram_app
    telegram_app = Application.builder().token(BOT_TOKEN).build()
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CallbackQueryHandler(handle_subscription, pattern="select_.*"))
    telegram_app.add_handler(CallbackQueryHandler(handle_payment, pattern="payment_.*"))
    telegram_app.add_handler(CallbackQueryHandler(confirm_payment, pattern="paid"))
    telegram_app.add_handler(CallbackQueryHandler(handle_back, pattern="back"))
    telegram_app.add_handler(CallbackQueryHandler(handle_support, pattern="support"))

    await telegram_app.initialize()
    await telegram_app.bot.delete_webhook()
    await telegram_app.bot.set_webhook(WEBHOOK_URL)
    await telegram_app.start()


@app.post("/webhook")
async def webhook(request: Request):
    global telegram_app
    update = Update.de_json(await request.json(), telegram_app.bot)
    await telegram_app.process_update(update)
    return {"status": "ok"}


# Start Command Handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("1 Month (£6.75)", callback_data="select_1_month")],
        [InlineKeyboardButton("Lifetime (£10.00)", callback_data="select_lifetime")],
        [InlineKeyboardButton("Support", callback_data="support")],
    ]
    await update.message.reply_text(
        "👋 Welcome to the VIP Bot!\n\n💎 Select your subscription plan below:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# Handle Subscription Plan Selection
async def handle_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    plan = query.data.split("_")[1]
    keyboard = [
        [InlineKeyboardButton("Stripe (Instant Access)", callback_data=f"payment_stripe_{plan}")],
        [InlineKeyboardButton("Crypto", callback_data=f"payment_crypto_{plan}")],
        [InlineKeyboardButton("PayPal", callback_data=f"payment_paypal_{plan}")],
        [InlineKeyboardButton("Go Back", callback_data="back")],
    ]

    message = (
        f"📋 You selected the **{plan.replace('_', ' ').upper()}** plan.\n\n"
        "Choose your preferred payment method below:\n"
        "💳 **Stripe (Apple Pay/Google Pay):** Instant access.\n"
        "⚡ **Crypto:** Manual processing.\n"
        "📧 **PayPal:** Manual processing."
    )
    await query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup(keyboard))


# Handle Payment Method Selection
async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        _, method, plan = query.data.split("_")
    except ValueError:
        await query.edit_message_text("❌ Invalid option. Please try again.", reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Go Back", callback_data="back")]]))
        return

    if method == "stripe":
        message = f"💳 **Stripe Payment (Instant Access):**\n[Pay Now]({PAYMENT_INFO['stripe']})\n\n" \
                  "After payment, click **'I've Paid'**."
    elif method == "crypto":
        message = f"⚡ **Crypto Payment:**\nSend payment to:\n🔗 `{PAYMENT_INFO['crypto']['eth']}`\n\n" \
                  "💰 **Prices:**\n- $8 Monthly\n- $15 Lifetime\n\nAfter payment, click **'I've Paid'**."
    elif method == "paypal":
        message = (
            "💰 **PayPal Payment:**\n\n"
            "💰 £10.00 GBP for LIFETIME\n"
            "💰 £6.75 GBP for 1 MONTH\n\n"
            f"➡️ PayPal: `{PAYMENT_INFO['paypal']}`\n\n"
            "✅ **MUST BE FRIENDS AND FAMILY**\n"
            "✅ **IF YOU DON'T HAVE FAMILY AND FRIENDS USE CARD/CRYPTO**\n"
            "❌ **DON'T LEAVE A NOTE**\n\n"
            "➡️ Click 'I Paid'\n"
            f"✅ Send payment screenshot to {SUPPORT_CONTACT} and provide your full PayPal name."
        )

    keyboard = [
        [InlineKeyboardButton("I've Paid", callback_data="paid")],
        [InlineKeyboardButton("Go Back", callback_data="back")],
    ]
    await query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")


# Confirm Payment
async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text="✅ Thank you for your payment! Please send a screenshot or transaction ID for verification to "
             f"{SUPPORT_CONTACT}.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Support", callback_data="support")],
            [InlineKeyboardButton("Go Back", callback_data="back")],
        ])
    )


# Handle Support Button
async def handle_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text=f"💬 **Support Contact:** {SUPPORT_CONTACT}\n\nPlease reach out if you need assistance!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Go Back", callback_data="back")]
        ])
    )


# Go Back to Main Menu
async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(query, context)
