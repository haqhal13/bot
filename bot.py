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
    "shopify": "https://bot-1-f2wh.onrender.com/pay-now/{plan_type}",
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
    plan_text = "LIFETIME" if plan == "lifetime" else "MONTHLY"
    keyboard = [
        [InlineKeyboardButton("Lifetime (£10.00)", web_app=WebAppInfo(url=PAYMENT_INFO["shopify"].replace("{plan_type}", "lifetime")))],
        [InlineKeyboardButton("1 Month (£6.75)", web_app=WebAppInfo(url=PAYMENT_INFO["shopify"].replace("{plan_type}", "1_month")))],
        [InlineKeyboardButton("Support", callback_data="support")],
        [InlineKeyboardButton("Go Back", callback_data="back")],
    ]

    message = (
        f"📋 **You have chosen the {plan_text} plan.**\n\n"
        "💳 **Apple Pay/Google Pay (Instant Access):**\n\n"
        "💰 £10.00 GBP for LIFETIME\n"
        "💰 £6.75 GBP for 1 MONTH\n\n"
        "Click below to proceed. Your VIP link will be emailed instantly."
    )
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
    message = (
        "💬 **Contact Customer Support:**\n\n"
        "If you're having issues with payment, have questions, or haven’t received your VIP link yet, "
        "we're here to help!\n\n"
        "We operate between **7 AM and 12 AM BST** to ensure prompt assistance.\n\n"
        f"Reach out to us at {SUPPORT_CONTACT}."
    )
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Go Back", callback_data="back")],
        ]),
        parse_mode="Markdown"
    )

# Go Back to Main Menu
async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(query, context)
