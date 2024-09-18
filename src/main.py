import json
import time
from datetime import datetime, timedelta

from telegram_bot import TelegramBot
from rit_tigerspend import TigerSpend
from secret import *


class Host:
    def __init__(self, bot_token):
        self.semester_end = datetime.strptime("12/18/24", "%m/%d/%y")
        self.connect_id = None
        self.telegram = TelegramBot(bot_token, self.refresh_transactions, self.check_funds)
        self.tiger_spend = None
        self.transactions = {}

    def add_transactions(self, new_transactions):
        self.transactions = {**self.transactions, **new_transactions}

    def calculate_remaining_days(self):
        today = datetime.today()
        days_remaining = (self.semester_end - today).days
        return days_remaining

    def calculate_remaining_money(self):
        try:
            with open('rit_statements.json', 'r') as file:
                existing_data = json.load(file)
        except FileNotFoundError:
            existing_data = {}

        if not existing_data:
            return 0.0

        # Get the latest remaining balance from the most recent transaction
        last_transaction_date = max(existing_data.keys(), key=lambda date: datetime.strptime(date, "%b %d, %Y %I:%M%p"))
        last_transaction = existing_data[last_transaction_date]
        return float(last_transaction['amount_remaining'])

    def calculate_budget(self, total_remaining, days_remaining):
        weeks_remaining = days_remaining / 7
        daily_budget = total_remaining / days_remaining
        weekly_budget = total_remaining / weeks_remaining
        return daily_budget, weekly_budget

    def calculate_spent_today_and_week(self):
        today = datetime.today().date()
        start_of_week = today - timedelta(days=today.weekday())

        spent_today = 0.0
        spent_week = 0.0

        try:
            with open('rit_statements.json', 'r') as file:
                existing_data = json.load(file)
        except FileNotFoundError:
            existing_data = {}

        for date_str, details in existing_data.items():
            transaction_date = datetime.strptime(date_str, "%b %d, %Y %I:%M%p").date()
            amount_spent = float(details['price'].replace("-", ""))

            if transaction_date == today:
                spent_today += amount_spent

            if start_of_week <= transaction_date <= today:
                spent_week += amount_spent

        return spent_today, spent_week

    def run(self):
        while True:
            updates = self.telegram.get_updates()
            if updates['ok']:
                for update in updates['result']:
                    self.telegram.last_update_id = update['update_id'] + 1
                    self.telegram.handle_message(update['message'])
            print(self.telegram.user_data)
            for id, details in self.telegram.user_data.items():
                try:
                    if details["username"] == "Michael":
                        self.connect_id = id
                except Exception as ex:
                    pass

            time.sleep(10)

    def check_funds(self, request_id):
        if self.connect_id and (self.connect_id == request_id):
            days_remaining = self.calculate_remaining_days()
            total_remaining = self.calculate_remaining_money()
            daily_budget, weekly_budget = self.calculate_budget(total_remaining, days_remaining)

            spent_today, spent_week = self.calculate_spent_today_and_week()

            day_money = daily_budget - spent_today
            week_money = weekly_budget - spent_week

            message = (f"Total remaining ${self.calculate_remaining_money()}\n"
                       f"${day_money:.2f} remaining today\n"
                       f"${week_money:.2f} remaining this week")
            self.telegram.send_message(self.connect_id, message)

    def retrieve_transactions(self):
        self.tiger_spend = TigerSpend()

        new_transactions = self.tiger_spend.check_statement()

        if new_transactions:
            self.add_transactions(new_transactions)

        self.tiger_spend.scraper.quit_scraper()

    def refresh_transactions(self, request_id):
        if self.connect_id and (self.connect_id == request_id):

            self.telegram.send_message(self.connect_id, "Loading")

            self.retrieve_transactions()

            if self.transactions:

                days_remaining = self.calculate_remaining_days()
                total_remaining = self.calculate_remaining_money()
                daily_budget, weekly_budget = self.calculate_budget(total_remaining, days_remaining)

                spent_today, spent_week = self.calculate_spent_today_and_week()

                day_money = daily_budget - spent_today
                week_money = weekly_budget - spent_week

                for transaction, details in self.transactions.items():
                    message = (f"{details['price']} Spent at {details['description']}\n"
                               f"You now have {details['amount_remaining']}\n"
                               f"${day_money:.2f} remaining today\n"
                               f"${week_money:.2f} remaining this week")
                    self.telegram.send_message(self.connect_id, message)

                self.transactions = {}
            else:

                message = (f"No new transactions found.\n"
                           f"Total remaining ${self.calculate_remaining_money()}")
                self.telegram.send_message(self.connect_id, message)


if __name__ == '__main__':
    bot_token = BOT
    host = Host(bot_token)
    host.run()
