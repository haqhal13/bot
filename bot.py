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
app = FastAPI()
telegram_app = None

# Uptime Monitoring Routes
@app.get("/", response_class=Response)
async def root():
    """Root route to confirm bot is live."""
    logger.info("Root route pinged!")
    return Response("Bot is active at root!", status_code=200)

@app.api_route("/ping", methods=["GET", "HEAD"])
async def ping():
    """Ping endpoint for UptimeRobot."""
    logger.info("Ping route checked!")
    return Response("Bot is active at ping!", status_code=200)

@app.api_route("/uptime", methods=["GET", "HEAD"])
async def uptime():
    """Uptime Check for FastAPI."""
    logger.info("Uptime check triggered!")
    current_time = datetime.now()
    uptime_duration = current_time - START_TIME
    return JSONResponse(content={
        "status": "online",
        "uptime": str(uptime_duration),
        "start_time": START_TIME.strftime("%Y-%m-%d %H:%M:%S")
    })

# Telegram Bot Initialization
@app.on_event("startup")
async def startup_event():
    global telegram_app
    logger.info("Initializing Telegram bot...")
    telegram_app = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CallbackQueryHandler(handle_subscription, pattern="select_.*"))
    telegram_app.add_handler(CallbackQueryHandler(handle_support, pattern="support"))
    telegram_app.add_handler(CallbackQueryHandler(handle_back, pattern="back"))

    await telegram_app.initialize()
    logger.info("Deleting any existing webhooks...")
    await telegram_app.bot.delete_webhook()

    logger.info(f"Setting new webhook: {WEBHOOK_URL}")
    success = await telegram_app.bot.set_webhook(WEBHOOK_URL)
    if success:
        logger.info("Webhook set successfully!")
    else:
        logger.error("Failed to set webhook!")

    await telegram_app.start()
    logger.info("Telegram Bot and FastAPI initialized successfully.")

@app.post("/webhook")
async def webhook(request: Request):
    """Handle Telegram updates."""
    global telegram_app
    try:
        update_data = await request.json()
        logger.debug(f"Received webhook update: {update_data}")
        update = Update.de_json(update_data, telegram_app.bot)
        await telegram_app.process_update(update)
        logger.info("Update processed successfully.")
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Telegram Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Start command triggered by {update.effective_user.username}")
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
    logger.info(f"Subscription callback received: {query.data}")
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
    logger.info("Support callback triggered.")
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(f"💬 **Contact Support:** {SUPPORT_CONTACT}")

async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Back callback triggered.")
    await update.callback_query.answer()
    await start(update.callback_query, context)

# Run FastAPI
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI application...")
    uvicorn.run(app, host="0.0.0.0", port=5000)
