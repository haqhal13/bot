from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from fastapi import FastAPI, Request
import logging
import httpx
from datetime import datetime
from fastapi.responses import JSONResponse

# Constants
BOT_TOKEN = "7739378344:AAHRj6VmmmS19xCiIOFrdmyfcJ5_gRGXRHc"
WEBHOOK_URL = "https://bot-1-f2wh.onrender.com/webhook"
UPTIME_MONITOR_URL = "https://bot-1-f2wh.onrender.com/uptime"
SUPPORT_CONTACT = "@ZakiVip1"
ADMIN_CHAT_ID = 834523364  # Replace with the admin's chat ID

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
START_TIME = datetime.now()


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

    logger.info("Telegram Bot Initialized!")

    # Uptime Robot Monitoring
    async with httpx.AsyncClient() as client:
        await client.get(UPTIME_MONITOR_URL)
        logger.info("Uptime Monitoring Reintegrated!")

    await telegram_app.initialize()
    await telegram_app.bot.delete_webhook()
    await telegram_app.bot.set_webhook(WEBHOOK_URL)
    await telegram_app.start()


@app.post("/webhook")
async def webhook(request: Request):
    global telegram_app
    update = Update.de_json(await request.json(), telegram_app.bot)
    await telegram_app.process_update(update)
    return {"status": "ok"}


@app.get("/uptime")
async def get_uptime():
    current_time = datetime.now()
    uptime_duration = current_time - START_TIME
    return JSONResponse(content={
        "status": "online",
        "uptime": str(uptime_duration),
        "start_time": START_TIME.strftime("%Y-%m-%d %H:%M:%S")
    })


# Start Command Handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("1 Month (£6.75)", callback_data="select_1_month")],
        [InlineKeyboardButton("Lifetime (£10.00)", callback_data="select_lifetime")],
        [InlineKeyboardButton("Support", callback_data="support")],
    ]
    await update.message.reply_text(
        "💎 **Welcome to the VIP Bot!**\n\n"
        "💎 *Get access to thousands of creators every month!*\n"
        "⚡ *Instant access to the VIP link sent directly to your email!*\n"
        "⭐ *Don’t see the model you’re looking for? We’ll add them within 24–72 hours!*\n\n"
        "📌 Select your subscription plan below or contact support for assistance! 🔍👀",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )

