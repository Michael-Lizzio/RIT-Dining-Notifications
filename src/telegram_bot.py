import time
import requests


class TelegramBot:
    def __init__(self, bot_token, refresh_func, check_funds):
        self.bot_token = bot_token
        self.refresh_transactions = refresh_func
        self.check_funds = check_funds
        self.base_url = f'https://api.telegram.org/bot{self.bot_token}/'
        self.user_data = {}
        self.last_update_id = None
        self.connection_code = '8891'  # Hard-coded connection code

    def get_updates(self):
        params = {'timeout': 100, 'offset': self.last_update_id}
        response = requests.get(f'{self.base_url}getUpdates', params=params)
        return response.json()

    def send_message(self, chat_id, text):
        url = f'{self.base_url}sendMessage'
        data = {'chat_id': chat_id, 'text': text}
        requests.post(url, data=data)

    def send_message_to_connected(self, text):
        for chat_id, details in self.user_data.items():
            if details.get('status') == 'connected':
                self.send_message(chat_id, text)

    def handle_start(self, chat_id):
        self.send_message(chat_id,
                          "Welcome! Please provide your username and connection code in the format: username,code")
        self.user_data[chat_id] = {'status': 'awaiting_details'}

    def handle_disconnect(self, chat_id):
        self.user_data.pop(chat_id, None)
        self.send_message(chat_id, "You have been disconnected.")

    def handle_help(self, chat_id):
        help_message = (
            "Commands:\n"
            "/start - Start the connection process\n"
            "/disconnect - Disconnect\n"
            "/status - Show your account status\n"
            "/checkfunds - Check your available funds\n"
            "/refresh - Refresh server info after purchase\n"
            "/help - Show this help message"
        )
        self.send_message(chat_id, help_message)

    def handle_status(self, chat_id):
        status = self.user_data.get(chat_id, {}).get('status', 'No status available')
        self.send_message(chat_id, f"Account Status:\n{status}")

    def handle_checkfunds(self, chat_id):
        print("checking funds")
        self.check_funds(chat_id)

    def handle_refresh(self, chat_id):
        self.refresh_transactions(chat_id)
        print("send refresh")

    def handle_message(self, message):
        chat_id = message['chat']['id']
        text = message.get('text')

        if chat_id not in self.user_data:
            self.user_data[chat_id] = {'status': 'null'}

        if text == '/start':
            self.handle_start(chat_id)
        elif text == '/disconnect':
            self.handle_disconnect(chat_id)
        elif text == '/help':
            self.handle_help(chat_id)
        elif text == '/status':
            self.handle_status(chat_id)
        elif text == '/checkfunds':
            if self.user_data.get(chat_id, {}).get('status') == 'connected':
                self.handle_checkfunds(chat_id)
            else:
                self.send_message(chat_id, "You must be connected to use this command.")
        elif text == '/refresh':
            if self.user_data.get(chat_id, {}).get('status') == 'connected':
                self.handle_refresh(chat_id)
            else:
                self.send_message(chat_id, "You must be connected to use this command.")
        else:
            self.handle_details(chat_id, text)

    def handle_details(self, chat_id, text):
        if self.user_data[chat_id]['status'] == 'awaiting_details':
            try:
                username, code = text.split(',')
                if code.strip() == self.connection_code:
                    self.user_data[chat_id] = {'status': 'connected', 'username': username.strip()}
                    self.send_message(chat_id,
                                      f"Connected as {username}. You can now disconnect with /disconnect or type /help for more options.")
                else:
                    self.send_message(chat_id, "Invalid connection code. Please try again.")
            except ValueError:
                self.send_message(chat_id, "Invalid format. Please provide your details in the format: username,code")

    def run(self):
        while True:
            updates = self.get_updates()
            if updates['ok']:
                for update in updates['result']:
                    self.last_update_id = update['update_id'] + 1
                    self.handle_message(update['message'])

            time.sleep(15)


if __name__ == '__main__':
    bot_token = '7519080565:AAFEgaNHGOjEyV7ylFhzcQAcdhPGTDG9dlk'
    bot = TelegramBot(bot_token)
    bot.run()
