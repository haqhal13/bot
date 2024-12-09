from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from flask import Flask, Response
import logging
import httpx
from threading import Thread
from datetime import datetime

# Constants
BOT_TOKEN = "7739378344:AAHRj6VmmmS19xCiIOFrdmyfcJ5_gRGXRHc"
WEBHOOK_URL = "https://bot-1-f2wh.onrender.com/webhook"
SUPPORT_CONTACT = "@ZakiVip1"
ADMIN_CHAT_ID = 834523364
START_TIME = datetime.now()

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

# Flask App for Uptime Monitoring
flask_app = Flask(__name__)

@flask_app.route("/", methods=["GET"])
def uptime_home():
    """Root route to confirm the bot is live."""
    return Response("Bot is active at root!", status=200)

@flask_app.route("/ping", methods=["GET", "HEAD"])
def uptime_ping():
    """Ping Endpoint"""
    return Response("Bot is active at ping!", status=200)

@flask_app.route("/uptime", methods=["GET", "HEAD"])
def flask_uptime():
    """Uptime Check for Flask"""
    current_time = datetime.now()
    uptime_duration = current_time - START_TIME
    return {
        "status": "online",
        "uptime": str(uptime_duration),
        "start_time": START_TIME.strftime("%Y-%m-%d %H:%M:%S"),
    }, 200

# FastAPI Uptime Endpoint
@fastapi_app.api_route("/uptime", methods=["GET", "HEAD"])
async def fastapi_uptime():
    """Uptime Check for FastAPI"""
    current_time = datetime.now()
    uptime_duration = current_time - START_TIME
    return JSONResponse(content={
        "status": "online",
        "uptime": str(uptime_duration),
        "start_time": START_TIME.strftime("%Y-%m-%d %H:%M:%S")
    })

# Run Flask in a thread
def run_flask():
    flask_app.run(host="0.0.0.0", port=8000, use_reloader=False)

Thread(target=run_flask).start()

# Telegram Bot Initialization
@fastapi_app.on_event("startup")
async def startup_event():
    global telegram_app
    telegram_app = Application.builder().token(BOT_TOKEN).build()
    telegram_app.add_handler(CommandHandler("start", start))
    await telegram_app.initialize()
    await telegram_app.bot.delete_webhook()
    await telegram_app.bot.set_webhook(WEBHOOK_URL)
    await telegram_app.start()
    logger.info("Telegram Bot and FastAPI initialized.")

@fastapi_app.post("/webhook")
async def webhook(request: Request):
    global telegram_app
    update = Update.de_json(await request.json(), telegram_app.bot)
    await telegram_app.process_update(update)
    return {"status": "ok"}

# Telegram Handlers
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

# Other Telegram Handlers (unchanged)
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

async def handle_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(f"💬 **Contact Support:** {SUPPORT_CONTACT}")

async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await start(update.callback_query, context)

# Run FastAPI
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(fastapi_app, host="0.0.0.0", port=5000)
