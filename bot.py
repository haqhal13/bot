from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import os
import requests

# Bot Token and Admin Details
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'  # Replace with your actual bot token
ADMIN_CHAT_ID = 834523364  # Replace with your admin chat ID

# Flask app for handling webhooks
app = Flask(__name__)

# Create the bot application
application = Application.builder().token(TOKEN).build()

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    intro_text = (
        "👋 Welcome to the BADDIES FACTORY VIP Bot!\n\n"
        "💎 Access exclusive VIP content instantly with a growing collection every day.\n"
        "Choose your subscription plan below or contact support for assistance."
    )
    keyboard = [
        [
            InlineKeyboardButton("1 MONTH (£6.75)", callback_data="1_month"),
            InlineKeyboardButton("LIFETIME (£10)", callback_data="lifetime"),
        ],
        [InlineKeyboardButton("Support", callback_data="support")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(intro_text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.edit_text(intro_text, reply_markup=reply_markup)

# Subscription handler
async def subscription_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    context.user_data["subscription"] = query.data.replace('_', ' ').upper()

    text = (
        f"📄 You selected the **{context.user_data['subscription']}** plan.\n\n"
        "Choose your preferred payment method below:\n"
        "💳 **Apple Pay / Google Pay:** Instant VIP access (emailed immediately).\n"
        "⚡ **Crypto:** VIP link will be sent within 30 minutes during BST hours.\n"
        "📧 **PayPal:** VIP link will be sent within 30 minutes during BST hours."
    )
    keyboard = [
        [InlineKeyboardButton("Apple Pay / Google Pay", callback_data="apple_google_pay"),
         InlineKeyboardButton("Crypto", callback_data="crypto")],
        [InlineKeyboardButton("PayPal", callback_data="paypal")],
        [InlineKeyboardButton("⬅️ Back", callback_data="back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(text, reply_markup=reply_markup)

# Back button handler
async def back_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start(update, context)

# Payment method handler
async def payment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "apple_google_pay":
        await query.message.reply_text("You chose Apple Pay / Google Pay. Payment instructions will be emailed.")
    elif query.data == "crypto":
        await query.message.reply_text("You chose Crypto. Send the payment to the provided wallet address.")
    elif query.data == "paypal":
        await query.message.reply_text("You chose PayPal. Send your payment to our secure PayPal account.")

# Support handler
async def support_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Support is available. Contact @YourSupportHandle.")

# Handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(subscription_handler, pattern="1_month|lifetime"))
application.add_handler(CallbackQueryHandler(payment_handler, pattern="apple_google_pay|crypto|paypal"))
application.add_handler(CallbackQueryHandler(back_button_handler, pattern="back"))
application.add_handler(CallbackQueryHandler(support_handler, pattern="support"))

# Webhook route
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    """Handle incoming webhook requests from Telegram."""
    json_data = request.get_json()
    update = Update.de_json(json_data, application.bot)
    application.process_update(update)
    return "OK", 200

if __name__ == "__main__":
    # Set the webhook URL
    webhook_url = f'https://your-service-name.onrender.com/{TOKEN}'
    requests.get(f'https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}')

    # Run Flask app on Render's expected port
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)