import os
from telegram.ext import ApplicationBuilder, CommandHandler

# Your bot token
BOT_TOKEN = "7739378344:AAHePCaShSC60pN1VwX9AY4TqD-xZMxQ1gY"
WEBHOOK_URL = "https://your-deployed-url.com"  # Replace with your deployment URL

async def start(update, context):
    """Handles the /start command."""
    await update.message.reply_text("Hello! I am your bot, ready to assist!")

if __name__ == "__main__":
    # Create the bot application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add the /start command handler
    app.add_handler(CommandHandler("start", start))

    # Delete any existing webhook to avoid conflicts
    app.bot.delete_webhook()

    # Start the webhook
    app.run_webhook(
        listen="0.0.0.0",  # Listen on all network interfaces
        port=int(os.environ.get("PORT", 8443)),  # Use PORT environment variable or default to 8443
        webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}"  # Webhook endpoint
    )