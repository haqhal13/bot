from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import logging
import httpx

# Constants
BOT_TOKEN = "7739378344:AAHRj6VmmmS19xCiIOFrdmyfcJ5_gRGXRHc"
WEBHOOK_URL = "https://bot-1-f2wh.onrender.com/webhook"

# Payment Information
PAYMENT_INFO = {
    "1_month": {"price": "£6.75", "shopify_link": "/shopify-checkout/1_month"},
    "lifetime": {"price": "£10.00", "shopify_link": "https://5fbqad-qz.myshopify.com/checkouts/cn/Z2NwLWV1cm9wZS13ZXN0NDowMUpFS01ZUVg1S0ZQMFo0U0pCRUVRNzRRRA?skip_shop_pay=true"},
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


@app.get("/shopify-checkout/{plan_type}")
async def load_checkout(plan_type: str):
    # Map plan types to correct Shopify checkout URLs
    shopify_urls = {
        "1_month": "https://5fbqad-qz.myshopify.com/checkouts/cn/1-month-checkout-url?skip_shop_pay=true",
        "lifetime": "https://5fbqad-qz.myshopify.com/checkouts/cn/lifetime-checkout-url?skip_shop_pay=true"
    }
    
    # Validate plan type
    if plan_type not in shopify_urls:
        return HTMLResponse(content="<h1>Invalid Plan</h1>", status_code=400)

    # Fetch the Shopify checkout page
    async with httpx.AsyncClient() as client:
        response = await client.get(shopify_urls[plan_type])
        if response.status_code != 200:
            return HTMLResponse(content="<h1>Shopify Checkout Not Found</h1>", status_code=404)
        original_html = response.text

    # Inject custom CSS to hide the store name and header
    custom_css = """
    <style>
        header.header { display: none !important; }
        h1, .shop-name { display: none !important; }
        a { pointer-events: none !important; }
    </style>
    """
    modified_html = original_html.replace("</head>", f"{custom_css}</head>")
    return HTMLResponse(content=modified_html)


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
            [InlineKeyboardButton("Shopify (Secure Payment)", callback_data="shopify_1_month")],
        ]
        await query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "select_lifetime":
        message = (
            "💳 *Lifetime Subscription (£10.00):*\n\n"
            "Select your preferred payment method:"
        )
        keyboard = [
            [InlineKeyboardButton("PayPal", callback_data="paypal_lifetime")],
            [InlineKeyboardButton("Shopify (Secure Payment)", callback_data="shopify_lifetime")],
        ]
        await query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup(keyboard))


async def handle_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("shopify"):
        plan_type = query.data.split("_")[1]
        shopify_link = f"https://bot-1-f2wh.onrender.com/shopify-checkout/{plan_type}"
        message = (
            "🛒 *Shopify Payment:*\n\n"
            "Pay securely on our Shopify store. After payment, check your email for the VIP link."
        )
        keyboard = [[InlineKeyboardButton("Pay Now", web_app=WebAppInfo(url=shopify_link))]]
        await query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup(keyboard))
