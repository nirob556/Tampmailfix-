import asyncio, logging, random, string, time, re
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN        = "8446272435:AAH18fvcHjo5w92_zFZdkRY9_KkF9Kvcq2o"
CHANNEL_USERNAME = "SPEED_X_OFFICIAL1"
CHANNEL_LINK     = "https://t.me/SPEED_X_OFFICIAL1"
MAIL_EXPIRE_MIN  = 10
BASE_URL         = "https://api.mail.tm"

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
user_sessions: dict = {}

# ══════════════════════════════════════════════════════
# MAIL.TM API
# ══════════════════════════════════════════════════════

async def api_get_domains():
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get(f"{BASE_URL}/domains"); r.raise_for_status()
        return [d["domain"] for d in r.json().get("hydra:member", [])]

async def api_create_account(email, pw):
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.post(f"{BASE_URL}/accounts", json={"address": email, "password": pw})
        r.raise_for_status(); return r.json()

async def api_get_token(email, pw):
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.post(f"{BASE_URL}/token", json={"address": email, "password": pw})
        r.raise_for_status(); return r.json()["token"]

async def api_get_messages(token):
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get(f"{BASE_URL}/messages", headers={"Authorization": f"Bearer {token}"})
        r.raise_for_status(); return r.json().get("hydra:member", [])

async def api_get_message(token, mid):
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get(f"{BASE_URL}/messages/{mid}", headers={"Authorization": f"Bearer {token}"})
        r.raise_for_status(); return r.json()

# ══════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════

def gen_password():
    pool = string.ascii_letters + string.digits + "!@#$%^&*"
    return "speedx" + "".join(random.choices(pool, k=8))

def gen_username():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=9))

def time_left(created_at):
    rem = MAIL_EXPIRE_MIN * 60 - (time.time() - created_at)
    if rem <= 0: return "⛔  Expired"
    m, s = divmod(int(rem), 60)
    filled = int((rem / (MAIL_EXPIRE_MIN * 60)) * 10)
    bar = "█" * filled + "░" * (10 - filled)
    return f"[{bar}]  {m}m {s}s remaining"

def is_expired(created_at):
    return (time.time() - created_at) >= MAIL_EXPIRE_MIN * 60

async def is_member(bot, user_id):
    try:
        m = await bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return m.status in ("member", "administrator", "creator")
    except Exception:
        return False

def kb_home(user_id):
    has = user_id in user_sessions
    rows = []
    if has:
        rows += [
            [InlineKeyboardButton("📋  View My Email",      callback_data="show_email")],
            [InlineKeyboardButton("📬  Check Inbox",        callback_data="inbox"),
             InlineKeyboardButton("🔄  New Email",          callback_data="new_email")],
        ]
    else:
        rows += [[InlineKeyboardButton("✨  Generate New Email", callback_data="new_email")]]
    rows += [[InlineKeyboardButton("📢  Our Channel", url=CHANNEL_LINK),
              InlineKeyboardButton("❓  Help",         callback_data="help")]]
    return InlineKeyboardMarkup(rows)

def kb_inbox(messages):
    rows = []
    for msg in messages[:8]:
        subj   = (msg.get("subject") or "No Subject")[:30]
        sender = msg.get("from", {}).get("address", "unknown")[:20]
        rows.append([InlineKeyboardButton(
            f"✉️  {subj}  ·  {sender}", callback_data=f"msg_{msg['id']}"
        )])
    rows += [[InlineKeyboardButton("🔄  Refresh", callback_data="inbox"),
              InlineKeyboardButton("🏠  Home",    callback_data="home")]]
    return InlineKeyboardMarkup(rows)

# ══════════════════════════════════════════════════════
# HANDLERS
# ══════════════════════════════════════════════════════

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not await is_member(ctx.bot, user.id):
        await update.message.reply_text(
            f"👋  *Welcome, {user.first_name}!*\n\n"
            "🔒  Join our channel to use this bot.\n\n"
            f"➡️  {CHANNEL_LINK}\n\n"
            "After joining tap *I've Joined* 👇",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢  Join Channel", url=CHANNEL_LINK)],
                [InlineKeyboardButton("✅  I've Joined",  callback_data="verify_join")],
            ])
        )
        return
    await send_home(update.message, user.id)

