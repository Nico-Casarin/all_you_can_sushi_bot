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
def init_db():
    conn = sqlite3.connect("ordini.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS session (
            id TEXT PRIMARY KEY,
            attiva INTEGER DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            session_id TEXT,
            user TEXT,
            piatto INTEGER,
            quantita INTEGER,
            PRIMARY KEY (session_id, user, piatto),
            FOREIGN KEY (session_id) REFERENCES sessioni(id)
        )
    """)

    conn.commit()
    conn.close()

async def new_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session_id = str(random.randint(10000, 99999))

    conn = sqlite3.connect("ordini.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO session (id) VALUES (?)", (session_id,))
    conn.commit()
    conn.close()

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('-t', '--token', help = 'Bot Token', required = True)
    parser.add_argument('-o', '--order', help = 'Order DB', required = True)

    args = parser.parse_args()

    api_token = args.token

    global order_db
    order_db = args.order

    application = ApplicationBuilder().token(api_token).build()
    hanlder =  TypeHandler(Update, Callback)
    application.add_handler(handler, -1)


    application.run_polling()

if __name__=='__main__':
    main()

