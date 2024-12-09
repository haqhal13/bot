from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
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
    telegram_app.add_handler(CallbackQueryHandler(handle_support, pattern="support"))
    telegram_app.add_handler(CallbackQueryHandler(handle_back, pattern="back"))
    telegram_app.add_handler(CallbackQueryHandler(handle_paid, pattern="paid"))
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
    # Send two separate messages
    await update.message.reply_text(f"👋 Hey {username}!")
    keyboard = [
        [InlineKeyboardButton("1 MONTH", callback_data="select_1_month")],
        [InlineKeyboardButton("LIFETIME", callback_data="select_lifetime")],
        [InlineKeyboardButton("❓ Support", callback_data="support")]
    ]
    await update.message.reply_text(
        "💎 Welcome to the VIP Bot!\n\n💎 Get access to 1000's of creators every month!\n⚡ INSTANT ACCESS TO VIP LINK SENT TO EMAIL!\n⭐ If we don’t have the model you're looking for, we’ll add them within 24–72 hours!\n\nSelect your subscription plan below or contact support for assistance! 🔍👀",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Plan Selection
async def handle_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    plan = query.data.split("_")[1]
    plan_name = "1 MONTH (£6.75)" if plan == "1_month" else "LIFETIME (£10.00)"
    plan_text = "🎉 You’ve Chosen LIFETIME Access! 🎉\nJust £10 for unlimited content! Pick your payment method below 💳" if plan == "lifetime" else "🎉 You’ve Chosen 1 MONTH Access! 🎉\nJust £6.75 to start exploring! Pick your payment method below 💳"

    keyboard = [
        [InlineKeyboardButton("🍏 Apple Pay / Google Pay", callback_data=f"payment_shopify_{plan}")],
        [InlineKeyboardButton("₿ Pay with Crypto", callback_data=f"payment_crypto_{plan}")],
        [InlineKeyboardButton("💳 PayPal Secure Checkout", callback_data=f"payment_paypal_{plan}")],
        [InlineKeyboardButton("🔙 Back", callback_data="back")],
        [InlineKeyboardButton("❓ Support", callback_data="support")]
    ]
    await query.message.edit_text(
        text=plan_text, reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Payment Methods
async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    method, plan = query.data.split("_")[1], query.data.split("_")[2]

    if method == "shopify":
        message = "✅ Pay Now via **Apple Pay / Google Pay**:\n[Click Here to Pay](https://bot-1-f2wh.onrender.com/pay-now/{}).\n\nAfter payment, click 'I've Paid'!".format(plan)
    elif method == "crypto":
        message = "💰 **Crypto Payment Options**:\n- **Ethereum**: `0x123456...\n- **Bitcoin**: `123456...`\n\nSend the payment and click 'I've Paid'."
    elif method == "paypal":
        message = "💳 **PayPal Secure Checkout**:\n➡️ Send payment to `onlyvipfan@outlook.com`\n✅ **MUST BE FRIENDS AND FAMILY**.\n❌ DON'T LEAVE A NOTE!\n\nClick 'I’ve Paid' after payment and send a screenshot to @ZakiVip1."

    keyboard = [
        [InlineKeyboardButton("✅ I’ve Paid", callback_data="paid")],
        [InlineKeyboardButton("🔙 Back", callback_data="back")],
        [InlineKeyboardButton("❓ Support", callback_data="support")]
    ]
    await query.message.edit_text(text=message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# Paid Confirmation
async def handle_paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("❓ Support", callback_data="support")],
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ]
    await query.message.edit_text(
        text="✅ **Thank you for your payment!**\n\n📸 Please send a screenshot or transaction ID to @ZakiVip1 for verification.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# Support Section
async def handle_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.edit_text(
        text="💬 **Contact Customer Support:**\n\nIf you're having payment issues, questions, or need help, we're here!\n\nWe operate between **7 AM and 12 AM BST**.\nReach out to us at @ZakiVip1.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]]),
        parse_mode="Markdown"
    )

# Back Navigation
async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start_callback_query(update, context)

async def start_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username or "there"
    keyboard = [
        [InlineKeyboardButton("1 MONTH", callback_data="select_1_month")],
        [InlineKeyboardButton("LIFETIME", callback_data="select_lifetime")],
        [InlineKeyboardButton("❓ Support", callback_data="support")]
    ]
    await update.callback_query.message.edit_text(
        f"👋 Hey {username}!\n\n💎 Welcome to the VIP Bot!\n\n💎 Get access to 1000's of creators every month!\n⚡ INSTANT ACCESS TO VIP LINK SENT TO EMAIL!\n⭐ If we don’t have the model you're looking for, we’ll add them within 24–72 hours!\n\nSelect your subscription plan below or contact support for assistance! 🔍👀",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Selection Handler
async def handle_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    plan = query.data.split("_")[1]
    plan_name = "1 MONTH (£6.75)" if plan == "1_month" else "LIFETIME (£10.00)"
    keyboard = [
        [InlineKeyboardButton("Apple Pay/Google Pay", callback_data=f"payment_shopify_{plan}")],
        [InlineKeyboardButton("Crypto", callback_data=f"payment_crypto_{plan}")],
        [InlineKeyboardButton("PayPal", callback_data=f"payment_paypal_{plan}")],
        [InlineKeyboardButton("Back", callback_data="back")],
        [InlineKeyboardButton("Support", callback_data="support")]
    ]
    await query.edit_message_text(
        text=f"📋 You selected **{plan_name}**.\n\nChoose your payment method:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# Payment Handler
async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    method, plan = query.data.split("_")[1], query.data.split("_")[2]
    if method == "shopify":
        keyboard = [[InlineKeyboardButton("I’ve Paid", callback_data="paid")],
                    [InlineKeyboardButton("Back", callback_data="back")],
                    [InlineKeyboardButton("Support", callback_data="support")]]
        message = "✅ Click to pay via Apple Pay/Google Pay: [Pay Now](https://bot-1-f2wh.onrender.com/pay-now/{})".format(plan)
    elif method == "crypto":
        message = "💰 Crypto Address:\n- Ethereum: 0x123456...\n- Bitcoin: 123456...\n- Solana: ...\nClick 'I’ve Paid' after sending payment."
        keyboard = [[InlineKeyboardButton("I’ve Paid", callback_data="paid")],
                    [InlineKeyboardButton("Back", callback_data="back")],
                    [InlineKeyboardButton("Support", callback_data="support")]]
    elif method == "paypal":
        message = "➡️ PayPal: onlyvipfan@outlook.com\n✅ MUST BE FRIENDS AND FAMILY.\n❌ DON'T LEAVE A NOTE.\nSend payment screenshot to @ZakiVip1."
        keyboard = [[InlineKeyboardButton("I’ve Paid", callback_data="paid")],
                    [InlineKeyboardButton("Back", callback_data="back")],
                    [InlineKeyboardButton("Support", callback_data="support")]]

    await query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# Paid Handler
async def handle_paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("Support", callback_data="support")],
        [InlineKeyboardButton("Go Back", callback_data="back")]
    ]
    await query.edit_message_text(
        text="✅ Thank you for your payment!\n📸 Please send a screenshot or transaction ID to @ZakiVip1 for verification.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Support Handler
async def handle_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text="💬 Contact Customer Support:\n\nIf you're having issues with payment, have questions, or haven’t received your VIP link yet, we're here to help!\n\nWe operate between 7 AM and 12 AM BST.\nReach out to us at @ZakiVip1.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Go Back", callback_data="back")]])
    )

# Back Handler
async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, context)
