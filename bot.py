from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler, ContextTypes

# Initialize Flask app
app = Flask(__name__)

# Define your bot token and other settings
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # Replace with your actual bot token
WEBHOOK_URL = "https://bot-1-f2wh.onrender.com/webhook"  # Replace with your Render URL
bot = Bot(token=TOKEN)

# Initialize the dispatcher
dispatcher = Dispatcher(bot, None, use_context=True)


# Define the start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    intro_text = (
        "👋 Welcome to the BADDIES FACTORY VIP Bot!\n\n"
        "💎 Access exclusive VIP content instantly with a growing collection every day.\n"
        "Choose your subscription plan below or contact support for assistance."
    )
    keyboard = [
        [InlineKeyboardButton("1 MONTH (£6.75)", callback_data="1_month"),
         InlineKeyboardButton("LIFETIME (£10)", callback_data="lifetime")],
        [InlineKeyboardButton("Support", callback_data="support")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(intro_text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.edit_text(intro_text, reply_markup=reply_markup)


# Define the subscription handler
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
        [InlineKeyboardButton("PayPal", callback_data="paypal"),
         InlineKeyboardButton("Go Back", callback_data="go_back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)


# Define the paid handler
async def paid_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    subscription = context.user_data.get("subscription", "Unknown Plan")
    admin_message = (
        f"✅ Payment Notification!\n\n"
        f"👤 User: @{user.username or 'No Username'} (ID: {user.id})\n"
        f"📄 Subscription: {subscription}\n"
    )

    # Send a message to the admin
    await bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_message)

    # Acknowledge the user's payment
    text = (
        "✅ Thank you for your payment! Please send a screenshot of your transaction "
        "or provide the transaction ID for verification to @zakivip1.\n\n"
        "💬 Need help? Contact @zakivip1."
    )
    keyboard = [[InlineKeyboardButton("Support", callback_data="support")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)


# Webhook route for Telegram updates
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), bot)
    dispatcher.process_update(update)
    return "OK", 200


# Set up the dispatcher with handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(subscription_handler, pattern="^(1_month|lifetime)$"))
dispatcher.add_handler(CallbackQueryHandler(paid_handler, pattern="^paid$"))


# Main function to run the app
if __name__ == "__main__":
    # Set webhook
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=10000)
    )