import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

# Replace with your bot token
BOT_TOKEN = "7739378344:AAHePCaShSC60pN1VwX9AY4TqD-xZMxQ1gY"

# Replace with your Render URL
WEBHOOK_URL = f"https://bot-1-f2wh.onrender.com/{BOT_TOKEN}"

async def start(update: Update, context):
    """Handles the /start command."""
    await update.message.reply_text("Hello! I am your bot. How can I help you?")

async def payment_menu(update: Update, context):
    """Displays payment options."""
    keyboard = [
        [InlineKeyboardButton("PayPal", callback_data="paypal")],
        [InlineKeyboardButton("Stripe (Apple Pay/Google Pay)", callback_data="stripe")],
        [InlineKeyboardButton("Crypto", callback_data="crypto")],
        [InlineKeyboardButton("I Paid", callback_data="paid")],
        [InlineKeyboardButton("Go Back", callback_data="go_back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose your payment option:", reply_markup=reply_markup)

async def button_handler(update: Update, context):
    """Handles button interactions."""
    query = update.callback_query
    await query.answer()
    if query.data == "paypal":
        await query.edit_message_text("Pay via PayPal: your_paypal@example.com")
    elif query.data == "stripe":
        await query.edit_message_text("Pay via Stripe: [Stripe Payment Link](https://stripe.com)", parse_mode="Markdown")
    elif query.data == "crypto":
        await query.edit_message_text("Pay via Crypto: Bitcoin Address: 1ExampleAddress")
    elif query.data == "paid":
        await query.edit_message_text("Thank you for your payment! We'll verify it shortly.")
    elif query.data == "go_back":
        await payment_menu(update, context)

if __name__ == "__main__":
    # Initialize the bot application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add handlers for commands and buttons
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("pay", payment_menu))
    app.add_handler(CallbackQueryHandler(button_handler))

    # Start the webhook
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        webhook_url=WEBHOOK_URL,
    )