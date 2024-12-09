from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import logging
import datetime

# Constants
BOT_TOKEN = "7739378344:AAHRj6VmmmS19xCiIOFrdmyfcJ5_gRGXRHc"  # Your bot token
WEBHOOK_URL = "https://bot-1-f2wh.onrender.com/webhook"

# Payment Links
SHOPIFY_CART_URLS = {
    "1_month": "https://5fbqad-qz.myshopify.com/cart/123456789:1?checkout",
    "lifetime": "https://5fbqad-qz.myshopify.com/cart/50086610207066:1?checkout"
}
PAYPAL_EMAIL = "your_paypal_email@example.com"
CRYPTO_ADDRESSES = {
    "BTC": "your_btc_wallet_address",
    "ETH": "your_eth_wallet_address",
}
STRIPE_LINKS = {
    "1_month": "https://buy.stripe.com/xyz12345",
    "lifetime": "https://buy.stripe.com/abc98765"
}

SUPPORT_CONTACT = "@ZakiVip1"

# Logging Configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("bot")

# FastAPI App
app = FastAPI()
START_TIME = datetime.datetime.now()
telegram_app = None

@app.on_event("startup")
async def startup_event():
    global telegram_app
    if telegram_app is None:
        telegram_app = Application.builder().token(BOT_TOKEN).build()
        telegram_app.add_handler(CommandHandler("start", start))
        telegram_app.add_handler(CallbackQueryHandler(handle_payment_selection, pattern="select_.*"))
        telegram_app.add_handler(CallbackQueryHandler(handle_payment_method, pattern="method_.*|back|support"))
        await telegram_app.initialize()
        await telegram_app.bot.delete_webhook()
        await telegram_app.bot.set_webhook(WEBHOOK_URL)
        await telegram_app.start()

@app.post("/webhook")
async def webhook(request: Request):
    global telegram_app
    try:
        update_json = await request.json()
        update = Update.de_json(update_json, telegram_app.bot)
        await telegram_app.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        logger.exception(f"Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/")
async def root():
    return {"status": "ok", "message": "Bot is running!"}

@app.get("/uptime")
async def uptime():
    uptime_duration = datetime.datetime.now() - START_TIME
    return {"status": "ok", "uptime": str(uptime_duration)}

# Start Command Handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("1 Month (£6.75)", callback_data="select_1_month")],
        [InlineKeyboardButton("Lifetime (£10.00)", callback_data="select_lifetime")],
        [InlineKeyboardButton("Support", callback_data="support")],
    ]
    await update.message.reply_text(
        "👋 Welcome to the VIP Bot!\n\n💎 Choose your subscription plan below:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Handle Plan Selection
async def handle_payment_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    plan_type = query.data.split("_")[1]
    message = f"💳 *{plan_type.replace('_', ' ').capitalize()} Subscription:*\n\nChoose your payment method:"
    keyboard = [
        [InlineKeyboardButton("PayPal", callback_data=f"method_paypal_{plan_type}")],
        [InlineKeyboardButton("Crypto", callback_data=f"method_crypto_{plan_type}")],
        [InlineKeyboardButton("Apple/Google Pay", callback_data=f"method_stripe_{plan_type}")],
        [InlineKeyboardButton("Back", callback_data="back"), InlineKeyboardButton("Support", callback_data="support")],
    ]
    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# Handle Payment Methods
async def handle_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data_parts = query.data.split("_")
    method, plan = data_parts[1], data_parts[2]

    if method == "paypal":
        message = f"💰 *PayPal Instructions:*\n\nSend *£6.75* for 1 Month or *£10.00* for Lifetime to:\n📧 `{PAYPAL_EMAIL}`\n\nClick 'Paid' after payment."
    elif method == "crypto":
        message = f"💰 *Crypto Payment:*\n\nSend to:\nBTC: `{CRYPTO_ADDRESSES['BTC']}`\nETH: `{CRYPTO_ADDRESSES['ETH']}`\n\nClick 'Paid' after payment."
    elif method == "stripe":
        pay_link = STRIPE_LINKS[plan]
        keyboard = [[InlineKeyboardButton("Pay Now", web_app=WebAppInfo(url=pay_link))]]
        await query.edit_message_text(f"💳 *Apple/Google Pay:*\n\nClick below to pay securely.", 
                                      reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    keyboard = [
        [InlineKeyboardButton("Paid", callback_data="support")],
        [InlineKeyboardButton("Back", callback_data=f"select_{plan}"), InlineKeyboardButton("Support", callback_data="support")],
    ]
    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# Support and Back Buttons
async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(f"💬 Contact Support: {SUPPORT_CONTACT}")

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)