async def send_home(msg, user_id, edit=False):
    sess = user_sessions.get(user_id)
    if sess and is_expired(sess["created_at"]):
        del user_sessions[user_id]; sess = None
    status = ""
    if sess:
        tl = time_left(sess["created_at"])
        status = f"\n┌────────────────────────\n│  📧  `{sess['email']}`\n│  ⏱️  {tl}\n└────────────────────────\n"
    text = (
        "⚡  *SPEED X TempMail Bot*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{status}"
        "Disposable emails, instant OTP copy.\n\n"
        "Use the buttons below 👇"
    )
    if edit:
        return text, kb_home(user_id)
    await msg.reply_text(text, parse_mode="Markdown", reply_markup=kb_home(user_id))

async def on_button(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user = q.from_user
    data = q.data

    if data == "verify_join":
        if not await is_member(ctx.bot, user.id):
            await q.answer("⚠️  Not joined yet!", show_alert=True); return
        await q.message.delete()
        await send_home(q.message, user.id); return

    if not await is_member(ctx.bot, user.id):
        await q.answer("🔒  Join our channel first!", show_alert=True); return

    if data == "home":
        txt, kb = await send_home(q.message, user.id, edit=True)
        await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=kb); return

    if data == "new_email":
        await q.edit_message_text("⏳  *Generating your email…*", parse_mode="Markdown")
        try:
            domains = await api_get_domains()
            if not domains: raise RuntimeError("No domains")
            email = f"{gen_username()}@{random.choice(domains)}"
            pw    = gen_password()
            await api_create_account(email, pw)
            token = await api_get_token(email, pw)
            user_sessions[user.id] = {"email": email, "password": pw,
                                       "token": token, "created_at": time.time()}
            asyncio.create_task(expiry_watcher(ctx.bot, user.id, email))
            tl = time_left(user_sessions[user.id]["created_at"])
            await q.edit_message_text(
                "✅  *Email Created!*\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "📧  *Address*\n"
                f"`{email}`\n\n"
                "🔑  *Password*\n"
                f"`{pw}`\n\n"
                f"⏱️  {tl}\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "_Tap to copy_",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📬  Check Inbox",  callback_data="inbox")],
                    [InlineKeyboardButton("🔄  Regenerate",   callback_data="new_email"),
                     InlineKeyboardButton("🏠  Home",         callback_data="home")],
                ])
            )
        except Exception as e:
            logger.error(f"Email error: {e}")
            await q.edit_message_text(
                "❌  *Failed. Try again.*", parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔄  Retry", callback_data="new_email")
                ]]))
        return

    if data == "show_email":
        sess = user_sessions.get(user.id)
        if not sess: await q.answer("❌  No active email!", show_alert=True); return
        if is_expired(sess["created_at"]):
            del user_sessions[user.id]
            await q.answer("⛔  Expired. Generate new.", show_alert=True); return
        tl = time_left(sess["created_at"])
        await q.edit_message_text(
            "📧  *Your Active Email*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📬  *Address*\n`{sess['email']}`\n\n"
            f"🔑  *Password*\n`{sess['password']}`\n\n"
            f"⏱️  {tl}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n_Tap to copy_",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📬  Inbox",  callback_data="inbox"),
                 InlineKeyboardButton("🔄  New",    callback_data="new_email")],
                [InlineKeyboardButton("🏠  Home",   callback_data="home")],
            ])
        ); return

    if data == "inbox":
        sess = user_sessions.get(user.id)
        if not sess: await q.answer("❌  Generate an email first!", show_alert=True); return
        if is_expired(sess["created_at"]):
            del user_sessions[user.id]
            await q.answer("⛔  Expired.", show_alert=True); return
        await q.edit_message_text("📬  *Loading inbox…*", parse_mode="Markdown")
        try:
            msgs = await api_get_messages(sess["token"])
            tl   = time_left(sess["created_at"])
            if not msgs:
                await q.edit_message_text(
                    "📭  *Inbox Empty*\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"📧  `{sess['email']}`\n⏱️  {tl}\n\n_No messages yet._",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔄  Refresh", callback_data="inbox"),
                         InlineKeyboardButton("🏠  Home",    callback_data="home")],
                    ])
                )
            else:
                await q.edit_message_text(
                    f"📬  *Inbox  ·  {len(msgs)} message{'s' if len(msgs)>1 else ''}*\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"📧  `{sess['email']}`\n⏱️  {tl}\n\nTap to read 👇",
                    parse_mode="Markdown", reply_markup=kb_inbox(msgs)
                )
        except Exception as e:
            logger.error(f"Inbox error: {e}")
            await q.edit_message_text("❌  *Failed to load inbox.*", parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔄  Retry", callback_data="inbox")
                ]]))
        return

    if data.startswith("msg_"):
        mid  = data[4:]
        sess = user_sessions.get(user.id)
        if not sess: await q.answer("⛔  Session expired!", show_alert=True); return
        await q.edit_message_text("📩  *Opening…*", parse_mode="Markdown")
        try:
            d       = await api_get_message(sess["token"], mid)
            sender  = d.get("from", {}).get("address", "unknown")
            subject = d.get("subject", "No Subject")
            body    = d.get("text") or ""
            if isinstance(body, list): body = "\n".join(body)
            body  = body.strip()[:1800] + ("…" if len(body) > 1800 else "")
            codes = list(dict.fromkeys(re.findall(r'\b\d{4,8}\b', body)))
            text  = (
                "📩  *Message*\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤  *From:*  `{sender}`\n"
                f"📌  *Subject:*  {subject}\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"{body or '_No content_'}"
            )
            if codes:
                text += "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n🔢  *Codes / OTPs detected:*"
            buttons = [[InlineKeyboardButton(f"📋  Copy: {c}", callback_data=f"copy_{c}")] for c in codes[:6]]
            buttons.append([InlineKeyboardButton("◀️  Inbox", callback_data="inbox"),
                             InlineKeyboardButton("🏠  Home",  callback_data="home")])
            await q.edit_message_text(text, parse_mode="Markdown",
                                       reply_markup=InlineKeyboardMarkup(buttons))
        except Exception as e:
            logger.error(f"Msg error: {e}")
            await q.edit_message_text("❌  *Failed to load message.*", parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("◀️  Inbox", callback_data="inbox"),
                    InlineKeyboardButton("🏠  Home",  callback_data="home"),
                ]]))
        return

    if data.startswith("copy_"):
        code = data[5:]
        await q.answer(f"✅  Copied: {code}", show_alert=False)
        await ctx.bot.send_message(user.id,
            f"📋  *Copied Code*\n\n`{code}`\n\n_Tap the code above to copy._",
            parse_mode="Markdown")
        return

    if data == "help":
        await q.edit_message_text(
            "❓  *Help Guide*\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "✨  *Generate Email* — Disposable address + password\n\n"
            "📬  *Check Inbox* — Real-time incoming emails\n\n"
            "📋  *Copy Code* — OTPs auto-detected, one-tap copy\n\n"
            f"⏱️  *Expiry* — {MAIL_EXPIRE_MIN} min lifetime, 1 min warning\n\n"
            "🔑  *Password* — Always starts with `speedx`\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠  Home", callback_data="home")
            ]])
        ); return

# ══════════════════════════════════════════════════════
# EXPIRY WATCHER
# ══════════════════════════════════════════════════════

async def expiry_watcher(bot, user_id, email):
    await asyncio.sleep(MAIL_EXPIRE_MIN * 60 - 60)
    sess = user_sessions.get(user_id)
    if sess and sess["email"] == email:
        try:
            await bot.send_message(user_id,
                f"⚠️  *1 Minute Warning!*\n\n`{email}` expires in 1 minute.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔄  Generate New", callback_data="new_email")
                ]]))
        except Exception: pass
    await asyncio.sleep(60)
    sess = user_sessions.get(user_id)
    if sess and sess["email"] == email:
        del user_sessions[user_id]
        try:
            await bot.send_message(user_id,
                f"⛔  *Email Expired*\n\n`{email}` has been deleted.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("✨  Generate New", callback_data="new_email")
                ]]))
        except Exception: pass

# ══════════════════════════════════════════════════════
# MAIN — asyncio.run() instead of app.run_polling()
# ══════════════════════════════════════════════════════

async def async_main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(on_button))
    logger.info("⚡ SPEED X TempMail Bot running")
    async with app:
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        # Keep running forever
        await asyncio.Event().wait()

def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
