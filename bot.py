from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from fastapi import FastAPI, Request
import logging
import httpx
from datetime import datetime
from fastapi.responses import JSONResponse
import threading

# Constants
BOT_TOKEN = "7739378344:AAHRj6VmmmS19xCiIOFrdmyfcJ5_gRGXRHc"
WEBHOOK_URL = "https://bot-1-f2wh.onrender.com/webhook"
SUPPORT_CONTACT = "@ZakiVip1"
ADMIN_CHAT_ID = 834523364  # Replace with the admin's chat ID

# Payment Information
PAYMENT_INFO = {
    "shopify": "https://bot-1-f2wh.onrender.com/pay-now/{plan_type}",
    "crypto": {"eth": "0x9ebeBd89395CaD9C29Ee0B5fC614E6f307d7Ca82"},
    "paypal": "onlyvipfan@outlook.com",
}

# Logging Configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("bot")

# FastAPI App
fastapi_app = FastAPI()
telegram_app = None
START_TIME = datetime.now()

# Flask App for Uptime Monitoring
flask_app = Flask(__name__)

@flask_app.route("/", methods=["GET"])
def uptime_home():
    """Root route to confirm the bot is live."""
    return "Bot is active at root!", 200

@flask_app.route("/ping", methods=["GET", "HEAD"])
def uptime_ping():
    """UptimeRobot Ping Endpoint"""
    return "Bot is active at ping!", 200


@fastapi_app.on_event("startup")
async def startup_event():
    global telegram_app
    telegram_app = Application.builder().token(BOT_TOKEN).build()
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CallbackQueryHandler(handle_subscription, pattern="select_.*"))
    telegram_app.add_handler(CallbackQueryHandler(handle_payment, pattern="payment_.*"))
    telegram_app.add_handler(CallbackQueryHandler(confirm_payment, pattern="paid"))
    telegram_app.add_handler(CallbackQueryHandler(handle_back, pattern="back"))
    telegram_app.add_handler(CallbackQueryHandler(handle_support, pattern="support"))

    logger.info("Telegram Bot Initialized!")

    await telegram_app.initialize()
    await telegram_app.bot.delete_webhook()
    await telegram_app.bot.set_webhook(WEBHOOK_URL)
    await telegram_app.start()


@fastapi_app.post("/webhook")
async def webhook(request: Request):
    global telegram_app
    update = Update.de_json(await request.json(), telegram_app.bot)
    await telegram_app.process_update(update)
    return {"status": "ok"}


@fastapi_app.get("/uptime")
async def get_uptime():
    current_time = datetime.now()
    uptime_duration = current_time - START_TIME
    return JSONResponse(content={
        "status": "online",
        "uptime": str(uptime_duration),
        "start_time": START_TIME.strftime("%Y-%m-%d %H:%M:%S")
    })


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
    plan_text = "LIFETIME" if plan == "lifetime" else "1 MONTH"
    keyboard = [
        [InlineKeyboardButton("Apple Pay/Google Pay (Instant Access)", callback_data=f"payment_shopify_{plan}")],
        [InlineKeyboardButton("Crypto", callback_data=f"payment_crypto_{plan}")],
        [InlineKeyboardButton("PayPal", callback_data=f"payment_paypal_{plan}")],
        [InlineKeyboardButton("Support", callback_data="support")],
        [InlineKeyboardButton("Go Back", callback_data="back")],
    ]

    message = (
        f"📋 You have chosen the **{plan_text}** plan.\n\n"
        "💰 Prices:\n"
        "💰 £10.00 GBP for LIFETIME\n"
        "💰 £6.75 GBP for 1 MONTH\n\n"
        "Choose your preferred payment method below:"
    )
    await query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup(keyboard))


# Handle Payment Method Selection
async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, method, plan = query.data.split("_")
    plan_text = "LIFETIME" if plan == "lifetime" else "1 MONTH"
    context.user_data["plan_text"] = plan_text
    context.user_data["method"] = method

    if method == "shopify":
        message = (
            "💳 **Apple Pay/Google Pay (Instant Access):**\n\n"
            "💰 £10.00 GBP for LIFETIME\n"
            "💰 £6.75 GBP for 1 MONTH\n\n"
            "Click below to proceed. After payment, click 'I've Paid'."
        )
        keyboard = [
            [InlineKeyboardButton("Lifetime (£10)", web_app=WebAppInfo(url=PAYMENT_INFO["shopify"].replace("{plan_type}", "lifetime")))],
            [InlineKeyboardButton("1 Month (£6.75)", web_app=WebAppInfo(url=PAYMENT_INFO["shopify"].replace("{plan_type}", "1_month")))],
            [InlineKeyboardButton("I've Paid", callback_data="paid")],
        ]
    elif method == "crypto":
        message = (
            "⚡ **Crypto Payment:**\nSend payment to:\n🔗 `"
            f"{PAYMENT_INFO['crypto']['eth']}`\n\n"
            "✅ After payment, click 'I've Paid'."
        )
        keyboard = [[InlineKeyboardButton("I've Paid", callback_data="paid")]]
    elif method == "paypal":
        message = (
            "💰 **PayPal Payment:**\n\n"
            f"➡️ PayPal: `{PAYMENT_INFO['paypal']}`\n\n"
            "✅ MUST BE FRIENDS AND FAMILY\n❌ DON'T LEAVE A NOTE"
        )
        keyboard = [[InlineKeyboardButton("I've Paid", callback_data="paid")]]

    await query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")


# Confirm Payment and Notify Admin
async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    username = query.from_user.username or "No Username"

    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"📝 **Payment Notification**\n👤 **User:** @{username}\n📋 **Plan:** {context.user_data['plan_text']}"
    )
    await query.edit_message_text("✅ Payment received! Contact support for activation.")


# Support and Back Handlers
async def handle_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(f"💬 **Contact Support:** {SUPPORT_CONTACT}")

async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await start(update.callback_query, context)

# Run Flask and FastAPI Simultaneously
if __name__ == "__main__":
    threading.Thread(target=lambda: flask_app.run(host="0.0.0.0", port=5000)).start()
    import uvicorn
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)
