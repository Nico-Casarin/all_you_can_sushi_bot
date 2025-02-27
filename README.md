# 🍣 All You Can Eat Helper Bot 🍣

This Telegram bot is your personal assistant for conquering all-you-can-eat (AYCE) adventures!  Whether you're a sushi aficionado, a dumpling devotee, or a rib-eye ruler, this bot helps you track your AYCE sessions, giving you insights into your eating habits and helping you make the most of your culinary challenges.  💪

## Features

* **🍣 Session Logging:** Effortlessly record your AYCE feasts!  Log the dishes you devoured, the quantities you conquered, and the time of your epic meal.  No more mental math or scribbling on napkins!
* **📜 Session History:**  Browse through your past AYCE conquests. Relive the glory of each perfectly placed piece of nigiri or the satisfaction of a mountain of tempura.
* **📊 Statistics and Insights:** (Future Feature)  Uncover the secrets of your appetite!  Discover your most frequently ordered dishes, calculate your average consumption per session, and gain valuable insights into your eating patterns.
* **🤖 User-Friendly Interface:** Communicate with the bot through a simple and intuitive Telegram interface.  Just use commands and let the bot do the rest!
* **💾 Data Persistence:** Your valuable session data is stored securely, so you can track your progress over time and compare your current performance to your past triumphs. (SQLite Database)
* **⌨️ Command Handling:**  Interact with the bot using Telegram commands.  `/start` your culinary journey, session management, `/search` session details

## Getting Started

### Prerequisites

* Python 3.7+
* `python-telegram-bot` library: `pip install python-telegram-bot`
* A Telegram Bot token (obtained from BotFather)

### Installation

1. Clone this repository.
2. Navigate to the project directory.
3. Create and activate a virtual environment (recommended).
4. Install dependencies: `pip install -r requirements.txt` (Create this file if you haven't already.)

### Running the Bot

`python bot.py -t "TOKEN_ID" -o "DB_PATH`

### Usage

Interact with the bot on Telegram using commands:

* `/new_session`: Open a new session.
* `/close_session`: Close a open session and print the orders.
* * `/search`: Search a session by id.
* `/list_sessions`: List the last 10 sessions.

## Contributing

Contributions are welcome!  Fork the repo, make your changes, and submit a pull request.