# Handle Subscription Plan Selection
async def handle_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    plan = query.data.split("_")[1]
    plan_text = "LIFETIME" if plan == "lifetime" else "1 MONTH"
    keyboard = [
        [InlineKeyboardButton("💳 Apple Pay/Google Pay 🚀 (Instant Access)", callback_data=f"payment_shopify_{plan}")],
        [InlineKeyboardButton("⚡ Crypto ⏳ (Secure Payment)", callback_data=f"payment_crypto_{plan}")],
        [InlineKeyboardButton("📧 PayPal 💌 (Easy & Quick)", callback_data=f"payment_paypal_{plan}")],
        [InlineKeyboardButton("💬 Support", callback_data="support")],
        [InlineKeyboardButton("🔙 Go Back", callback_data="back")],
    ]

    message = (
        f"⭐ You have chosen the **{plan_text}** plan.\n\n"
        "💳 **Apple Pay/Google Pay:** 🚀 Instant VIP access (link emailed immediately).\n"
        "⚡ **Crypto:** ⏳ Secure payment, VIP link sent manually.\n"
        "📧 **PayPal:** 💌 Easy and quick, VIP link sent manually.\n\n"
        "🎉 Choose your preferred payment method below and get access today!"
    )
    await query.edit_message_text(
        text=message, 
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# Handle Payment Method Selection
async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, method, plan = query.data.split("_")
    plan_text = "LIFETIME" if plan == "lifetime" else "1 MONTH"
    username = query.from_user.username or "No Username"

    # Store data for later use in confirmation
    context.user_data["plan_text"] = plan_text
    context.user_data["method"] = method

    # Payment Details
    if method == "shopify":
        message = (
            "🚀 **Instant Access with Apple Pay/Google Pay!**\n\n"
            "🎁 **Choose Your VIP Plan:**\n"
            "💎 Lifetime Access: **£10.00 GBP** 🎉\n"
            "⏳ 1 Month Access: **£6.75 GBP** 🌟\n\n"
            "🛒 Click below to pay securely and get **INSTANT VIP access** delivered to your email! 📧\n\n"
            "✅ After payment, click 'I've Paid' to confirm."
        )
        keyboard = [
            [InlineKeyboardButton("💎 Lifetime (£10.00)", web_app=WebAppInfo(url=PAYMENT_INFO["shopify"].replace("{plan_type}", "lifetime")))],
            [InlineKeyboardButton("⏳ 1 Month (£6.75)", web_app=WebAppInfo(url=PAYMENT_INFO["shopify"].replace("{plan_type}", "1_month")))],
            [InlineKeyboardButton("✅ I've Paid", callback_data="paid")],
        ]
    elif method == "crypto":
        message = (
            "⚡ **Pay Securely with Crypto!**\n\n"
            "🔗 **Send Your Payment To:**\n"
            f"`{PAYMENT_INFO['crypto']['eth']}`\n\n"
            "💎 **Choose Your Plan:**\n"
            "⏳ 1 Month Access: **$8 USD** 🌟\n"
            "💎 Lifetime Access: **$15 USD** 🎉\n\n"
            "✅ Once you've sent the payment, click 'I've Paid' to confirm.\n"
            "📨 Your VIP link will be sent to you manually. Thank you! 💖"
        )
        keyboard = [[InlineKeyboardButton("✅ I've Paid", callback_data="paid")]]
    elif method == "paypal":
        message = (
            "💸 **Easy Payment with PayPal!**\n\n"
            "➡️ **Send Payment To:**\n"
            f"`{PAYMENT_INFO['paypal']}`\n\n"
            "💎 **Choose Your Plan:**\n"
            "⏳ 1 Month Access: **£6.75 GBP** 🌟\n"
            "💎 Lifetime Access: **£10.00 GBP** 🎉\n\n"
            "⚠️ **Important:**\n"
            "✅ Send as **Friends and Family**.\n"
            "❌ *Do NOT leave a note.*\n\n"
            "✅ Once payment is complete, click 'I've Paid' to confirm.\n"
            "📨 Your VIP link will be sent manually. Thank you! 💖"
        )
        keyboard = [
            [InlineKeyboardButton("✅ I've Paid", callback_data="paid")],
            [InlineKeyboardButton("💬 Support", callback_data="support")],
            [InlineKeyboardButton("🔙 Go Back", callback_data="back")],
        ]
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# Confirm Payment and Notify Admin
async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    username = query.from_user.username or "No Username"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    plan_text = context.user_data.get("plan_text", "N/A")
    method = context.user_data.get("method", "N/A")

    # Notify admin
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=(
            f"📝 **Payment Notification**\n"
            f"👤 **User:** @{username}\n"
            f"📋 **Plan:** {plan_text}\n"
            f"💳 **Method:** {method.capitalize()}\n"
            f"🕒 **Time:** {current_time}"
        ),
        parse_mode="Markdown"
    )

# Confirm Payment and Notify Admin
async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    username = query.from_user.username or "No Username"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    plan_text = context.user_data.get("plan_text", "N/A")
    method = context.user_data.get("method", "N/A")

    # Notify admin
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=(
            f"📝 **Payment Notification**\n"
            f"👤 **User:** @{username}\n"
            f"📋 **Plan:** {plan_text}\n"
            f"💳 **Method:** {method.capitalize()}\n"
            f"🕒 **Time:** {current_time}"
        ),
        parse_mode="Markdown"
    )

    # Notify user
    await query.edit_message_text(
        text=(
            "✅ **Payment Received! Thank You!** 🎉\n\n"
            "📸 Please send a **screenshot** or **transaction ID** to our support team for verification:\n"
            f"👉 {SUPPORT_CONTACT}\n\n"
            "⚡ **Important Notice:**\n"
            "🔗 If you paid via **PayPal** or **Crypto**, your VIP link will be sent manually once the owner comes online.\n"
            "⏰ Our support team operates **8:00 AM - 12:00 AM BST**.\n\n"
            "Thank you for choosing VIP Bot! 💎 Your patience is greatly appreciated."
        ),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Support", callback_data="support")],
            [InlineKeyboardButton("🔙 Go Back", callback_data="back")]
        ]),
        parse_mode="Markdown"
    )

# Support Handler
async def handle_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text=(
            "💬 **Need Assistance? We're Here to Help!**\n\n"
            f"🕒 **Working Hours:** 8:00 AM - 12:00 AM BST\n"
            "📨 For support, contact us directly at:\n"
            f"👉 {SUPPORT_CONTACT}\n\n"
            "⚡ Our team is ready to assist you as quickly as possible. "
            "Thank you for choosing VIP Bot! 💎"
        ),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Go Back", callback_data="back")]
        ]),
        parse_mode="Markdown"
    )

# Go Back Handler
async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(query, context)

from fastapi import Response

# UPTIME
@app.head("/uptime")
async def head_uptime():
    return Response(status_code=200)
