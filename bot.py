from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import logging
from datetime import datetime, timedelta

# Constants
BOT_TOKEN = "7739378344:AAHRj6VmmmS19xCiIOFrdmyfcJ5_gRGXRHc"
WEBHOOK_URL = "https://bot-1-f2wh.onrender.com/webhook"
SUPPORT_CONTACT = "@ZakiVip1"
ADMIN_CHAT_ID = 834523364  # Your Chat ID
SHOPIFY_LIFETIME_LINK = "https://shopify.com/lifetime"  # Replace with your Shopify link
SHOPIFY_MONTHLY_LINK = "https://shopify.com/monthly"    # Replace with your Shopify link
LAST_START_NOTIFICATION = {}  # To prevent spamming admin notifications

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot")

# FastAPI App
app = FastAPI()
telegram_app = None

@app.on_event("startup")
async def startup_event():
    global telegram_app
    telegram_app = Application.builder().token(BOT_TOKEN).build()
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CallbackQueryHandler(handle_selection, pattern="select_.*"))
    telegram_app.add_handler(CallbackQueryHandler(handle_payment, pattern="payment_.*"))
    telegram_app.add_handler(CallbackQueryHandler(handle_paid, pattern="paid_.*"))
    telegram_app.add_handler(CallbackQueryHandler(handle_support, pattern="support"))
    telegram_app.add_handler(CallbackQueryHandler(handle_back, pattern="back"))
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
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"

    # Prevent spamming notifications to admin
    now = datetime.now()
    last_notified = LAST_START_NOTIFICATION.get(user_id, None)
    if not last_notified or now - last_notified > timedelta(minutes=10):
        LAST_START_NOTIFICATION[user_id] = now
        await telegram_app.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"🟣 **Chat ID**: {user_id}\n🔵 **Username**: @{username}\n🚀 **Started the bot!**"
        )

    # User start message
    await update.message.reply_text(f"👋 Hey {username}!")
    keyboard = [
        [InlineKeyboardButton("1 MONTH (\u00A36.75)", callback_data="select_1_month")],
        [InlineKeyboardButton("LIFETIME (\u00A310.00)", callback_data="select_lifetime")],
        [InlineKeyboardButton("❓ Need Help?", callback_data="support")]
    ]
    await update.message.reply_text(
        "💎 Welcome to the VIP Bot!\n\n💎 Get access to 1000's of creators every month!\n⚡ INSTANT ACCESS TO VIP LINK SENT TO EMAIL!\n⭐ If we don’t have the model you're looking for, we’ll add them within 24–72 hours!\n\nSelect your subscription plan below or contact support for assistance! 🔍👀",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Plan Selection Handler
async def handle_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    plan = query.data.split("_")[1]
    header = "🎉 You’ve Chosen LIFETIME Access! 🎉\nJust £10 for unlimited content! Pick your payment method below 💳" if plan == "lifetime" else "🎉 You’ve Chosen 1 MONTH Access! 🎉\nJust £6.75 to start exploring! Pick your payment method below 💳"

    keyboard = [
        [InlineKeyboardButton("🍏 Apple Pay / Google Pay", callback_data=f"payment_shopify_{plan}")],
        [InlineKeyboardButton("₿ Pay with Crypto", callback_data=f"payment_crypto_{plan}")],
        [InlineKeyboardButton("💳 PayPal Secure Checkout", callback_data=f"payment_paypal_{plan}")],
        [InlineKeyboardButton("🔙 Go Back", callback_data="back")],
        [InlineKeyboardButton("❓ Need Help?", callback_data="support")]
    ]
    await query.message.edit_text(
        text=header,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Payment Handler
async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    method, plan = query.data.split("_")[1], query.data.split("_")[2]

    if method == "shopify":
        shopify_link = SHOPIFY_LIFETIME_LINK if plan == "lifetime" else SHOPIFY_MONTHLY_LINK
        keyboard = [
            [InlineKeyboardButton("✅ I’ve Paid", callback_data=f"paid_shopify_{plan}")],
            [InlineKeyboardButton("🔙 Go Back", callback_data="back")],
            [InlineKeyboardButton("❓ Support", callback_data="support")]
        ]
        await query.message.edit_text(
            text=f"🛒 Click the button below to pay for **{plan.upper()}** via Apple Pay / Google Pay.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"Pay {plan.upper()}", web_app=WebAppInfo(url=shopify_link))],
                *keyboard
            ])
        )
    else:
        method_text = "PayPal" if method == "paypal" else "Crypto"
        keyboard = [
            [InlineKeyboardButton("✅ I’ve Paid", callback_data=f"paid_{method}_{plan}")],
            [InlineKeyboardButton("🔙 Go Back", callback_data="back")],
            [InlineKeyboardButton("❓ Support", callback_data="support")]
        ]
        await query.message.edit_text(
            f"💳 **{method_text} Checkout**:\nComplete your payment and press **'I’ve Paid'**.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# Paid Confirmation Handler
async def handle_paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    method, plan = query.data.split("_")[1], query.data.split("_")[2]
    username = query.from_user.username or "Unknown"
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    payment_method = {
        "shopify": "Apple Pay/Google Pay",
        "paypal": "PayPal",
        "crypto": "Crypto"
    }[method]
    await telegram_app.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=(
            "✅ **Payment Notification**:\n"
            f"🔵 **Username**: @{username}\n"
            f"💳 **Subscription**: {'LIFETIME (\u00A310.00)' if plan == 'lifetime' else '1 MONTH (\u00A36.75)'}\n"
            f"💼 **Payment Method**: {payment_method}\n"
            f"🕒 **Time**: {time}"
        )
    )

    await query.message.edit_text(
        text="✅ **Thank you for your payment!**\n📸 Send a screenshot or transaction ID to @ZakiVip1 for verification.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Go Back", callback_data="back")],
            [InlineKeyboardButton("❓ Need Help?", callback_data="support")]
        ])
    )

# Support Handler
async def handle_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.edit_text(
        text="💬 **Contact Support**:\nIf you need help, reach out to @ZakiVip1.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Go Back", callback_data="back")]
        ]),
        parse_mode="Markdown"
    )

# Back Handler
async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, context)
