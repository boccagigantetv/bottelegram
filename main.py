from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import logging

BOT_TOKEN = '7922315761:AAEGR4WFgjqL-TZyHsj3uOF7YT7q2yxzrps'
OPERATOR_IDS = [6978911275, 000000000]  # Inserisci qui gli ID Telegram degli operatori

# Mappa utente → in contatto
active_contacts = {}

logging.basicConfig(level=logging.INFO)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Benvenuto! Usa /contact per parlare con un operatore.")

# /contact
async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    active_contacts[user_id] = True
    await update.message.reply_text("Aspetta... un operatore ti contatterà attraverso il bot a breve.")

    # Notifica a ogni operatore
    for op_id in OPERATOR_IDS:
        try:
            await context.bot.send_message(
                chat_id=op_id,
                text=f"📞 L'utente @{update.effective_user.username or user_id} ha richiesto supporto. Usa /msg {user_id} <testo> per rispondere."
            )
        except:
            logging.warning(f"Impossibile inviare messaggio a {op_id}")

# /msg <user_id> <messaggio>
async def msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender_id = update.effective_user.id
    if sender_id not in OPERATOR_IDS:
        await update.message.reply_text("🚫 Accesso negato. Solo gli operatori possono usare questo comando.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Formato: /msg <user_id> <messaggio>")
        return

    try:
        user_id = int(context.args[0])
        message = ' '.join(context.args[1:])
        if user_id in active_contacts:
            await context.bot.send_message(chat_id=user_id, text=f"💬 Operatore: {message}")
            await update.message.reply_text("✅ Messaggio inviato.")
        else:
            await update.message.reply_text("⚠️ Questo utente non ha richiesto supporto.")
    except Exception as e:
        await update.message.reply_text("Errore nell'invio del messaggio.")
        logging.error(e)

# /stop
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in active_contacts:
        del active_contacts[user_id]
        await update.message.reply_text("✅ Hai interrotto il contatto con l'operatore.")
    else:
        await update.message.reply_text("Non sei in contatto con nessun operatore.")

# /info
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    testo = ("🤖 Il Bot Ufficiale del Partito Fratellanza Italiana, tramite questo bot puoi metterti in contatto "
             "con gli operatori o conoscere meglio il partito e come contribuire.")
    await update.message.reply_text(testo)

# /socials
async def socials(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = "https://tiktok.com/@pfi001corp"
    await update.message.reply_text(f"Seguici su TikTok: {link}")

# Avvio bot
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("contact", contact))
    app.add_handler(CommandHandler("msg", msg))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("socials", socials))
    app.run_polling()

if __name__ == "__main__":
    main()
