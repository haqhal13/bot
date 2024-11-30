from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import os  # Ensure the os module is imported

# Example token and webhook URL
BOT_TOKEN = '7739378344:AAHePCaShSC60pN1VwX9AY4TqD-xZMxQ1gY'
WEBHOOK_URL = 'https://bot-1-f2wh.onrender.com'

if not BOT_TOKEN or not WEBHOOK_URL:
    raise ValueError("BOT_TOKEN and WEBHOOK_URL must be set.")

# Flask app for webhook handling
app = Flask(__name__)

# Telegram bot application
application = Application.builder().token(BOT_TOKEN).build()

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    intro_text = (
        "👋 Welcome to the VIP Bot!💎\n\n"
        "Access exclusive content instantly. Choose your subscription plan or contact support."
    )
    keyboard = [
        [InlineKeyboardButton("1 MONTH (£6.75)", callback_data="1_month"),
         InlineKeyboardButton("3 MONTHS (£19.75)", callback_data="3_months")],
        [InlineKeyboardButton("Support", url="https://t.me/YourSupportHandle")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(intro_text, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Type /start to begin using the bot.")

# Callback query handler
async def handle_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    subscription_message = f"You selected: {query.data.replace('_', ' ').title()}"
    await query.edit_message_text(subscription_message)

# Webhook route for Telegram updates
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.process_update(update)
    return "OK", 200

# Health check route for UptimeRobot
@app.route("/health", methods=["GET"])
def health_check():
    return "OK", 200

# Initialize handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CallbackQueryHandler(handle_subscription))

async def setup_webhook():
    """Set the Telegram bot webhook."""
    await application.bot.set_webhook(f"{WEBHOOK_URL}/{BOT_TOKEN}")

if __name__ == "__main__":
    import asyncio  # Import asyncio for async operations
    # Set up webhook asynchronously
    asyncio.run(setup_webhook())

    # Start Flask app
    port = int(os.environ.get("PORT", 5000))  # Ensure PORT is fetched from environment variables
    app.run(host="0.0.0.0", port=port)

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