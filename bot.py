from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import logging
from datetime import datetime

# Constants
BOT_TOKEN = "7739378344:AAHRj6VmmmS19xCiIOFrdmyfcJ5_gRGXRHc"
WEBHOOK_URL = "https://bot-1-f2wh.onrender.com/webhook"
SUPPORT_CONTACT = "@ZakiVip1"
START_TIME = datetime.now()

# Payment Info
PAYMENT_INFO = {
    "shopify": "https://bot-1-f2wh.onrender.com/pay-now/{plan}",
    "crypto": {"eth": "0x9ebeBd89395CaD9C29Ee0B5fC614E6f307d7Ca82"},
    "paypal": "mailto:onlyvipfan@outlook.com",
}

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot")

# FastAPI App
app = FastAPI()
telegram_app = None


@app.get("/", response_class=Response)
async def root():
    return Response("Bot is active!", status_code=200)


@app.api_route("/ping", methods=["GET", "HEAD"])
async def ping():
    return Response("Pong!", status_code=200)


@app.api_route("/uptime", methods=["GET"])
async def uptime():
    return JSONResponse({
        "status": "online",
        "uptime": str(datetime.now() - START_TIME),
        "start_time": START_TIME.strftime("%Y-%m-%d %H:%M:%S"),
    })


@app.on_event("startup")
async def startup_event():
    global telegram_app
    telegram_app = Application.builder().token(BOT_TOKEN).build()
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CallbackQueryHandler(handle_subscription, pattern="select_.*"))
    telegram_app.add_handler(CallbackQueryHandler(handle_payment, pattern="payment_.*"))
    telegram_app.add_handler(CallbackQueryHandler(handle_support, pattern="support"))
    telegram_app.add_handler(CallbackQueryHandler(handle_back, pattern="back"))
    await telegram_app.initialize()
    await telegram_app.bot.delete_webhook()
    await telegram_app.bot.set_webhook(WEBHOOK_URL)
    await telegram_app.start()
    logger.info("Telegram bot started successfully.")


@app.post("/webhook")
async def webhook(request: Request):
    update = Update.de_json(await request.json(), telegram_app.bot)
    await telegram_app.process_update(update)
    return {"status": "ok"}


# Telegram Bot Handlers
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


async def handle_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    plan = query.data.split("_")[1]
    plan_text = "LIFETIME" if plan == "lifetime" else "1 MONTH"
    keyboard = [
        [InlineKeyboardButton("Apple Pay/Google Pay", callback_data=f"payment_shopify_{plan}")],
        [InlineKeyboardButton("Crypto", callback_data=f"payment_crypto_{plan}")],
        [InlineKeyboardButton("PayPal", callback_data=f"payment_paypal_{plan}")],
        [InlineKeyboardButton("Support", callback_data="support")],
        [InlineKeyboardButton("Go Back", callback_data="back")],
    ]

    message = f"📋 You selected **{plan_text}**.\n\nChoose your payment method:"
    await query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup(keyboard))


async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    method, plan = query.data.split("_")[1], query.data.split("_")[2]
    if method == "shopify":
        link = PAYMENT_INFO["shopify"].format(plan=plan)
        message = f"🛒 Click to pay: [Shopify Payment Link]({link})"
    elif method == "crypto":
        message = f"🔗 Send payment to this address:\n`{PAYMENT_INFO['crypto']['eth']}`"
    elif method == "paypal":
        message = f"💳 PayPal: {PAYMENT_INFO['paypal']}"

    await query.edit_message_text(
        text=message, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Go Back", callback_data="back")],
        ]), parse_mode="Markdown"
    )


async def handle_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        text=f"💬 **Contact Support:** {SUPPORT_CONTACT}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Go Back", callback_data="back")],
        ]), parse_mode="Markdown"
    )


async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, context)


# Run FastAPI
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
