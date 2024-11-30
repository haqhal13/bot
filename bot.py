from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import logging

# Telegram Bot Token and Admin Chat ID
TOKEN = '7739378344:AAHePCaShSC60pN1VwX9AY4TqD-xZMxQ1gY'
ADMIN_CHAT_ID = "834523364"  # Replace with your Telegram numeric ID

# Webhook URL
WEBHOOK_URL = "https://bot-1-f2wh.onrender.com"

# Initialize Flask app
app = Flask(__name__)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Initialize the bot
bot_app = Application.builder().token(TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command and show subscription options."""
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


async def subscription_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle subscription selection and show payment options."""
    query = update.callback_query
    await query.answer()

    # Store the selected subscription plan
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


async def apple_google_pay_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle Apple Pay/Google Pay selection."""
    query = update.callback_query
    await query.answer()

    text = (
        "**Apple Pay / Google Pay Payment:**\n\n"
        "Complete your payment using the links below:\n\n"
        "• **1 MONTH (£6.75):** [Click Here](https://buy.stripe.com/eVa9AE7b23xK036eUW)\n"
        "• **LIFETIME (£10):** [Click Here](https://buy.stripe.com/eVa9AE7b23xK036eUW)\n\n"
        "After payment, your VIP link will be emailed immediately!"
    )
    keyboard = [
        [InlineKeyboardButton("I've Paid", callback_data="paid"),
         InlineKeyboardButton("Go Back", callback_data="go_back_subscription")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)


async def crypto_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle crypto payment selection."""
    query = update.callback_query
    await query.answer()

    text = (
        "⚡ **Crypto Payment:**\n"
        "Send your payment to the following address:\n\n"
        "🔗 **Ethereum:** 0x9ebeBd89395CaD9C29Ee0B5fC614E6f307d7Ca82\n\n"
        "💰 **Prices:**\n"
        "• $8 Monthly\n"
        "• $15 Lifetime\n\n"
        "After payment, click 'I've Paid' and provide the transaction details. "
        "Your VIP link will be sent within 30 minutes during BST hours."
    )
    keyboard = [
        [InlineKeyboardButton("I've Paid", callback_data="paid"),
         InlineKeyboardButton("Go Back", callback_data="go_back_subscription")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)


async def paypal_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle PayPal payment selection."""
    query = update.callback_query
    await query.answer()

    text = (
        "➡️Send £6.75 for 1 MONTH or £10 for LIFETIME To\n"
        "➡️Paypal: onlyvipfan@outlook.com\n"
        "✅MUST BE FRIENDS AND FAMILY\n"
        "✅IF YOU DON'T HAVE FAMILY AND FRIENDS USE CARD/CRYPTO\n"
        "❌DONT LEAVE A NOTE\n"
        "➡️CLICK I PAID\n"
        "✅SEND PAYMENT SCREENSHOT TO @zakivip1 AND PROVIDE YOUR FULL PAYPAL NAME\n\n"
        "Your VIP link will be sent within 30 minutes during BST hours."
    )
    keyboard = [
        [InlineKeyboardButton("I've Paid", callback_data="paid"),
         InlineKeyboardButton("Go Back", callback_data="go_back_subscription")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)


async def paid_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle 'I've Paid' button clicks and notify admin."""
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    subscription = context.user_data.get("subscription", "Unknown Plan")
    admin_message = (
        f"✅ Payment Notification!\n\n"
        f"👤 User: @{user.username or 'No Username'} (ID: {user.id})\n"
        f"📄 Subscription: {subscription}\n"
    )

    # Notify the admin
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_message)

    # Notify the user
    text = (
        "✅ Thank you for your payment! Please send a screenshot of your transaction "
        "or provide the transaction ID for verification to @zakivip1.\n\n"
        "💬 Need help? Contact @zakivip1."
    )
    keyboard = [[InlineKeyboardButton("Support", callback_data="support")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)


async def support_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle support button clicks."""
    text = (
        "💬 Support:\n"
        "For any issues, contact @zakivip1.\n"
        "Available from 8:00 AM to 12:00 AM BST."
    )
    keyboard = [[InlineKeyboardButton("Go Back", callback_data="go_back_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)


async def go_back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle go back button clicks."""
    query = update.callback_query
    await query.answer()

    if query.data == "go_back_main":
        await start(update, context)
    elif query.data == "go_back_subscription":
        await subscription_handler(update, context)


# Set up Telegram bot handlers
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CallbackQueryHandler(subscription_handler, pattern="^(1_month|lifetime)$"))
bot_app.add_handler(CallbackQueryHandler(apple_google_pay_handler, pattern="^apple_google_pay$"))
bot_app.add_handler(CallbackQueryHandler(crypto_handler, pattern="^crypto$"))
bot_app.add_handler(CallbackQueryHandler(paypal_handler, pattern="^paypal$"))
bot_app.add_handler(CallbackQueryHandler(paid_handler, pattern="^paid$"))
bot_app.add_handler(CallbackQueryHandler(support_handler, pattern="^support$"))
bot_app.add_handler(CallbackQueryHandler(go_back_handler, pattern="^go_back_.*$"))


@app.route("/", methods=["GET", "POST"])
def webhook() -> str:
    """Webhook endpoint for Telegram updates."""
    if request.method == "POST":
        bot_app.update_queue.put(request.get_json())
        return "ok", 200
    return "Bot is running!"


if __name__ == "__main__":
    bot_app.run_webhook(
        listen="0.0.0.0",
        port=10000,  # Render detects the open port automatically
        url_path="",  # The bot webhook path
        webhook_url=WEBHOOK_URL
    )