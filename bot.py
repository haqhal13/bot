from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from fastapi import FastAPI, Request
import logging

# Constants
BOT_TOKEN = "7739378344:AAHRj6VmmmS19xCiIOFrdmyfcJ5_gRGXRHc"
WEBHOOK_URL = "https://bot-1-f2wh.onrender.com/webhook"

# Payment Information
PAYMENT_INFO = {
    "1_month": {"price": "£6.75", "stripe_link": "https://buy.stripe.com/bIYbIMane1pCeY0eUZ"},
    "lifetime": {"price": "£10.00", "stripe_link": "https://buy.stripe.com/aEUeUYaneecoeY03cc"},
    "shopify_link": {
        "1_month": "https://5fbqad-qz.myshopify.com/cart/50086610207066:1?checkout",
        "lifetime": "https://5fbqad-qz.myshopify.com/cart/9925739086170:1?checkout"
    },
    "paypal_email": "onlyvipfan@outlook.com",
    "crypto_addresses": {"btc": "your-bitcoin-wallet", "eth": "0x9ebeBd89395CaD9C29Ee0B5fC614E6f307d7Ca82"},
}

# Contact Support
SUPPORT_CONTACT = "@ZakiVip1"

# Logging Configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("bot")

# FastAPI App
app = FastAPI()

# Telegram Bot Application
telegram_app = None


@app.on_event("startup")
async def startup_event():
    global telegram_app
    if telegram_app is None:
        telegram_app = Application.builder().token(BOT_TOKEN).build()
        telegram_app.add_handler(CommandHandler("start", start))
        telegram_app.add_handler(CallbackQueryHandler(handle_payment_selection, pattern="select_.*"))
        telegram_app.add_handler(CallbackQueryHandler(handle_payment_method, pattern="paypal_.*|stripe_.*|shopify_.*|crypto_.*|back|paid|support"))
        await telegram_app.initialize()
        logger.info("Telegram bot application initialized.")
        await telegram_app.bot.delete_webhook()
        await telegram_app.bot.set_webhook(WEBHOOK_URL)
        await telegram_app.start()


@app.post("/webhook")
async def webhook(request: Request):
    global telegram_app
    if not telegram_app:
        logger.error("Telegram application not initialized.")
        return {"status": "error", "message": "Application not initialized"}
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


@app.head("/uptime")
async def uptime():
    return {"status": "ok"}


# Start Command Handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("1 Month (£6.75)", callback_data="select_1_month")],
        [InlineKeyboardButton("Lifetime (£10.00)", callback_data="select_lifetime")],
        [InlineKeyboardButton("Support", callback_data="support")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Welcome to the VIP Bot!\n\n"
        "💎 Choose your subscription plan below to proceed:",
        reply_markup=reply_markup,
    )


# Handle Payment Selection
async def handle_payment_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("select_"):
        plan = query.data.split("_")[1]
        message = f"💳 *{plan.capitalize()} Subscription:*\n\nChoose your payment method below:"
        keyboard = [
            [InlineKeyboardButton("PayPal", callback_data=f"paypal_{plan}")],
            [InlineKeyboardButton("Stripe (Apple/Google Pay)", callback_data=f"stripe_{plan}")],
            [InlineKeyboardButton("Shopify Checkout", callback_data=f"shopify_{plan}")],
            [InlineKeyboardButton("Crypto", callback_data=f"crypto_{plan}")],
            [InlineKeyboardButton("Go Back", callback_data="back")],
        ]
        await query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")


# Handle Payment Methods
async def handle_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    plan_type = query.data.split("_")[1]

    if query.data.startswith("stripe"):
        stripe_link = PAYMENT_INFO[plan_type]["stripe_link"]
        message = f"💳 *Stripe Payment: {PAYMENT_INFO[plan_type]['price']}*\n\nPay securely via Apple Pay / Google Pay."
        await query.edit_message_text(
            text=message,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Pay Now", web_app=WebAppInfo(url=stripe_link))]])
        )

    elif query.data.startswith("shopify"):
        shopify_link = PAYMENT_INFO["shopify_link"][plan_type]
        message = "🛒 *Shopify Checkout:*\n\nProceed securely with Shopify payment."
        await query.edit_message_text(
            text=message,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Proceed", web_app=WebAppInfo(url=shopify_link))]])
        )

    elif query.data.startswith("paypal"):
        message = (
            f"💰 *PayPal Payment:*\n\n"
            f"Send {PAYMENT_INFO[plan_type]['price']} to:\n{PAYMENT_INFO['paypal_email']}\n\n"
            "❌ No notes allowed!\n✅ Click 'I Paid' after sending payment."
        )
        keyboard = [[InlineKeyboardButton("I Paid", callback_data="paid")], [InlineKeyboardButton("Back", callback_data="back")]]
        await query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data.startswith("crypto"):
        message = (
            f"💰 *Crypto Payment:*\n\nBTC: `{PAYMENT_INFO['crypto_addresses']['btc']}`\n"
            f"ETH: `{PAYMENT_INFO['crypto_addresses']['eth']}`\n\nAfter payment, click 'I Paid'."
        )
        keyboard = [[InlineKeyboardButton("I Paid", callback_data="paid")], [InlineKeyboardButton("Back", callback_data="back")]]
        await query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "paid":
        await query.edit_message_text(f"✅ Send your screenshot to {SUPPORT_CONTACT} for verification.")

    elif query.data == "back":
        await start(update, context)


# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
@app.head("/uptime")
async def uptime():
    return {"status": "ok"}
