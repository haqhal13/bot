from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from fastapi import FastAPI, Request
import logging
import httpx
from datetime import datetime
from fastapi.responses import JSONResponse

# Constants
BOT_TOKEN = "7739378344:AAHRj6VmmmS19xCiIOFrdmyfcJ5_gRGXRHc"
WEBHOOK_URL = "https://bot-1-f2wh.onrender.com/webhook"
UPTIME_MONITOR_URL = "https://bot-1-f2wh.onrender.com/uptime"
SUPPORT_CONTACT = "@ZakiVip1"
ADMIN_CHAT_ID = 834523364  # Admin's Telegram Chat ID

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
app = FastAPI()
telegram_app = None
START_TIME = datetime.now()

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
    logger.info("Telegram Bot Initialized!")

    # Uptime Robot Monitoring
    async with httpx.AsyncClient() as client:
        await client.get(UPTIME_MONITOR_URL)
        logger.info("Uptime Monitoring Reintegrated!")

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


@app.get("/uptime")
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


# Handle Payment and Notify Admin
async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, method, plan = query.data.split("_")
    plan_text = "LIFETIME" if plan == "lifetime" else "1 MONTH"

    message, keyboard = "", []

    if method == "shopify":
        message = f"💳 **Apple Pay/Google Pay (Instant Access):**\n💰 £10.00 GBP for LIFETIME\n💰 £6.75 GBP for 1 MONTH"
        keyboard = [
            [InlineKeyboardButton("Lifetime (£10)", web_app=WebAppInfo(url=PAYMENT_INFO["shopify"].replace("{plan_type}", "lifetime")))],
            [InlineKeyboardButton("1 Month (£6.75)", web_app=WebAppInfo(url=PAYMENT_INFO["shopify"].replace("{plan_type}", "1_month")))],
            [InlineKeyboardButton("I've Paid", callback_data="paid")]
        ]

    elif method == "crypto":
        message = f"⚡ **Crypto Payment:** Send to `{PAYMENT_INFO['crypto']['eth']}`\n\n💰 £10.00 GBP for LIFETIME\n💰 £6.75 GBP for 1 MONTH"
        keyboard = [[InlineKeyboardButton("I've Paid", callback_data="paid")]]

    elif method == "paypal":
        message = f"💰 **PayPal Payment:** `{PAYMENT_INFO['paypal']}`\n\n💰 £10.00 GBP for LIFETIME\n💰 £6.75 GBP for 1 MONTH"
        keyboard = [[InlineKeyboardButton("I've Paid", callback_data="paid")]]

    keyboard += [[InlineKeyboardButton("Support", callback_data="support"), InlineKeyboardButton("Go Back", callback_data="back")]]

    await query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")


# Confirm Payment and Notify Admin
async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    username = query.from_user.username or "No Username"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"✅ Payment Confirmed\n👤 User: @{username}\n🕒 Time: {current_time}",
        parse_mode="Markdown"
    )

    await query.edit_message_text(
        text=f"✅ Thank you for your payment! Send a screenshot to {SUPPORT_CONTACT}.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Support", callback_data="support")],
            [InlineKeyboardButton("Go Back", callback_data="back")]
        ]),
        parse_mode="Markdown"
    )


# Support Handler
async def handle_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text=f"💬 **Contact Support:** {SUPPORT_CONTACT}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Go Back", callback_data="back")]]),
        parse_mode="Markdown"
    )


# Go Back Handler
async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(query, context)
