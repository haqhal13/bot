import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Your bot token
BOT_TOKEN = "7739378344:AAHePCaShSC60pN1VwX9AY4TqD-xZMxQ1gY"
WEBHOOK_URL = "https://bot-1-f2wh.onrender.com"  # Replace with your Render app URL

# Stripe Payment Link
STRIPE_PAYMENT_LINK = "https://buy.stripe.com/aEUeUYaneecoeY03cc"

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("PayPal", callback_data="paypal")],
        [InlineKeyboardButton("Stripe (Apple Pay/Google Pay)", callback_data="stripe")],
        [InlineKeyboardButton("Crypto", callback_data="crypto")],
        [InlineKeyboardButton("I Paid", callback_data="paid")],
        [InlineKeyboardButton("Go Back", callback_data="go_back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Send £10 using one of the options below:", reply_markup=reply_markup)

# Button callback handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "paypal":
        await query.edit_message_text(
            text=(
                "➡️Send £10 / $13.5 To\n"
                "➡️PayPal: onlyvipfan@outlook.com\n"
                "✅MUST BE FRIENDS AND FAMILY\n"
                "✅IF YOU DON'T HAVE FAMILY AND FRIENDS, USE CARD/CRYPTO\n"
                "❌DONT LEAVE A NOTE\n"
                "➡️CLICK I PAID\n"
                "✅SEND PAYMENT SCREENSHOT TO @ZAKIVIP1 AND PROVIDE YOUR FULL PAYPAL NAME"
            )
        )
    elif query.data == "stripe":
        await query.edit_message_text(
            text=(
                "Click the button below to complete payment via Stripe:\n\n"
                f"[Pay Now with Stripe]({STRIPE_PAYMENT_LINK})"
            ),
            parse_mode="Markdown",
        )
    elif query.data == "crypto":
        await query.edit_message_text(
            text=(
                "➡️Send $14 in Crypto:\n\n"
                "Bitcoin: `1ExampleBTCAddress`\n"
                "Ethereum: `0xExampleETHAddress`\n\n"
                "➡️Click I Paid after completing the payment.\n"
                "✅SEND PAYMENT SCREENSHOT TO @ZAKIVIP1"
            ),
            parse_mode="Markdown",
        )
    elif query.data == "paid":
        await query.edit_message_text(
            text="Thank you for your payment! Your access will be verified shortly."
        )
    elif query.data == "go_back":
        await start(update, context)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    # Start the webhook
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}"
    )