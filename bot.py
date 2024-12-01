from flask import Flask

# Flask app setup
app = Flask(__name__)

@app.route("/", methods=["GET"])
def uptime_ping():
    """UptimeRobot Ping Endpoint"""
    return "Bot is active!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)