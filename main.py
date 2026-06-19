#!/usr/bin/env python3
"""
SPEED X TempMail Bot — Main Runner
Bot runs first, then Flask starts in a daemon thread.
"""
import threading, logging, asyncio, os

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s  [%(levelname)s]  %(message)s")

BANNER = """
╔══════════════════════════════════════════╗
║   ⚡  SPEED X TempMail Bot               ║
║   Telegram Bot  +  Web Status Server     ║
╠══════════════════════════════════════════╣
║   Channel : t.me/SPEED_X_OFFICIAL1       ║
║   API      : mail.tm                     ║
╚══════════════════════════════════════════╝
"""

def run_web():
    from web import app
    port = int(os.environ.get("PORT", 8080))
    print(f"  🌐  Web server → http://0.0.0.0:{port}")
    # Create a new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app.run(host="0.0.0.0", port=port, use_reloader=False, threaded=True)

if __name__ == "__main__":
    print(BANNER)

    # Start web in background thread FIRST
    t = threading.Thread(target=run_web, daemon=True)
    t.start()

    # Bot runs in main thread with its own event loop
    print("  🤖  Telegram bot starting…")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    from bot import main
    main()
