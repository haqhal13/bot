from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import logging
import datetime  # For uptime calculation

# Constants
BOT_TOKEN = "7739378344:AAHRj6VmmmS19xCiIOFrdmyfcJ5_gRGXRHc"
WEBHOOK_URL = "https://bot-1-f2wh.onrender.com/webhook"

# Payment Links and Info
PAYMENT_INFO = {
    "stripe": "https://your-stripe-payment-link.com",
    "crypto": {
        "eth": "0x9ebeBd89395CaD9C29Ee0B5fC614E6f307d7Ca82",
        "prices": {"1_month": "$8", "lifetime": "$15"},
    },
    "paypal": "onlyvipfan@outlook.com"
}

# Shopify Checkout Links
SHOPIFY_CART_URLS = {
    "1_month": "https://5fbqad-qz.myshopify.com/cart/123456789:1?checkout",
    "lifetime": "https://5fbqad-qz.myshopify.com/cart/50086610207066:1?checkout",
}

# Support Contact
SUPPORT_CONTACT = "@ZakiVip1"

# Logging Configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("bot")

# FastAPI App
app = FastAPI()

# Start time for uptime tracking
START_TIME = datetime.datetime.now()

# Telegram Bot Application
telegram_app = None


@app.on_event("startup")
async def startup_event():
    global telegram_app
    if telegram_app is None:
        telegram_app = Application.builder().token(BOT_TOKEN).build()
        telegram_app.add_handler(CommandHandler("start", start))
        telegram_app.add_handler(CallbackQueryHandler(handle_subscription, pattern="select_.*"))
        telegram_app.add_handler(CallbackQueryHandler(handle_payment_method, pattern="payment_.*|back"))
        telegram_app.add_handler(CallbackQueryHandler(confirm_payment, pattern="paid"))
        await telegram_app.initialize()
        await telegram_app.bot.delete_webhook()
        await telegram_app.bot.set_webhook(WEBHOOK_URL)
        await telegram_app.start()


@app.post("/webhook")
async def webhook(request: Request):
    global telegram_app
    if not telegram_app:
        return {"status": "error", "message": "Application not initialized"}
    try:
        update_json = await request.json()
        update = Update.de_json(update_json, telegram_app.bot)
        await telegram_app.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        logger.exception(f"Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/pay-now/{plan_type}")
async def pay_now_page(plan_type: str):
    if plan_type not in SHOPIFY_CART_URLS:
        return HTMLResponse("<h1>Invalid Plan</h1>", status_code=400)
    return HTMLResponse(
        f"""
        <html>
        <head>
            <title>Redirecting...</title>
            <meta http-equiv="refresh" content="0;url={SHOPIFY_CART_URLS[plan_type]}" />
        </head>
        <body>
            Redirecting to Shopify checkout...
            <a href="{SHOPIFY_CART_URLS[plan_type]}">Click here if not redirected</a>
        </body>
        </html>
        """
    )


@app.get("/uptime")
async def uptime():
    current_time = datetime.datetime.now()
    uptime_duration = current_time - START_TIME
    return {"status": "ok", "uptime": str(uptime_duration)}


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
    message = (
        f"📋 You selected the **{plan.replace('_', ' ').upper()}** plan.\n\n"
        "Choose your preferred payment method below:\n\n"
        "💳 **Stripe (Apple Pay/Google Pay):** Instant access.\n"
        "⚡ **Crypto:** Manual processing.\n"
        "📧 **PayPal:** Manual processing."
    )

    keyboard = [
        [InlineKeyboardButton("Stripe (Instant Access)", callback_data=f"payment_stripe_{plan}")],
        [InlineKeyboardButton("Crypto", callback_data=f"payment_crypto_{plan}")],
        [InlineKeyboardButton("PayPal", callback_data=f"payment_paypal_{plan}")],
        [InlineKeyboardButton("Go Back", callback_data="back")],
    ]
    await query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup(keyboard))


async def handle_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, method, plan = query.data.split("_")

    if method == "stripe":
        message = f"💳 **Stripe Payment (Instant Access):**\n[Pay Now]({PAYMENT_INFO['stripe']})\n\n" \
                  "After payment, click **'I've Paid'**."
        keyboard = [[InlineKeyboardButton("I've Paid", callback_data="paid")],
                    [InlineKeyboardButton("Go Back", callback_data="back")]]
    elif method == "crypto":
        message = f"⚡ **Crypto Payment:**\nSend your payment to:\n" \
                  f"🔗 Ethereum: `{PAYMENT_INFO['crypto']['eth']}`\n\n" \
                  f"💰 **Prices:**\n- {PAYMENT_INFO['crypto']['prices']['1_month']} Monthly\n" \
                  f"- {PAYMENT_INFO['crypto']['prices']['lifetime']} Lifetime\n\n" \
                  "After payment, click **'I've Paid'**."
        keyboard = [[InlineKeyboardButton("I've Paid", callback_data="paid")],
                    [InlineKeyboardButton("Go Back", callback_data="back")]]
    elif method == "paypal":
        message = f"📧 **PayPal Payment:**\nSend payment to: `{PAYMENT_INFO['paypal']}`\n\n" \
                  "After payment, click **'I've Paid'**."
        keyboard = [[InlineKeyboardButton("I've Paid", callback_data="paid")],
                    [InlineKeyboardButton("Go Back", callback_data="back")]]

    await query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")


async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    message = f"✅ Thank you for your payment! Please send a screenshot or transaction ID for verification.\n\n" \
              f"💬 Need help? Contact: {SUPPORT_CONTACT}"
    keyboard = [[InlineKeyboardButton("Support", callback_data="support")],
                [InlineKeyboardButton("Go Back", callback_data="back")]]

    await query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup(keyboard))


async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update.callback_query, context)
