from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import logging

# Constants
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
WEBHOOK_URL = "https://your-render-url.com/webhook"

# Shopify Checkout Links (Replace with your dynamic cart links)
SHOPIFY_CART_URLS = {
    "1_month": "https://your-store.myshopify.com/cart/123456789:1",  # Product ID for 1-month subscription
    "lifetime": "https://your-store.myshopify.com/cart/987654321:1"  # Product ID for lifetime subscription
}

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
        telegram_app.add_handler(CallbackQueryHandler(handle_payment_method, pattern="shopify_.*"))
        await telegram_app.initialize()
        await telegram_app.bot.delete_webhook()
        await telegram_app.bot.set_webhook(WEBHOOK_URL)
        await telegram_app.start()

@app.post("/webhook")
async def webhook(request: Request):
    global telegram_app
    update_json = await request.json()
    update = Update.de_json(update_json, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"status": "ok", "message": "Bot is running!"}

# Intermediate "Pay Now" Page
@app.get("/pay-now/{plan_type}")
async def pay_now_page(plan_type: str):
    # Check if plan_type is valid
    if plan_type not in SHOPIFY_CART_URLS:
        return HTMLResponse("<h1>Invalid Plan</h1>", status_code=400)
    
    # HTML with auto-redirect to Shopify checkout
    pay_now_html = f"""
    <html>
    <head>
        <title>Pay Now</title>
        <meta http-equiv="refresh" content="0;url={SHOPIFY_CART_URLS[plan_type]}" />
        <script>
            window.onload = function() {{
                window.location.href = "{SHOPIFY_CART_URLS[plan_type]}";
            }};
        </script>
    </head>
    <body>
        <div style="text-align:center; margin-top:20%;">
            <h2>Redirecting you to checkout...</h2>
            <a href="{SHOPIFY_CART_URLS[plan_type]}" style="padding:10px 20px; background-color:blue; color:white; text-decoration:none;">
                Click here if you are not redirected
            </a>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=pay_now_html)

# Telegram Bot Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("1 Month (£6.75)", callback_data="select_1_month")],
        [InlineKeyboardButton("Lifetime (£10.00)", callback_data="select_lifetime")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👋 Choose your subscription plan below:", reply_markup=reply_markup)

async def handle_payment_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "select_1_month":
        keyboard = [[InlineKeyboardButton("Pay Now", callback_data="shopify_1_month")]]
        await query.edit_message_text("💳 *1 Month Subscription (£6.75):*\nClick below to pay securely:", 
                                      reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "select_lifetime":
        keyboard = [[InlineKeyboardButton("Pay Now", callback_data="shopify_lifetime")]]
        await query.edit_message_text("💳 *Lifetime Subscription (£10.00):*\nClick below to pay securely:", 
                                      reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    plan_type = query.data.split("_")[1]
    pay_now_link = f"https://your-render-url.com/pay-now/{plan_type}"  # Link to FastAPI page

    keyboard = [[InlineKeyboardButton("Pay Now", web_app=WebAppInfo(url=pay_now_link))]]
    await query.edit_message_text("🛒 *Proceed to Checkout:*\nClick below to complete your payment:",
                                  reply_markup=InlineKeyboardMarkup(keyboard))
