from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import logging
import traceback

# Telegram bot token
BOT_TOKEN = "7739378344:AAHePCaShSC60pN1VwX9AY4TqD-xZMxQ1gY"

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ],
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Initialize Telegram bot application
try:
    telegram_app = Application.builder().token(BOT_TOKEN).build()
    logger.info("Telegram bot application initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize Telegram bot application: {e}")
    raise

# Define command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /start command."""
    try:
        keyboard = [
            [InlineKeyboardButton("Option 1", callback_data="option1")],
            [InlineKeyboardButton("Option 2", callback_data="option2")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Welcome! Choose an option:", reply_markup=reply_markup)
        logger.info(f"/start command handled successfully for chat ID {update.message.chat_id}.")
    except Exception as e:
        logger.error(f"Error handling /start command: {e}")
        traceback.print_exc()

# Define callback query handler
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles button clicks in the bot."""
    try:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(f"You selected: {query.data}")
        logger.info(f"Button callback handled successfully for data: {query.data}.")
    except Exception as e:
        logger.error(f"Error handling button callback: {e}")
        traceback.print_exc()

# Add handlers to the bot application
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(button_callback))

# Webhook route for Telegram updates
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
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

# Health check route
@app.get("/")
async def root():
    """Basic health check endpoint."""
    logger.info("Health check endpoint hit.")
    return {"message": "Bot is running successfully!"}

# Main entry point
if __name__ == "__main__":
    import uvicorn

    logger.info("Starting bot...")
    try:
        # Start the FastAPI server
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        logger.error(f"Failed to start the FastAPI server: {e}")
        traceback.print_exc()
