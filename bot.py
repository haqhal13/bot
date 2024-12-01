from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import os

# Telegram Bot Token and Webhook URL
BOT_TOKEN = "123456789:EXAMPLETOKEN1234567890"  # Replace with your bot token
WEBHOOK_URL = "https://example-bot.onrender.com"  # Replace with your Render domain

# Initialize FastAPI app
app = FastAPI()

# Initialize Telegram bot application
telegram_app = Application.builder().token(BOT_TOKEN).build()

# Define Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /start command."""
    intro_text = (
        "👋 Welcome to the VIP Payment Bot!\n\n"
        "💎 Choose your subscription plan below to proceed:\n\n"
        "1 Month: £6.75\n"
        "Lifetime: £10"
    )
    keyboard = [
        [InlineKeyboardButton("PayPal", callback_data="paypal")],
        [InlineKeyboardButton("Apple Pay / Google Pay", callback_data="apple_google_pay")],
        [InlineKeyboardButton("Crypto (No KYC)", callback_data="crypto")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(intro_text, reply_markup=reply_markup)

async def payment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles payment options."""
    query = update.callback_query
    await query.answer()

    if query.data == "paypal":
        await query.edit_message_text(
            text="Send payment to:\n\n"
                 "💳 PayPal: onlyvipfan@outlook.com\n\n"
                 "💎 Pricing:\n"
                 "1 Month: £6.75\n"
                 "Lifetime: £10\n\n"
                 "✅ MUST BE FRIENDS AND FAMILY\n"
                 "❌ DO NOT LEAVE A NOTE\n\n"
                 "After payment, click 'I Paid' and provide your PayPal email.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Go Back", callback_data="go_back")]
            ])
        )

    elif query.data == "apple_google_pay":
        keyboard = [
            [
                InlineKeyboardButton(
                    "1 Month (£6.75)",
                    web_app=WebAppInfo(url="https://buy.stripe.com/8wM0041QI3xK3ficMP"),
                )
            ],
            [
                InlineKeyboardButton(
                    "Lifetime (£10)",
                    web_app=WebAppInfo(url="https://buy.stripe.com/aEUeUYaneecoeY03cc"),
                )
            ],
            [InlineKeyboardButton("Go Back", callback_data="go_back")],
        ]
        await query.edit_message_text(
            text="💳 Pay using Apple Pay / Google Pay via the links below:\n\n"
                 "💎 Pricing:\n"
                 "1 Month: £6.75\n"
                 "Lifetime: £10",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    elif query.data == "crypto":
        await query.edit_message_text(
            text="Send crypto to the following address:\n\n"
                 "💰 Bitcoin: 1ExampleBTCAddress\n"
                 "💰 Ethereum: 0xExampleETHAddress\n\n"
                 "💎 Pricing:\n"
                 "1 Month: $8\n"
                 "Lifetime: $14\n\n"
                 "After payment, click 'I Paid'.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Go Back", callback_data="go_back")]
            ])
        )

async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the Go Back action."""
    intro_text = (
        "👋 Welcome to the VIP Payment Bot!\n\n"
        "💎 Choose your subscription plan below to proceed:\n\n"
        "1 Month: £6.75\n"
        "Lifetime: £10"
    )
    keyboard = [
        [InlineKeyboardButton("PayPal", callback_data="paypal")],
        [InlineKeyboardButton("Apple Pay / Google Pay", callback_data="apple_google_pay")],
        [InlineKeyboardButton("Crypto (No KYC)", callback_data="crypto")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    await query.edit_message_text(intro_text, reply_markup=reply_markup)

# Add Handlers to Telegram App
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(payment_handler, pattern="^(paypal|apple_google_pay|crypto)$"))
telegram_app.add_handler(CallbackQueryHandler(go_back, pattern="^go_back$"))

# Webhook route
@app.post("/webhook")
async def webhook(request: Request):
    """Handle Telegram webhook updates."""
    update_data = await request.json()
    update = Update.de_json(update_data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"status": "ok"}

# Health Check
@app.get("/ping")
async def ping():
    """Health check endpoint."""
    return {"status": "ok"}

# On application startup, set Telegram webhook
@app.on_event("startup")
async def startup_event():
    """Set webhook on startup."""
    await telegram_app.bot.set_webhook(f"{WEBHOOK_URL}/webhook")

if __name__ == "__main__":
    import uvicorn

    # Get port for Render
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
