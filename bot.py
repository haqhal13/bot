from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import logging
from datetime import datetime

# Constants
BOT_TOKEN = "7739378344:AAHRj6VmmmS19xCiIOFrdmyfcJ5_gRGXRHc"
WEBHOOK_URL = "https://bot-1-f2wh.onrender.com/webhook"
SUPPORT_CONTACT = "@ZakiVip1"
START_TIME = datetime.now()

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
    telegram_app.add_handler(CallbackQueryHandler(handle_selection, pattern="select_.*"))
    telegram_app.add_handler(CallbackQueryHandler(handle_payment, pattern="payment_.*"))
    telegram_app.add_handler(CallbackQueryHandler(handle_support, pattern="support"))
    telegram_app.add_handler(CallbackQueryHandler(handle_back, pattern="back"))
    telegram_app.add_handler(CallbackQueryHandler(handle_paid, pattern="paid"))
    await telegram_app.initialize()
    await telegram_app.bot.set_webhook(WEBHOOK_URL)
    await telegram_app.start()
    logger.info("Telegram bot started successfully.")

@app.post("/webhook")
async def webhook(request: Request):
    update = Update.de_json(await request.json(), telegram_app.bot)
    await telegram_app.process_update(update)
    return {"status": "ok"}

# Start Handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username or "there"
    keyboard = [
        [InlineKeyboardButton("1 MONTH", callback_data="select_1_month")],
        [InlineKeyboardButton("LIFETIME", callback_data="select_lifetime")],
        [InlineKeyboardButton("Support", callback_data="support")]
    ]
    await update.message.reply_text(
        f"👋 Hey {username}!\n\n💎 Get access to 1000's of creators every month!\n⚡ INSTANT ACCESS TO VIP LINK SENT TO EMAIL!\n⭐ If we don’t have the model you're looking for, we’ll add them within 24–72 hours!\n\nSelect your subscription plan below or contact support for assistance if you have questions! 🔍👀",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Selection Handler
async def handle_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    plan = query.data.split("_")[1]
    plan_name = "1 MONTH (£6.75)" if plan == "1_month" else "LIFETIME (£10.00)"
    keyboard = [
        [InlineKeyboardButton("Apple Pay/Google Pay", callback_data=f"payment_shopify_{plan}")],
        [InlineKeyboardButton("Crypto", callback_data=f"payment_crypto_{plan}")],
        [InlineKeyboardButton("PayPal", callback_data=f"payment_paypal_{plan}")],
        [InlineKeyboardButton("Back", callback_data="back")],
        [InlineKeyboardButton("Support", callback_data="support")]
    ]
    await query.edit_message_text(
        text=f"📋 You selected **{plan_name}**.\n\nChoose your payment method:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# Payment Handler
async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    method, plan = query.data.split("_")[1], query.data.split("_")[2]
    if method == "shopify":
        keyboard = [[InlineKeyboardButton("I’ve Paid", callback_data="paid")],
                    [InlineKeyboardButton("Back", callback_data="back")],
                    [InlineKeyboardButton("Support", callback_data="support")]]
        message = "✅ Click to pay via Apple Pay/Google Pay: [Pay Now](https://bot-1-f2wh.onrender.com/pay-now/{})".format(plan)
    elif method == "crypto":
        message = "💰 Crypto Address:\n- Ethereum: 0x123456...\n- Bitcoin: 123456...\n- Solana: ...\nClick 'I’ve Paid' after sending payment."
        keyboard = [[InlineKeyboardButton("I’ve Paid", callback_data="paid")],
                    [InlineKeyboardButton("Back", callback_data="back")],
                    [InlineKeyboardButton("Support", callback_data="support")]]
    elif method == "paypal":
        message = "➡️ PayPal: onlyvipfan@outlook.com\n✅ MUST BE FRIENDS AND FAMILY.\n❌ DON'T LEAVE A NOTE.\nSend payment screenshot to @ZakiVip1."
        keyboard = [[InlineKeyboardButton("I’ve Paid", callback_data="paid")],
                    [InlineKeyboardButton("Back", callback_data="back")],
                    [InlineKeyboardButton("Support", callback_data="support")]]

    await query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# Paid Handler
async def handle_paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("Support", callback_data="support")],
        [InlineKeyboardButton("Go Back", callback_data="back")]
    ]
    await query.edit_message_text(
        text="✅ Thank you for your payment!\n📸 Please send a screenshot or transaction ID to @ZakiVip1 for verification.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Support Handler
async def handle_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text="💬 Contact Customer Support:\n\nIf you're having issues with payment, have questions, or haven’t received your VIP link yet, we're here to help!\n\nWe operate between 7 AM and 12 AM BST.\nReach out to us at @ZakiVip1.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Go Back", callback_data="back")]])
    )

# Back Handler
async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, context)
