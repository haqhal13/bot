# -*- coding: utf-8 -*-
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
    
@app.get("/uptime")
async def uptime():
    return {"status": "OK", "message": "Service is running"}

@app.post("/webhook")
async def webhook(request: Request):
    update = Update.de_json(await request.json(), telegram_app.bot)
    await telegram_app.process_update(update)
    return {"status": "ok"}
    
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
    header = "🎉 You’ve Chosen LIFETIME Access! 🎉\nJust \u00A310 for unlimited content! Pick your payment method below 💳" if plan == "lifetime" else "🎉 You’ve Chosen 1 MONTH Access! 🎉\nJust \u00A36.75 to start exploring! Pick your payment method below 💳"

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


# Here is the fully updated script with the "I’ve Paid" button added to the Apple Pay/Google Pay mini-apps.
# The "I’ve Paid" button only appears after a user clicks on Lifetime (£10) or 1 Month (£6.75) within the Shopify mini-app options.

# Additionally:
# --- 
# Full Corrected Script

# After:
#python
# Example of fixed code
print("Hello World")
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import logging
from datetime import datetime, timedelta

# Constants
BOT_TOKEN = "7739378344:AAHRj6VmmmS19xCiIOFrdmyfcJ5_gRGXRHc"
WEBHOOK_URL = "https://bot-1-f2wh.onrender.com/webhook"
SUPPORT_CONTACT = "@ZakiVip1"
ADMIN_CHAT_ID = 834523364  # Admin Chat ID
SHOPIFY_LIFETIME_LINK = "https://shopify.com/lifetime"  # Replace with actual Shopify link
SHOPIFY_MONTHLY_LINK = "https://shopify.com/monthly"    # Replace with actual Shopify link
LAST_START_NOTIFICATION = {}  # Prevent repeated notifications

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
    header = "🎉 You’ve Chosen LIFETIME Access! 🎉\nJust \u00A310 for unlimited content! Pick your payment method below 💳" if plan == "lifetime" else "🎉 You’ve Chosen 1 MONTH Access! 🎉\nJust \u00A36.75 to start exploring! Pick your payment method below 💳"

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
                [InlineKeyboardButton("✅ I’ve Paid", callback_data=f"paid_shopify_{plan}")],
                [InlineKeyboardButton("🔙 Go Back", callback_data="back")],
                [InlineKeyboardButton("❓ Support", callback_data="support")]
            ])
        )
    else:
        message = {
            "crypto": "₿ Pay with Crypto:\nSend payment to:\n- **Ethereum**: `0x123456`\n✅ Click 'I Paid' when done.",
            "paypal": "💳 PayPal Secure Checkout:\n➡️ Send payment to `onlyvipfan@outlook.com`\n✅ **Friends and Family Only**\n❌ Don’t leave a note!"
        }
        await query.message.edit_text(
            text=message[method],
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ I’ve Paid", callback_data=f"paid_{method}_{plan}")],
                [InlineKeyboardButton("🔙 Go Back", callback_data="back")],
                [InlineKeyboardButton("❓ Support", callback_data="support")]
            ]),
            parse_mode="Markdown"
        )

# Paid Confirmation Handler
async def handle_paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Extract details
    method, plan = query.data.split("_")[1], query.data.split("_")[2]
    username = query.from_user.username or "Unknown"
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Notify admin
    await telegram_app.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=(
            "✅ **Payment Notification**:\n"
            f"🔵 **Username**: @{username}\n"
            f"💳 **Subscription**: {plan.upper()} (\u00A3{'10.00' if plan == 'lifetime' else '6.75'})\n"
            f"🕒 **Time**: {time}\n"
            f"💼 **Payment Method**: {'Apple Pay/Google Pay' if method == 'shopify' else method.capitalize()}"
        )
    )

    await query.message.edit_text(
        text="✅ **Thank you for your payment!**\n📸 Please send a screenshot or transaction ID to @ZakiVip1 for verification.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Go Back", callback_data="back")],
            [InlineKeyboardButton("❓ Need Help?", callback_data="support")]
        ]),
        parse_mode="Markdown"
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
    await start_callback_query(update, context)

async def start_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("1 MONTH (£6.75)", callback_data="select_1_month")],
        [InlineKeyboardButton("LIFETIME (£10.00)", callback_data="select_lifetime")],
        [InlineKeyboardButton("❓ Need Help?", callback_data="support")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.message.edit_text(
        text="💎 Welcome back! Please select a subscription plan:",
        reply_markup=reply_markup
    )

# Startup Event
@app.on_event("startup")
async def startup_event():
    global telegram_app
    telegram_app = Application.builder().token(BOT_TOKEN).build()
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CallbackQueryHandler(handle_selection, pattern="select_.*"))
    telegram_app.add_handler(CallbackQueryHandler(handle_payment, pattern="payment_.*"))
    telegram_app.add_handler(CallbackQueryHandler(handle_paid, pattern="paid_.*"))
    telegram_app.add_handler(CallbackQueryHandler(handle_support, pattern="support"))
    telegram_app.add_handler(CallbackQueryHandler(handle_back, pattern="back"))  # No error now
    await telegram_app.initialize()
    await telegram_app.bot.set_webhook(WEBHOOK_URL)
    await telegram_app.start()
    logger.info("Telegram bot started successfully.")
