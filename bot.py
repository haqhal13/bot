from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import logging
import asyncio

# Telegram bot token
BOT_TOKEN = "7739378344:AAHePCaShSC60pN1VwX9AY4TqD-xZMxQ1gY"

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Telegram bot application
telegram_app = Application.builder().token(BOT_TOKEN).build()

# Proper initialization of the application
async def initialize_telegram_app():
    await telegram_app.initialize()
    logger.info("Telegram application initialized.")

# Add handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /start command."""
    keyboard = [
        [InlineKeyboardButton("Option 1", callback_data="option1")],
        [InlineKeyboardButton("Option 2", callback_data="option2")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome! Choose an option:", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles button clicks in the bot."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(f"You selected: {query.data}")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(button_callback))

# Webhook route
@app.post("/webhook")
async def webhook(request: Request):
    """Handles Telegram webhook updates."""
    try:
        data = await request.json()
        update = Update.de_json(data, telegram_app.bot)
        logger.info(f"Received update: {data}")
        await telegram_app.process_update(update)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error handling webhook request: {e}")
        return {"status": "error", "message": str(e)}

# Health check route
@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Bot is running!"}

# Main entry point
if __name__ == "__main__":
    import uvicorn
    import threading

    async def start_app():
        await initialize_telegram_app()
        # Set the webhook for Telegram
        await telegram_app.bot.set_webhook(url="https://bot-1-f2wh.onrender.com/webhook")
        logger.info("Webhook set successfully.")

    # Initialize the Telegram application in a separate thread to ensure FastAPI starts independently
    threading.Thread(target=lambda: asyncio.run(start_app())).start()

    # Start FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        logger.error(f"Failed to start the FastAPI server: {e}")
        traceback.print_exc()
