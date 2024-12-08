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
    "1_month": {"price": "£6.75", "fastapi_pay_link": "/pay-now/1_month"},
    "lifetime": {"price": "£10.00", "fastapi_pay_link": "/pay-now/lifetime"},
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
        telegram_app.add_handler(CallbackQueryHandler(handle_payment_method, pattern="paypal_.*|shopify_.*|crypto_.*|back|paid|support"))
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

# "Pay Now" FastAPI Page
@app.get("/pay-now/{plan_type}")
async def pay_now_page(plan_type: str):
    # Map plan types to Shopify cart URLs
    shopify_cart_urls = {
        "1_month": "https://5fbqad-qz.myshopify.com/cart/123456789:1",  # Replace with actual variant ID
        "lifetime": "https://5fbqad-qz.myshopify.com/cart/9925739086170:1"  # Replace with actual variant ID
    }

    # Validate plan type
    if plan_type not in shopify_cart_urls:
        return HTMLResponse("<h1>Invalid Plan</h1>", status_code=400)

    # Generate HTML with "Pay Now" button that auto-triggers redirect
    pay_now_html = f"""
    <html>
    <head>
        <title>Pay Now</title>
        <script>
            function redirectToCheckout() {{
                window.location.href = "{shopify_cart_urls[plan_type]}";
            }}
            window.onload = redirectToCheckout;  // Auto-trigger redirect
        </script>
    </head>
    <body>
        <div style="text-align:center; margin-top:20%;">
            <h2>Click the button below to proceed with payment</h2>
            <button onclick="redirectToCheckout()" 
                style="padding:10px 20px; background-color:blue; color:white; border:none; font-size:16px;">
                Pay Now
            </button>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=pay_now_html)

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

    if query.data == "select_1_month":
        message = (
            "💳 *1 Month Subscription (£6.75):*\n\n"
            "Select your preferred payment method:"
        )
        keyboard = [
            [InlineKeyboardButton("PayPal", callback_data="paypal_1_month")],
            [InlineKeyboardButton("Pay Now (Shopify)", callback_data="shopify_1_month")],
        ]
        await query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "select_lifetime":
        message = (
            "💳 *Lifetime Subscription (£10.00):*\n\n"
            "Select your preferred payment method:"
        )
        keyboard = [
            [InlineKeyboardButton("PayPal", callback_data="paypal_lifetime")],
            [InlineKeyboardButton("Pay Now (Shopify)", callback_data="shopify_lifetime")],
        ]
        await query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup(keyboard))

# Handle Payment Methods
async def handle_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("shopify"):
        plan_type = query.data.split("_")[1]
        pay_link = f"https://bot-1-f2wh.onrender.com/pay-now/{plan_type}"
        message = (
            "🛒 *Pay Now:*\n\n"
            "Click below to proceed with payment securely."
        )
        keyboard = [[InlineKeyboardButton("Pay Now", web_app=WebAppInfo(url=pay_link))]]
        await query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup(keyboard))
