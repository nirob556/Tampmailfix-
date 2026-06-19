#!/usr/bin/env python3
"""
⚡ SPEED X TempMail Bot
Runs Telegram bot + web status server simultaneously.
"""

import threading, logging, os
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
    app.run(host="0.0.0.0", port=port, use_reloader=False)

def run_bot():
    from bot import main
    print("  🤖  Telegram bot starting…")
    main()

if __name__ == "__main__":
    print(BANNER)
    t = threading.Thread(target=run_web, daemon=True)
    t.start()
    run_bot()
