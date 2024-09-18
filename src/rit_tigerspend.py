import json
import time
from bs4 import BeautifulSoup
from main_webscraper import MainWebScraper
from secret import *


class TigerSpend:
    def __init__(self):
        self.statement_file = "rit_statements.json"
        proxy_details = {
            'hostname': 'dc.smartproxy.com',
            'port': '10002',
            'username': '',
            'password': '',
            'ip': ''
        }
        self.scraper = MainWebScraper({}, website_url="https://tigerspend.rit.edu/login.php",
                                      log_value=2, speed_limiter=1.5, headless=False, debug_name="Test",
                                      profile="Profile 10000", undetectable=False)
        # scraper.click_button("xpath", button_path="//a[text()='App Center']")
        # scraper.click_button("xpath", button_type="test")
        self.scraper.enter_text(text=USER, query_type="id", box_path="ritUsername")
        self.scraper.enter_text(text=PASS, query_type="id", box_path="ritPassword")
        self.scraper.press_key("enter")
        # self.scraper.click_button(query_type="xpath", button_path="button//[@name='_eventId_proceed']")

        self.scraper.wait_for(wait_type="xpath", element_path="//h2[@id='jumptocontent']", wait_time=60)
        self.locate_statement()

    def locate_statement(self):
        self.scraper.set_web_url("https://tigerspend.rit.edu/statementnew.php")

        dropdown_type = "custom_dropdown_type"  # Define if you have a specific type in your `elements`, otherwise set to None
        dropdown_path = "//select[@id='select-account']"  # XPath or other selector to locate the dropdown
        option_value = "63"  # The value associated with "Dining Dollars (Roar Plan)"
        # Select the "Dining Dollars (Roar Plan)" option in the dropdown
        self.scraper.select_dropdown_option(
            query_type="xpath",  # Assuming you're using XPath to locate the element
            dropdown_type=dropdown_type,
            dropdown_path=dropdown_path,
            option_value=option_value
        )
        self.scraper.click_button(query_type="id", button_path="view-statement-button")

    def remove_brackets(self, text):
        result = []
        skip = 0
        for char in text:
            if char == '[':
                skip += 1
            elif char == ']':
                skip -= 1
            elif skip == 0:
                result.append(char)
        return ''.join(result)

    def check_statement(self):

        self.scraper.press_key("refresh", random_key="3z")
        right_page = self.scraper.wait_for(wait_type="xpath",
                                           element_path="//h2[@id='jumptocontent' and text()='Account Statements']",
                                           wait_time=15)
        if not right_page:
            print("reconnecting")
            self.locate_statement()

        soup = BeautifulSoup(self.scraper.driver.page_source, 'html.parser')

        # Parse the table rows
        rows = soup.find_all('tr')[1:]  # Skip the header row
        transactions = {}

        for row in rows:
            date_time_cell = row.find('th', class_='jsa_month')
            description_cell = row.find('td', class_='jsa_desc')
            price_cell = row.find('td', class_='jsa_amount')
            # amount_remaining = row.find('td', class_='jsa_balance bal sr-only')

            if date_time_cell and description_cell and price_cell:
                date_time = date_time_cell.text.strip()
                price = price_cell.text.strip().split()[0].replace(",", "")  # Only take the price, not the balance
                description = self.remove_brackets(description_cell.text.strip()).strip()
                # This splits the description into a list of words, removes the last element, and then joins it back into a string
                description = " ".join(description.split(" ")[:-1])
                amount_remaining = price_cell.text.strip().split()[3].replace(",", "")

                # Use date_time as the key in the dictionary
                transactions[date_time] = {
                    'description': description,
                    'price': price,
                    'amount_remaining': amount_remaining
                }
            else:
                pass
                # print(f"Skipped a row due to missing elements: {row}")

        # Load the existing JSON data if available
        try:
            with open('rit_statements.json', 'r') as file:
                existing_data = json.load(file)
        except FileNotFoundError:
            existing_data = {}

        # Identify new transactions by comparing the existing and new data
        new_transactions = {k: v for k, v in transactions.items() if k not in existing_data}

        # If there are new transactions, merge and write to the file, then return the new transactions
        if new_transactions:
            merged_data = {**existing_data, **transactions}

            with open('rit_statements.json', 'w') as file:
                json.dump(merged_data, file, indent=4)

            print("New data has been detected and written to rit_statements.json")
            return new_transactions

        # If no new transactions, return None
        print("No new data found.")
        return None
