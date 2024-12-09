from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import logging
from datetime import datetime, timedelta

# Constants
BOT_TOKEN = "7739378344:AAHRj6VmmmS19xCiIOFrdmyfcJ5_gRGXRHc"
WEBHOOK_URL = "https://bot-1-f2wh.onrender.com/webhook"
SUPPORT_CONTACT = "@ZakiVip1"
ADMIN_CHAT_ID = 834523364
SHOPIFY_LIFETIME_LINK = "https://shopify.com/lifetime"
SHOPIFY_MONTHLY_LINK = "https://shopify.com/monthly"
LAST_START_NOTIFICATION = {}

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
    now = datetime.now()

    # Admin notification limit
    if not LAST_START_NOTIFICATION.get(user_id) or now - LAST_START_NOTIFICATION[user_id] > timedelta(minutes=10):
        LAST_START_NOTIFICATION[user_id] = now
        await telegram_app.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"🟣 **Chat ID**: {user_id}\n🔵 **Username**: @{username}\n🚀 **Started the bot!**"
        )

    # User menu
    await update.message.reply_text(
        f"👋 Hey {username}!\n\n💎 Choose your subscription plan:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("1 MONTH (£6.75)", callback_data="select_1_month")],
            [InlineKeyboardButton("LIFETIME (£10.00)", callback_data="select_lifetime")],
            [InlineKeyboardButton("❓ Need Help?", callback_data="support")]
        ])
    )

# Plan Selection Handler
async def handle_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    plan = query.data.split("_")[1]

    # Payment method menu
    await query.message.edit_text(
        text=f"🎉 You’ve chosen **{'LIFETIME (£10.00)' if plan == 'lifetime' else '1 MONTH (£6.75)'}**!\nSelect your payment method:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🍏 Apple Pay / Google Pay", callback_data=f"payment_shopify_{plan}")],
            [InlineKeyboardButton("₿ Pay with Crypto", callback_data=f"payment_crypto_{plan}")],
            [InlineKeyboardButton("💳 PayPal Secure Checkout", callback_data=f"payment_paypal_{plan}")],
            [InlineKeyboardButton("🔙 Go Back", callback_data="back")],
            [InlineKeyboardButton("❓ Need Help?", callback_data="support")]
        ])
    )

# Payment Handler
async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    method, plan = query.data.split("_")[1], query.data.split("_")[2]

    if method == "shopify":
        shopify_link = SHOPIFY_LIFETIME_LINK if plan == "lifetime" else SHOPIFY_MONTHLY_LINK
        await query.message.edit_text(
            text=f"🛒 Use the button below to pay for **{plan.upper()}** via Apple Pay / Google Pay.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 Pay Now", web_app=WebAppInfo(url=shopify_link))],
                [InlineKeyboardButton("✅ I’ve Paid", callback_data=f"paid_shopify_{plan}")],
                [InlineKeyboardButton("🔙 Go Back", callback_data="back")],
                [InlineKeyboardButton("❓ Need Help?", callback_data="support")]
            ])
        )
    else:
        messages = {
            "crypto": "₿ **Pay with Crypto**:\n- Send your payment to:\n  **Bitcoin**: `1ABCDEF`\n\n✅ Click 'I’ve Paid' when complete.",
            "paypal": "💳 **PayPal Secure Checkout**:\n- Send payment to: `onlyvipfan@outlook.com`\n✅ Must be **Friends & Family**\n❌ Don’t leave a note!"
        }
        await query.message.edit_text(
            text=messages[method],
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ I’ve Paid", callback_data=f"paid_{method}_{plan}")],
                [InlineKeyboardButton("🔙 Go Back", callback_data="back")],
                [InlineKeyboardButton("❓ Need Help?", callback_data="support")]
            ]),
            parse_mode="Markdown"
        )

# Paid Handler
async def handle_paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    method, plan = query.data.split("_")[1], query.data.split("_")[2]
    username = query.from_user.username or "Unknown"
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Admin notification
    await telegram_app.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=(
            "✅ **Payment Notification**:\n"
            f"🔵 **Username**: @{username}\n"
            f"💳 **Subscription**: {plan.upper()} (£{'10.00' if plan == 'lifetime' else '6.75'})\n"
            f"🕒 **Time**: {time}\n"
            f"💼 **Payment Method**: {'Apple Pay/Google Pay' if method == 'shopify' else method.capitalize()}"
        )
    )

    # Confirmation message
    await query.message.edit_text(
        text="✅ **Thank you for your payment!**\n📸 Send a screenshot or transaction ID to @ZakiVip1 for verification.",
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
        text="💬 **Contact Support**:\nReach out to @ZakiVip1 for assistance.",
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
    await start(update, context)
