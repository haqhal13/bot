from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import logging
import asyncio

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Your bot token
BOT_TOKEN = "7739378344:AAHePCaShSC60pN1VwX9AY4TqD-xZMxQ1gY"

# Your Stripe Payment Link
STRIPE_PAYMENT_LINK = "https://buy.stripe.com/aEUeUYaneecoeY03cc"

# Webhook URL
WEBHOOK_URL = "https://bot-1-grpp.onrender.com"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command handler to display payment options."""
    keyboard = [
        [InlineKeyboardButton("PayPal", callback_data="paypal")],
        [InlineKeyboardButton("Stripe (Apple Pay/Google Pay)", callback_data="stripe")],
        [InlineKeyboardButton("Crypto", callback_data="crypto")],
        [InlineKeyboardButton("I Paid", callback_data="paid")],
        [InlineKeyboardButton("Go Back", callback_data="go_back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Send £10 using one of the options below:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button clicks."""
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

async def main() -> None:
    # Initialize the bot application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers for the commands and button clicks
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    # Ensure webhook is set correctly
    await app.bot.delete_webhook()  # Clear existing webhook (added await)
    app.run_webhook(
        listen="0.0.0.0",
        port=8000,
        url_path=f"{BOT_TOKEN}",
        webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}"
    )

# Entry point for the script
if __name__ == "__main__":
    asyncio.run(main())