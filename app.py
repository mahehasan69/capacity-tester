import os
import threading
import uvicorn
from dotenv import load_dotenv
from controller.server import app
from bot.telegram_bot import run_bot

load_dotenv()

def run_api():
    uvicorn.run(
        app,
        host=os.getenv("CONTROLLER_HOST", "0.0.0.0"),
        port=int(os.getenv("CONTROLLER_PORT", "8080")),
        log_level="info",
    )

if __name__ == "__main__":
    threading.Thread(target=run_api, daemon=True).start()
    run_bot()
