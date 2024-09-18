
# RIT-Dining-Notifications

## Overview
This repository provides a system that helps RIT students manage and track their RIT Dining Dollars, Tiger Bucks, and Meal Swipes. By connecting your RIT account, you will receive notifications and reports based on your spending, such as purchase reports and budgeting assistance.

Whenever you spend money or dining dollars, the system will notify you with your remaining balance. Additionally, the system includes a budgeting feature that calculates how much you can spend daily and weekly, subtracting purchases from your remaining balance. This helps students make better financial decisions by offering a clear view of their spending.

## Features
- **Spending Notifications**: Receive real-time notifications after every purchase.
- **Remaining Balance**: See your remaining Dining Dollars, Tiger Bucks, or Meal Swipes after each transaction.
- **Budget Assistant**: Track your daily and weekly spending budget.
- **Transaction History**: Retrieve a record of past transactions and remaining balance.

## Requirements
- Python 3.x
- Required Libraries:
  - `requests`
  - `BeautifulSoup`
  - `json`
  - `time`
  - `datetime`
  - Additional helper libraries as specified in the project files.

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/RIT-Dining-Notifications.git
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your credentials:
   - Update `rit_tigerspend.py` with your RIT username and password for accessing the dining statements.
   - Update `telegram_bot.py` with your Telegram Bot API key.

4. Run the program:
   ```bash
   python main.py
   ```

## Usage
- Once connected, the system will automatically track your spending and notify you of your remaining balance.
- Use the `/checkfunds` and `/refresh` commands in the Telegram bot to manually check your balance or refresh the data.

## Files
- **main.py**: Core script that handles transactions, budgeting, and notifications.
- **rit_tigerspend.py**: Handles web scraping for retrieving dining statements from RIT's TigerSpend website.
- **telegram_bot.py**: Implements the Telegram bot for communication with users.

## Future Enhancements
- Integration with other payment methods used on campus.
- More detailed budgeting analytics.

## License
This project is licensed under the MIT License.
