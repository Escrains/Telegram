import csv
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("BOT_TOKEN")
ARCHIVO = "contactos.csv"

# Guardar contactos
async def guardar_contacto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contacto = update.message.contact
    if contacto:
        nombre = contacto.first_name or ""
        apellido = contacto.last_name or ""
        numero = contacto.phone_number or ""
        comentario = " ".join(context.args) if context.args else ""
        
        with open(ARCHIVO, "a", newline='', encoding='utf-8') as archivo_csv:
            writer = csv.writer(archivo_csv)
            writer.writerow([nombre, apellido, numero, comentario])

        await update.message.reply_text("✅ Contacto guardado.")

# Ver todos los contactos como archivo
async def ver_contactos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if os.path.exists(ARCHIVO):
        await update.message.reply_document(document=open(ARCHIVO, "rb"), filename="contactos.csv")
    else:
        await update.message.reply_text("📂 Aún no hay contactos guardados.")

# Buscar contacto por número
async def buscar_contacto_por_numero(update: Update, context: ContextTypes.DEFAULT_TYPE):
    numero_consulta = update.message.text.strip()

    if not numero_consulta.startswith("+") and not numero_consulta.isdigit():
        return

    if os.path.exists(ARCHIVO):
        with open(ARCHIVO, newline='', encoding='utf-8') as archivo_csv:
            reader = csv.reader(archivo_csv)
            for fila in reader:
                if len(fila) >= 3 and numero_consulta in fila[2]:
                    nombre = fila[0]
                    apellido = fila[1]
                    comentario = fila[3] if len(fila) > 3 else "Sin comentario"
                    mensaje = f"👤 *Nombre:* {nombre} {apellido}\n📞 *Número:* {fila[2]}\n📝 *Comentario:* {comentario}"
                    await update.message.reply_markdown(mensaje)
                    return
        await update.message.reply_text("❌ Número no encontrado.")
    else:
        await update.message.reply_text("❌ No hay contactos registrados.")

# Ayuda
async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 *Bot de Contactos*\n\n"
        "📥 Envía un contacto para guardarlo\n"
        "🔎 Envía un número para consultar su comentario\n"
        "📄 /ver_contactos para descargar la lista\n",
        parse_mode='Markdown'
    )

# Ejecutar bot
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.CONTACT, guardar_contacto))
app.add_handler(CommandHandler("ver_contactos", ver_contactos))
app.add_handler(CommandHandler("start", ayuda))
app.add_handler(CommandHandler("ayuda", ayuda))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), buscar_contacto_por_numero))

print("🤖 Bot activo...")
app.run_polling()
