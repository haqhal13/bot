from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import CommandHandler, CallbackQueryHandler, Application
import os

TOKEN = "7739378344:AAHePCaShSC60pN1VwX9AY4TqD-xZMxQ1gY"
WEBHOOK_URL = "https://bot-1-f2wh.onrender.com/webhook"

# Initialize Flask app
flask_app = Flask(__name__)

# Initialize Telegram Bot
bot_app = Application.builder().token(TOKEN).build()

@flask_app.route('/webhook', methods=['POST'])
def webhook_handler():
    """Handle incoming webhook updates from Telegram."""
    if request.method == "POST":
        update = Update.de_json(request.get_json(), bot_app.bot)
        bot_app.process_update(update)
        return "OK", 200

# Define /start command
async def start(update: Update, context):
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
    await update.message.reply_text(intro_text, reply_markup=reply_markup)

# Define CallbackQueryHandler for subscriptions
async def subscription_handler(update: Update, context):
    query = update.callback_query
    await query.answer()

    subscription = query.data.replace('_', ' ').upper()
    context.user_data["subscription"] = subscription

    text = (
        f"📄 You selected the **{subscription}** plan.\n\n"
        "Choose your preferred payment method below:\n"
        "💳 **Apple Pay / Google Pay:** Instant VIP access (emailed immediately).\n"
        "⚡ **Crypto:** VIP link will be sent within 30 minutes during BST hours.\n"
        "📧 **PayPal:** VIP link will be sent within 30 minutes during BST hours."
    )
    keyboard = [
        [
            InlineKeyboardButton("Apple Pay / Google Pay", callback_data="apple_google_pay"),
            InlineKeyboardButton("Crypto", callback_data="crypto"),
        ],
        [
            InlineKeyboardButton("PayPal", callback_data="paypal"),
            InlineKeyboardButton("Go Back", callback_data="go_back"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)

# Other handlers for payments and support
async def apple_google_pay_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    text = (
        "**Apple Pay / Google Pay Payment:**\n\n"
        "Complete your payment using the links below:\n"
        "• **1 MONTH (£6.75):** [Click Here](https://buy.stripe.com/eVa9AE7b23xK036eUW)\n"
        "• **LIFETIME (£10):** [Click Here](https://buy.stripe.com/eVa9AE7b23xK036eUW)\n\n"
        "After payment, your VIP link will be emailed immediately!"
    )
    keyboard = [
        [
            InlineKeyboardButton("I've Paid", callback_data="paid"),
            InlineKeyboardButton("Go Back", callback_data="go_back"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)

async def paid_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    subscription = context.user_data.get("subscription", "Unknown Plan")

    admin_message = (
        f"✅ Payment Notification!\n\n"
        f"👤 User: @{user.username or 'No Username'} (ID: {user.id})\n"
        f"📄 Subscription: {subscription}\n"
    )
    await bot_app.bot.send_message(chat_id=os.getenv("ADMIN_CHAT_ID", 123456789), text=admin_message)

    text = (
        "✅ Thank you for your payment! Please send a screenshot of your transaction or provide the transaction ID "
        "for verification to @zakivip1.\n\n"
        "💬 Need help? Contact @zakivip1."
    )
    keyboard = [[InlineKeyboardButton("Support", callback_data="support")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)

async def go_back_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    await start(update, context)

# Add command and callback handlers
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CallbackQueryHandler(subscription_handler, pattern="^(1_month|lifetime)$"))
bot_app.add_handler(CallbackQueryHandler(apple_google_pay_handler, pattern="^apple_google_pay$"))
bot_app.add_handler(CallbackQueryHandler(paid_handler, pattern="^paid$"))
bot_app.add_handler(CallbackQueryHandler(go_back_handler, pattern="^go_back$"))

def main():
    # Start the Flask app and Telegram bot webhook
    bot_app.run_webhook(
        listen="0.0.0.0",
        port=8443,
        url_path="/webhook",
        webhook_url=WEBHOOK_URL + "/webhook",
    )

    flask_app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    main()