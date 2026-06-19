# ⚡ SPEED X TempMail Bot

Professional disposable email Telegram bot with real-time inbox and web status dashboard.

---

## File Structure

```
tempmail_bot/
├── main.py          ← Run this  (Bot + Web together)
├── bot.py           ← Telegram bot logic
├── web.py           ← Web status dashboard
└── requirements.txt
```

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run everything
python main.py
```

Bot starts polling + web server runs at **http://localhost:8080**

---

## Features

| Feature | Details |
|---|---|
| 📧 TempMail | mail.tm API — 100% working |
| 🔑 Passwords | Always start with `speedx` |
| 📬 Inbox | Real-time message viewing |
| 🔢 OTP Copy | Auto-detect & one-tap copy |
| ⏰ Auto-expire | 10 min lifetime + notifications |
| 🔒 Channel Gate | Must join to use the bot |
| 🌐 Status Page | Live uptime dashboard |

---

## Deploy on Render.com (Free)

1. Push files to a GitHub repo
2. Render → New Web Service → connect repo
3. Settings:
   - Build: `pip install -r requirements.txt`
   - Start: `python main.py`
   - Port: `8080`
4. Your status URL: `https://your-app.onrender.com`

---

## Channel
https://t.me/SPEED_X_OFFICIAL1
