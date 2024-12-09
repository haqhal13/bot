from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from fastapi import FastAPI, Request
import logging
from datetime import datetime
import httpx

# Constants
BOT_TOKEN = "7739378344:AAHRj6VmmmS19xCiIOFrdmyfcJ5_gRGXRHc"
WEBHOOK_URL = "https://bot-1-f2wh.onrender.com/webhook"
UPTIME_MONITOR_URL = "https://uptimerobot.com/ping"

# Payment Information
PAYMENT_INFO = {
    "shopify": "https://bot-1-f2wh.onrender.com/pay-now/{plan_type}",
    "crypto": {"eth": "0x9ebeBd89395CaD9C29Ee0B5fC614E6f307d7Ca82"},
    "paypal": "onlyvipfan@outlook.com",
}

SUPPORT_CONTACT = "@ZakiVip1"
ADMIN_CONTACT = "@telehaq"

# Logging Configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("bot")

# FastAPI App
app = FastAPI()
telegram_app = None


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

    await telegram_app.initialize()
    await telegram_app.bot.delete_webhook()
    await telegram_app.bot.set_webhook(WEBHOOK_URL)
    await telegram_app.start()
    # Uptime Robot Ping
    await ping_uptime_robot()


@app.post("/webhook")
async def webhook(request: Request):
    global telegram_app
    update = Update.de_json(await request.json(), telegram_app.bot)
    await telegram_app.process_update(update)
    return {"status": "ok"}


async def ping_uptime_robot():
    """Ping UptimeRobot to ensure monitoring is active."""
    try:
        async with httpx.AsyncClient() as client:
            await client.get(UPTIME_MONITOR_URL)
            logger.info("Uptime Robot pinged successfully.")
    except Exception as e:
        logger.error(f"Failed to ping Uptime Robot: {e}")


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
    keyboard = [
        [InlineKeyboardButton("Apple Pay/Google Pay (Instant Access)", callback_data=f"payment_shopify_{plan}")],
        [InlineKeyboardButton("Crypto", callback_data=f"payment_crypto_{plan}")],
        [InlineKeyboardButton("PayPal", callback_data=f"payment_paypal_{plan}")],
        [InlineKeyboardButton("Support", callback_data="support")],
        [InlineKeyboardButton("Go Back", callback_data="back")],
    ]
    message = (
        f"📋 Choose your preferred payment method below:\n"
        "💳 **Apple Pay/Google Pay:** Instant access. VIP link will be emailed instantly.\n\n"
        "⚡ **Crypto:** VIP link will be sent within 30 minutes.\n\n"
        "📧 **PayPal:** VIP link will be sent within 30 minutes."
    )
    await query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup(keyboard))


# Handle Payment Method Selection
async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, method, plan = query.data.split("_")
    plan_text = "LIFETIME" if plan == "lifetime" else "1 MONTH"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    user = query.from_user.username or query.from_user.id
    await send_admin_notification(method, plan_text, current_time, user)

    if method == "paypal":
        message = (
            "💰 **PayPal Payment:**\n\n"
            f"➡️ PayPal: `{PAYMENT_INFO['paypal']}`\n\n"
            "✅ **MUST BE FRIENDS AND FAMILY**\n"
            "✅ **IF YOU DON'T HAVE FAMILY AND FRIENDS USE CARD/CRYPTO**\n"
            "❌ **DON'T LEAVE A NOTE**\n\n"
            "✅ Your VIP link will be sent within 30 minutes."
        )
    else:
        message = "Please proceed with the selected payment method."

    keyboard = [[InlineKeyboardButton("I've Paid", callback_data="paid")]]
    await query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")


# Notify Admin of Purchase
async def send_admin_notification(method, plan_text, current_time, user):
    notification = (
        f"📢 **New Payment Notification**\n"
        f"🗓 Date & Time: `{current_time}`\n"
        f"💳 Payment Method: `{method}`\n"
        f"🎟 Plan: `{plan_text}`\n"
        f"👤 User: @{user}"
    )
    await telegram_app.bot.send_message(chat_id=ADMIN_CONTACT, text=notification, parse_mode="Markdown")


# Confirm Payment
async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text="✅ Thank you for your payment! Please send a screenshot or transaction ID for verification to "
             f"{SUPPORT_CONTACT}.",
    )


# Handle Support
async def handle_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    message = f"💬 Contact support at {SUPPORT_CONTACT}."
    await query.edit_message_text(text=message)


# Go Back Fix
async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(query, context)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
