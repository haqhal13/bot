from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Bot
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = 'YOUR_BOT_TOKEN'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Introductory Message
    intro_text = (
        "👋 Welcome to the BADDIES FACTORY VIP Bot!\n\n"
        "💎 Get access to exclusive VIP content instantly with a growing collection every day. "
        "If we don't have it, we will add it within 24-72 hours!\n\n"
        "Select your subscription plan below or contact support for assistance."
    )
    keyboard = [
        [InlineKeyboardButton("1 MONTH (£6.75)", callback_data="1_month"),
         InlineKeyboardButton("LIFETIME (£10)", callback_data="lifetime")],
        [InlineKeyboardButton("Support", callback_data="support")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(intro_text, reply_markup=reply_markup)

async def subscription_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data in ["1_month", "lifetime"]:
        # Plan-specific message
        text = (
            f"📄 You selected the **{query.data.replace('_', ' ').upper()}** plan.\n\n"
            "Choose your preferred payment method below:\n"
            "💳 **Stripe (Apple Pay/Google Pay):** Instant VIP access (link emailed immediately).\n"
            "⚡ **Crypto:** Wait for a VIP link to be manually sent.\n"
            "📧 **PayPal:** Wait for a VIP link to be manually sent."
        )
        keyboard = [
            [InlineKeyboardButton("Stripe (Instant Access)", callback_data="stripe"),
             InlineKeyboardButton("Crypto", callback_data="crypto")],
            [InlineKeyboardButton("PayPal", callback_data="paypal"),
             InlineKeyboardButton("Go Back", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=text, reply_markup=reply_markup)

    elif query.data == "support":
        # Support Message
        text = (
            "💬 Support:\n"
            "For any issues, contact @zakivip1.\n"
            "Available from 8:00 AM to 12:00 AM BST."
        )
        keyboard = [[InlineKeyboardButton("Go Back", callback_data="start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=text, reply_markup=reply_markup)

async def payment_method_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "stripe":
        text = (
            "💳 **Stripe Payment** (Instant Access):\n"
            "Pay via Stripe (Apple Pay/Google Pay). A VIP link will be emailed to you instantly.\n\n"
            "📱 [Pay Now via Mini App](https://your-stripe-mini-app-link.com)"
        )
    elif query.data == "crypto":
        text = (
            "⚡ **Crypto Payment:**\n"
            "Send your payment to the following address:\n\n"
            "🔗 **Ethereum:** 0x9ebeBd89395CaD9C29Ee0B5fC614E6f307d7Ca82\n\n"
            "💰 **Prices:**\n"
            "• $8 Monthly\n"
            "• $15 Lifetime\n\n"
            "After payment, click 'I've Paid' and provide the transaction details. "
            "Wait for a VIP link to be manually sent."
        )
    elif query.data == "paypal":
        text = (
            "➡️Send £6.75 for 1 MONTH or £10 for LIFETIME To\n"
            "➡️Paypal: onlyvipfan@outlook.com\n"
            "✅MUST BE FRIENDS AND FAMILY\n"
            "✅IF YOU DON'T HAVE FAMILY AND FRIENDS USE CARD/CRYPTO\n"
            "❌DONT LEAVE A NOTE\n"
            "➡️CLICK I PAID\n"
            "✅SEND PAYMENT SCREENSHOT TO @zakivip1 AND PROVIDE YOUR FULL PAYPAL NAME"
        )
    keyboard = [
        [InlineKeyboardButton("I've Paid", callback_data="paid"),
         InlineKeyboardButton("Go Back", callback_data="1_month")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)

async def paid_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    text = (
        "✅ Thank you for your payment! Please upload a screenshot of your transaction "
        "or provide the transaction ID for verification.\n\n"
        "💬 Need help? Contact @zakivip1."
    )
    keyboard = [[InlineKeyboardButton("Support", callback_data="support")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)

async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await start(query, context)

def main() -> None:
    app = Application.builder().token(TOKEN).build()

    # Command Handlers
    app.add_handler(CommandHandler("start", start))

    # Callback Query Handlers
    app.add_handler(CallbackQueryHandler(subscription_handler, pattern="^(1_month|lifetime|support)$"))
    app.add_handler(CallbackQueryHandler(payment_method_handler, pattern="^(stripe|crypto|paypal)$"))
    app.add_handler(CallbackQueryHandler(paid_handler, pattern="^paid$"))
    app.add_handler(CallbackQueryHandler(go_back, pattern="^start$"))

    # Run the bot
    app.run_polling()

if __name__ == "__main__":
    main()