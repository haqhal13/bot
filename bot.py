# Initialize Telegram bot application globally
telegram_app = None  # Declare it globally for use across the script

# Webhook route
@app.post("/webhook")
async def webhook(request: Request):
    try:
        update = Update.de_json(await request.json(), telegram_app.bot)
        # Ensure the application is initialized before processing updates
        if not telegram_app:
            logger.error("Telegram Application is not initialized!")
            return {"status": "error", "message": "Telegram Application not initialized"}

        await telegram_app.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return {"status": "error", "message": str(e)}

# Webhook setup during startup
@app.on_event("startup")
async def on_startup():
    global telegram_app  # Use the global application instance
    try:
        # Initialize the Telegram bot application
        telegram_app = Application.builder().token(BOT_TOKEN).build()

        # Delete any existing webhook
        delete_response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
        if delete_response.status_code == 200:
            logger.info("Deleted previous webhook successfully.")
        else:
            logger.warning(f"Failed to delete webhook: {delete_response.text}")

        # Set up a new webhook
        set_response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={WEBHOOK_URL}")
        if set_response.status_code == 200:
            logger.info("Webhook set successfully.")
        else:
            logger.error(f"Failed to set webhook: {set_response.text}")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error during webhook setup: {e}")
        sys.exit(1)
