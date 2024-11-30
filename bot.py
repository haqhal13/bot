import os
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram import Update

# Replace with your bot token
BOT_TOKEN = "7739378344:AAHePCaShSC60pN1VwX9AY4TqD-xZMxQ1gY"
# Replace with your webhook URL
WEBHOOK_URL = "https://your-deployed-url.com/"

async def start(update: Update, context):
    """Handles the /start command."""
    await update.message.reply_text("Hello! I am your bot, ready to assist!")

async def main():
    """Main function to set up the bot and webhook."""
    # Build the application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add the /start command handler
    app.add_handler(CommandHandler("start", start))

    # Delete any existing webhook to avoid conflicts
    await app.bot.delete_webhook()

    # Run the webhook
    app.run_webhook(
        listen="0.0.0.0",  # Listen on all available IP addresses
        port=int(os.environ.get("PORT", 8443)),  # Use PORT from environment or default to 8443
        url_path=BOT_TOKEN,  # Bot token as the URL path
        webhook_url=f"{WEBHOOK_URL}{BOT_TOKEN}"  # Full webhook URL
    )

# Execute the bot
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())