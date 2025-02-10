import logging
import sqlite3
import argparse
import random
from telegram import Update

from telegram.ext import (
    ApplicationBuilder, ContextTypes, CommandHandler, filters,
    MessageHandler, TypeHandler , ApplicationHandlerStop,
    JobQueue)

import os

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# Inizializza il database SQLite
def init_db(db):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS session (
            id TEXT PRIMARY KEY,
            active INTEGER DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            session_id TEXT,
            user TEXT,
            plate INTEGER,
            quantity INTEGER,
            PRIMARY KEY (session_id, user, plate),
            FOREIGN KEY (session_id) REFERENCES session(id)
        )
    """)

    print('test')

    conn.commit()
    conn.close()

async def new_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session_id = str(random.randint(10000, 99999))

    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO session (id) VALUES (?)", (session_id,))
    conn.commit()
    conn.close()

    await update.message.reply_text(f"New session created! Session ID: {session_id}")

async def new_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.split()

    if len(msg) != 2 or not msg[0].isdigit() or not msg[1].isdigit():
        await update.message.reply_text("Wrong fromat! Use: 'plate_number quantity'.")
        return

    plate, quantity = map(int, msg)
    user = update.message.from_user.username

    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM session WHERE active = 1 ORDER BY id DESC LIMIT 1")
    session = cursor.fetchone()
    if not session:
        await update.message.reply_text("No active sessione. Wait for a new session")
        conn.close()
        return

    session_id = session[0]
    cursor.execute("""
        INSERT INTO orders (session_id, user, plate, quantity)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(session_id, user, plate) DO UPDATE SET quantity = quantity + ?
    """, (session_id, user, plate, quantity, quantity))

    conn.commit()
    conn.close()

    await update.message.reply_text(f"Order saved for plate n. {plate}")

async def close_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM session WHERE active = 1 ORDER BY id DESC LIMIT 1")
    session = cursor.fetchone()

    if not session:
        await update.message.reply_text("No Active session")
        conn.close()
        return

    session_id = session[0]
    cursor.execute("UPDATE session SET active = 0 WHERE id = ?", (session_id,))

    cursor.execute("""
        SELECT plate, SUM(quantity) FROM orders
        WHERE session_id = ?
        GROUP BY plate
    """, (session_id,))

    consolidated_orders = cursor.fetchall()
    conn.commit()
    conn.close()

    if not consolidated_orders:
        await update.message.reply_text("No orders found!")
        return

    message = f" **Orders summary for session {session_id}:**\n"
    for plate, quantity in consolidated_orders:
        message += f"- Plate {plate}: {quantity} times\n"

    await update.message.reply_text(message)

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('-t', '--token', help = 'Bot Token', required = True)
    parser.add_argument('-o', '--order', help = 'Order DB', required = True)

    args = parser.parse_args()

    api_token = args.token

    global db
    db = args.order

    init_db(db)

    application = ApplicationBuilder().token(api_token).build()
    # hanlder =  TypeHandler(Update, callback)
    # application.add_handler(handler, -1)
    application.add_handler(CommandHandler("new_session", new_session))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, new_order))
    application.add_handler(CommandHandler("close_session", close_session))


    application.run_polling()

if __name__=='__main__':
    main()

