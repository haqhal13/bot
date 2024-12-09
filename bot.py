from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import logging
from datetime import datetime

# Constants
BOT_TOKEN = "7739378344:AAHRj6VmmmS19xCiIOFrdmyfcJ5_gRGXRHc"
WEBHOOK_URL = "https://bot-1-f2wh.onrender.com/webhook"
SUPPORT_CONTACT = "@ZakiVip1"
START_TIME = datetime.now()

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
    telegram_app.add_handler(CallbackQueryHandler(handle_paid, pattern="paid"))
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
    username = update.effective_user.username or "there"
    keyboard = [
        [InlineKeyboardButton("1 MONTH (£6.75)", callback_data="select_1_month")],
        [InlineKeyboardButton("LIFETIME (£10)", callback_data="select_lifetime")],
        [InlineKeyboardButton("❓ Need Help?", callback_data="support")]
    ]
    if update.message:
        await update.message.reply_text(f"👋 Hey {username}!")
        await update.message.reply_text(
            "💎 Welcome to the VIP Bot!\n\n💎 Get access to 1000's of creators every month!\n⚡ INSTANT ACCESS TO VIP LINK SENT TO EMAIL!\n⭐ If we don’t have the model you're looking for, we’ll add them within 24–72 hours!\n\nSelect your subscription plan below or contact support for assistance! 🔍👀",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif update.callback_query:
        query = update.callback_query
        await query.message.edit_text(
            text=f"👋 Hey {username}!\n\n💎 Welcome to the VIP Bot!\n\n💎 Get access to 1000's of creators every month!\n⚡ INSTANT ACCESS TO VIP LINK SENT TO EMAIL!\n⭐ If we don’t have the model you're looking for, we’ll add them within 24–72 hours!\n\nSelect your subscription plan below or contact support for assistance! 🔍👀",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

# Plan Selection Handler
async def handle_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    plan = query.data.split("_")[1]
    header = (
        "🎉 You’ve Selected LIFETIME Access! 🎉\nJust £10 for unlimited content! Pick your payment method below 💳"
        if plan == "lifetime"
        else "🎉 You’ve Selected 1 MONTH Access! 🎉\nJust £6.75 to start exploring! Pick your payment method below 💳"
    )

    keyboard = [
        [InlineKeyboardButton("🍏 Apple Pay / Google Pay", callback_data=f"payment_shopify_{plan}")],
        [InlineKeyboardButton("₿ Pay with Crypto", callback_data=f"payment_crypto_{plan}")],
        [InlineKeyboardButton("💳 PayPal Secure Checkout", callback_data=f"payment_paypal_{plan}")],
        [InlineKeyboardButton("🔙 Go Back", callback_data="back")],
        [InlineKeyboardButton("❓ Need Help?", callback_data="support")]
    ]
    await query.message.edit_text(header, reply_markup=InlineKeyboardMarkup(keyboard))

# Updated Payment Handler with Mini Apps for Apple Pay / Google Pay
async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    method, plan = query.data.split("_")[1], query.data.split("_")[2]

    if method == "shopify":
        message = "🍏 **Apple Pay / Google Pay**\n\nSelect your plan below:"
        keyboard = [
            [
                InlineKeyboardButton(
                    "💎 Lifetime (£10)", 
                    web_app=WebAppInfo(url="SHOPIFY_LIFETIME_LINK")  # Replace with actual Shopify link
                )
            ],
            [
                InlineKeyboardButton(
                    "📅 1 Month (£6.75)", 
                    web_app=WebAppInfo(url="SHOPIFY_MONTHLY_LINK")  # Replace with actual Shopify link
                )
            ],
            [InlineKeyboardButton("🔙 Go Back", callback_data="back")],
            [InlineKeyboardButton("❓ Need Help?", callback_data="support")]
        ]
    elif method == "crypto":
        message = "₿ **Pay with Crypto**:\nSend payment to:\n- **Ethereum**: `0x123abc...`\n- **Bitcoin**: `1abc...`\n\nPress '✅ I’ve Paid' after completing the transaction."
        keyboard = [
            [InlineKeyboardButton("✅ I’ve Paid", callback_data="paid")],
            [InlineKeyboardButton("🔙 Go Back", callback_data="back")],
            [InlineKeyboardButton("❓ Need Help?", callback_data="support")]
        ]
    elif method == "paypal":
        message = (
            "💳 **PayPal Secure Checkout**:\n\n"
            "💰 **£10.00 - LIFETIME**\n💰 **£6.75 - 1 MONTH**\n\n"
            "➡️ PayPal: `onlyvipfan@outlook.com`\n"
            "✅ MUST BE FRIENDS AND FAMILY\n"
            "❌ DON'T LEAVE A NOTE\n\n"
            "➡️ CLICK 'I PAID'\n"
            "✅ Send payment screenshot to @ZakiVip1 and provide your full PayPal name."
        )
        keyboard = [
            [InlineKeyboardButton("✅ I’ve Paid", callback_data="paid")],
            [InlineKeyboardButton("🔙 Go Back", callback_data="back")],
            [InlineKeyboardButton("❓ Need Help?", callback_data="support")]
        ]

    await query.message.edit_text(
        text=message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )

# Paid Confirmation Handler
async def handle_paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.edit_text(
        text="✅ **Thank you for your payment!**\n\n📸 Please send a screenshot or transaction ID to @ZakiVip1 for verification.",
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
        text="💬 **Contact Support**:\nIf you're experiencing issues or need help, reach out to us at @ZakiVip1.\nWe’re available 7 AM to 12 AM BST.",
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
