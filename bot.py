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

class DatabaseManager:
    def __init__(self, db_name):
        self.db_name =  db_name
        self.conn = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

    def execute_query(self, query, params=(), fetch_one = False, auto_commit = True):
        try:
            self.cursor.execute(query, params)
            if fetch_one:
                query_result = self.cursor.fetchone()
            else:
                query_result = self.cursor.fetchall()

            if auto_commit and not query.lower().startswith("select"):
                self.commit()

            return query_result
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            return None

    def commit(self):
        if self.conn:
            self.conn.commit()

    def create_table(self, query):
        try:
            self.cursor.execute(query)
            self.commit()
            return True
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            return False


# Inizializza il database SQLite
def init_db(db):
    with DatabaseManager(db) as db_manager:
        query_create = """
        CREATE TABLE IF NOT EXISTS session (
        id TEXT PRIMARY KEY,
        active INTEGER DEFAULT 1,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)
        """

        db_manager.create_table(query_create)

        query_create= """
        CREATE TABLE IF NOT EXISTS orders (
        session_id TEXT,
        user TEXT,
        plate INTEGER,
        quantity INTEGER,
        PRIMARY KEY (session_id, user, plate),
        FOREIGN KEY (session_id) REFERENCES session(id))
        """

        db_manager.create_table(query_create)


async def new_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session_id = str(random.randint(10000, 99999))

    with DatabaseManager(db) as db_manager:
        db_manager.execute_query("INSERT INTO session (id) VALUES (?)", (session_id,))

    await update.message.reply_text(f"New session created! Session ID: {session_id}")

async def new_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.split()

    if len(msg) != 2 or not msg[0].isdigit() or not msg[1].isdigit():
        await update.message.reply_text("Wrong fromat! Use: 'plate_number quantity'.")
        return

    plate, quantity = map(int, msg)
    user = update.message.from_user.username

    with DatabaseManager(db) as db_manager:
        session = db_manager.execute_query("SELECT id FROM session WHERE active = 1 ORDER BY id DESC LIMIT 1",
                                fetch_one = True)
        if not session:
            await update.message.reply_text("No active sessione. Wait for a new session")
            return

        session_id = session[0]
        db_manager.execute_query("""
        INSERT INTO orders (session_id, user, plate, quantity)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(session_id, user, plate) DO UPDATE SET quantity = quantity + ?
    """, (session_id, user, plate, quantity, quantity))

        await update.message.reply_text(f"Order saved for plate n. {plate}")

async def close_session(update: Update, context: ContextTypes.DEFAULT_TYPE):

    with DatabaseManager(db) as db_manager:
        session = db_manager.execute_query("SELECT id FROM session WHERE active = 1 ORDER BY id DESC LIMIT 1", fetch_one = True)
        if not session:
            await update.message.reply_text("No Active session")
            return

        session_id = session[0]
        db_manager.execute_query("UPDATE session SET active = 0 WHERE id = ?", (session_id,))

        consolidated_orders = db_manager.execute_query("""
            SELECT plate, SUM(quantity) FROM orders
         WHERE session_id = ?
         GROUP BY plate
        """, (session_id,))

        if not consolidated_orders:
            await update.message.reply_text("No orders found!")
            return

        message = f" **Orders summary for session {session_id}:**\n"
        for plate, quantity in consolidated_orders:
            message += f"- Plate {plate}: {quantity} times\n"

        await update.message.reply_text(message)

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = " ".join(context.args)
    if len(command) == 0:
        await update.message.reply_text("No Session ID provided!")
        return

    with DatabaseManager(db) as db_manager:
        consolidated_orders = db_manager.execute_query("""
            SELECT plate, SUM(quantity) FROM orders
         WHERE session_id = ?
         GROUP BY plate
        """, (command,))

        if not consolidated_orders:
            await update.message.reply_text("No orders found!")
            return

        message = f" **Orders summary for session {command}:**\n"
        for plate, quantity in consolidated_orders:
            message += f"- Plate {plate}: {quantity} times\n"

        await update.message.reply_text(message)

async def list_sessions(update: Update, context: ContextTypes.DEFAULT_TYPE):

    with DatabaseManager(db) as db_manager:
        sessions = db_manager.execute_query("SELECT id, active, timestamp FROM session ORDER BY timestamp DESC LIMIT 10")

        if not sessions:
            await update.message.reply_text("No sessions saved")
            return

        message = f"Last 10 sessions:\n\nid-active-timestamp\n"

        for session in sessions:
            id, active, timestamp = session
            message += f"{id}-{active}-{timestamp}\n"

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
    application.add_handler(CommandHandler("list_sessions", list_sessions))
    application.add_handler(CommandHandler("search", search))


    application.run_polling()

if __name__=='__main__':
    main()

