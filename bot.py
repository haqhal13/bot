from flask import Flask

# Flask app setup
app = Flask(__name__)

@app.route("/", methods=["GET"])
def uptime_home():
    """Root route to confirm the bot is live."""
    return "Bot is active at root!", 200

@app.route("/ping", methods=["GET", "HEAD"])
def uptime_ping():
    """UptimeRobot Ping Endpoint"""
    return "Bot is active at ping!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)