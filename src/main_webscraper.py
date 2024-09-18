# 5/23/23
# main imports

import os
import random
import time
import logging
from typing import Dict, Optional

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select


class MainWebScraper:
    def __init__(self, elements: Optional[Dict[str, str]] = None, website_url: Optional[str] = None,
                 speed_limiter: float = 0.0, log_value: int = 0,
                 headless: bool = False, debug_name: str = "null", profile: str = "", undetectable: bool = False,
                 proxy_info: Optional[Dict[str, str]] = None):

        self.log_value = log_value
        self.speed_limiter = speed_limiter
        self.headless = headless
        self.debug_name = debug_name
        self.profile = profile
        self.undetectable = undetectable
        self.proxy_info = proxy_info

        self.driver = self.setup_driver()

        self.website_url = website_url
        if self.website_url is not None:
            self.driver.get(self.website_url)
            logging.info(f"Loaded URL: {self.website_url} - {self.debug_name}")
        else:
            logging.info(f"No website URL provided - {self.debug_name}")

        self.elements = elements

        self.special_action = {
            'enter': Keys.RETURN,
            'tab': Keys.TAB,
            'ctrl': Keys.CONTROL,
            'alt': Keys.ALT,
            'delete': Keys.DELETE,
            'backspace': Keys.BACKSPACE,
            'escape': Keys.ESCAPE,
            'down_arrow': Keys.ARROW_DOWN,
            'up_arrow': Keys.ARROW_UP,
            'right_arrow': Keys.ARROW_RIGHT,
            'left_arrow': Keys.ARROW_LEFT,
            "refresh": Keys.F5

        }

        self.random_dict = {'full': 60, 'half': 30, 'long': 15, 'slow': 10, 'medium': 5, 'quick': 2, 'fast': 1}

    # general ----------------------------------------------------------------------------------------------------------
    def setup_driver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("start-maximized")
        if self.profile:
            # gets the computers username
            computer = os.path.dirname(os.path.abspath(__file__)).split(os.path.sep)[2]
            # chrome_options.add_argument(
            #    rf'--user-data-dir=C:\Users\mjliz_9kaompp\AppData\Local\Google\Chrome\User Data\{self.profile}')
            chrome_options.add_argument(
                rf'--user-data-dir=C:\Users\{computer}\AppData\Local\Google\Chrome\User Data\{self.profile}')

        if self.proxy_info:
            proxy_str = '{hostname}:{port}'.format(hostname=self.proxy_info["hostname"], port=self.proxy_info["port"])
            chrome_options.add_argument('--proxy-server={}'.format(proxy_str))

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            return self.driver

        except Exception as e:
            logging.error(
                f"Failed to start browser: , error: {e} - {self.debug_name}")
            return False

    def quit_scraper(self, attempt=2) -> None:
        logging.info(f"Quitting scraper... - {self.debug_name}")
        try:
            # self.driver.close()
            self.driver.quit()
        finally:
            try:
                if self.wait_for('tag_name', element_path="body", wait_time=1):
                    print("Failed Close")
                    self.quit_scraper(attempt=attempt - 1) if attempt > 0 else None
                print("Closed")
            except Exception as ex:
                print(f"Closed {ex}")

        # try:
        #     url = self.driver.current_url
        #     print(url)
        # except Exception as ex:
        #     print(f"Closed {ex}")
        # else:
        #     print("Failed Close")
        #     self.quit_scraper(attempt=attempt-1) if attempt > 0 else None

    def __enter__(self) -> 'MainWebScraper':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.quit_scraper()

    def set_web_url(self, new_url: str, update_driver: bool = True) -> bool:
        print(new_url)
        logging.info(f"Set new URL: {new_url} - {self.debug_name}")
        self.website_url = new_url

        if update_driver:
            try:
                self.driver.get(self.website_url)
                self.wait_for('tag_name', element_path="body", wait_time=10)
                time.sleep(self.speed_limiter)
                self.wait_for('tag_name', element_path="body", wait_time=10)
                logging.info(f"Updated driver URL to: {self.website_url} - {self.debug_name}")
                return True
            except Exception as e:
                logging.error(f"Failed to update driver URL to: {self.website_url}\nError - {e} - {self.debug_name}")
                return False

    def get_query(self, query_type, transfer):
        match query_type:
            case "xpath":
                return By.XPATH, transfer
            case "id":
                return By.ID, transfer
            case "name":
                return By.NAME, transfer
            case "class":
                return By.CLASS_NAME, transfer
            case "tag_name":
                return By.TAG_NAME, transfer
            case "link_text":
                return By.LINK_TEXT, transfer
            case "partial_link_text":
                return By.PARTIAL_LINK_TEXT, transfer
            case "css":
                return By.CSS_SELECTOR, transfer
            case _:
                return None

    def random_wait(self, random_key) -> float:
        closest_upper = float('inf')
        closest_lower = float('-inf')

        if random_key == "0":
            return 0.0
        # Check for 'e' or 'z' at the end of the input number
        if random_key.endswith('e'):
            return float(random_key[:-1])  # Wait exactly the input number

        if random_key.endswith('z'):
            return random.uniform(0, float(random_key[:-1]))  # Wait from 0 to the input number

        # Iterate over the dictionary items to find the closest upper and lower bounds
        for key, value in self.random_dict.items():
            if value >= int(random_key) and value < closest_upper:
                closest_upper = value
            if value <= int(random_key) and value > closest_lower:
                closest_lower = value

        # Generate a random float within the range of closest_lower to closest_upper
        return random.uniform(float(closest_lower), float(closest_upper))

    def wait_for(self, wait_type: str, element_type: str = "null", element_path: str = "null",
                 wait_time: int = 30) -> bool:
        path = self.elements.get(element_type, None)
        path = element_path if path is None else path
        search = self.get_query(wait_type, path)
        if path is None:
            logging.warning(f"No element found for type: {element_type} path: {element_path} - {self.debug_name}")
            return False
        try:
            wait = WebDriverWait(self.driver, wait_time)
            wait.until(EC.presence_of_element_located(search))
            logging.info(f"Found element for type: {element_type} path: {element_path} - {self.debug_name}")
            return True
        except Exception as e:
            logging.error(
                f"Failed to Find element for type: {element_type} path: {element_path}, error: {e} - {self.debug_name}")
            return False

    # interactions -----------------------------------------------------------------------------------------------------

    def click_button_fail_test(self, query_type: str, button_type: str = "null", button_path: str = "null",
                               wait_time: int = 10, random_key: str = "0", index: int = None) -> bool:
        time.sleep(self.random_wait(random_key))
        path = self.elements.get(button_type, None)
        path = button_path if path is None else path

        # Construct path dynamically if an index is provided
        if index is not None and query_type == 'xpath' and 'radio' in path:
            path = f"({path})[{index}]"

        search = self.get_query(query_type, path)
        if path is None:
            logging.warning(f"No button found for type: {button_type} path: {button_path} - {self.debug_name}")
            return False
        try:
            button = WebDriverWait(self.driver, wait_time).until(EC.element_to_be_clickable(search))
            # self.driver.execute_script("arguments[0].scrollIntoView();", button)
            button.click()
            logging.info(f"Clicked button for type: {button_type} path: {button_path} - {self.debug_name}")
            return True
        except Exception as e:
            logging.error(
                f"Failed to click button for type: {button_type} path: {button_path}, error: e - {self.debug_name}")
            # f"Failed to click button for type: {button_type} path: {button_path}, error: {e} - {self.debug_name}")
            return False

    def click_button(self, query_type: str, button_type: str = "null", button_path: str = "null",
                     wait_time: int = 10, random_key: str = "0", scroll_type: str = "default") -> bool:
        time.sleep(self.random_wait(random_key))
        path = self.elements.get(button_type, None)
        path = button_path if path is None else path
        search = self.get_query(query_type, path)
        if path is None:
            logging.warning(f"No button found for type: {button_type} path: {button_path} - {self.debug_name}")
            return False
        try:
            button = WebDriverWait(self.driver, wait_time).until(EC.element_to_be_clickable(search))

            # Scroll to the button based on scroll_type
            if scroll_type == "center":
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'auto', block: 'center', inline: 'nearest'});", button)
            elif isinstance(scroll_type, (int, float)):
                self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_type});")
            else:  # Default scrolling
                # self.driver.execute_script("arguments[0].scrollIntoView();", button)
                actions = ActionChains(self.driver)
                actions.move_to_element(button).perform()

            button.click()
            logging.info(f"Clicked button for type: {button_type} path: {button_path} - {self.debug_name}")
            return True
        except Exception as e:
            logging.error(
                f"Failed to click button for type: {button_type} path: {button_path}, error: e - {self.debug_name}")
            # f"Failed to click button for type: {button_type} path: {button_path}, error: {e} - {self.debug_name}")
            return False

    def enter_text(self, text: str, query_type: str, box_type: str = "null", box_path: str = "null",
                   wait_time: int = 10, random_key: str = "0", scroll_type: str = "default") -> bool:
        time.sleep(self.random_wait(random_key))
        path = self.elements.get(box_type, None)
        path = box_path if path is None else path
        search = self.get_query(query_type, path)
        if path is None:
            logging.warning(f"No textbox found for type: {box_type} path: {box_path} - {self.debug_name}")
            return False
        try:
            textbox = WebDriverWait(self.driver, wait_time).until(EC.presence_of_element_located(search))
            # Scroll to the button based on scroll_type
            if scroll_type == "center":
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'auto', block: 'center', inline: 'nearest'});", textbox)
            elif isinstance(scroll_type, (int, float)):
                self.driver.execute_script("arguments[0].scrollIntoView(true);", textbox)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_type});")
            else:  # Default scrolling
                # self.driver.execute_script("arguments[0].scrollIntoView();", textbox)
                actions = ActionChains(self.driver)
                actions.move_to_element(textbox).perform()
            textbox.clear()
            textbox.send_keys(Keys.CONTROL + "a")
            textbox.send_keys(Keys.BACK_SPACE)
            textbox.send_keys(text)
            logging.info(
                f"Entered text '{text}' into textbox for type: {box_type} path: {box_path} - {self.debug_name}")
            return True
        except Exception as e:
            # logging.error(f"Failed to enter text '{text}' into textbox for type: {box_type} path: {box_path}, error: {e} - {self.debug_name}")
            logging.error(
                f"Failed to enter text '{text}' into textbox for type: {box_type} path: {box_path}, error: e - {self.debug_name}")
            return False

    def upload_photo(self, file_path: str, query_type: str, input_box_type: str = "null", input_box_path: str = "null",
                     wait_time: int = 10, random_key: str = "0") -> bool:
        time.sleep(self.random_wait(random_key))
        path = self.elements.get(input_box_type, None)
        path = input_box_path if path is None else path
        search = self.get_query(query_type, path)
        if path is None:
            logging.warning(f"No input box found for type: {input_box_type} path: {input_box_path} - {self.debug_name}")
            return False
        try:
            file_input = WebDriverWait(self.driver, wait_time).until(EC.presence_of_element_located(search))
            # self.driver.execute_script("arguments[0].scrollIntoView();", file_input)
            actions = ActionChains(self.driver)
            actions.move_to_element(file_input).perform()
            file_input.send_keys(file_path)
            logging.info(
                f"Uploaded photo '{file_path}' into input box for type: {input_box_type} path: {input_box_path} - {self.debug_name}")
            return True
        except Exception as e:
            logging.error(
                f"Failed to upload photo '{file_path}' into input box for type: {input_box_type} path: {input_box_path}, error: {e} - {self.debug_name}")
            return False

    def press_key(self, key: str, random_key: str = "0") -> bool:
        time.sleep(self.random_wait(random_key))
        if key in self.special_action:
            key_press = self.special_action[key]
        else:
            logging.warning(f"Invalid key: {key} - {self.debug_name}")
            return False

        try:
            self.actions = ActionChains(self.driver)
            self.actions.send_keys(key_press).perform()
            logging.info(f"Pressed key: {key} - {self.debug_name}")
            return True
        except Exception as e:
            logging.error(f"Failed to press key: {key}, error: {e} - {self.debug_name}")
            return False

    def select_dropdown_option(self, query_type, dropdown_type: str = "null", dropdown_path: str = "null",
                               option_value: str = None, option_text: str = None, wait_time: int = 10,
                               random_key: str = "0") -> bool:

        time.sleep(self.random_wait(random_key))
        path = self.elements.get(dropdown_type, None)
        path = dropdown_path if path is None else path

        time.sleep(self.random_wait(random_key))
        path = self.elements.get(dropdown_type, None)
        path = dropdown_path if path is None else path
        search = self.get_query(query_type, path)

        if path is None:
            logging.warning(f"No dropdown found for type: {query_type} path: {path} - {self.debug_name}")
            return False

        try:
            dropdown = WebDriverWait(self.driver, wait_time).until(EC.presence_of_element_located(search))

            select = Select(dropdown)

            if option_value is not None:
                select.select_by_value(option_value)
            elif option_text is not None:
                select.select_by_visible_text(option_text)
            else:
                logging.error(f"No option value or text provided for dropdown with path: {path} - {self.debug_name}")
                return False

            logging.info(f"Selected option in dropdown with path: {path} - {self.debug_name}")
            return True
        except Exception as e:
            logging.error(f"Failed to select option in dropdown with path: {path}, error: {e} - {self.debug_name}")
            return False


# copy this code into other webscraper
# from main_webscraper import *
# import time
class WebsiteScraper(MainWebScraper):
    def __init__(self, user_info, website_url="null", speed_limiter=0.0, log_value=0, headless=False, debug_name="null",
                 profile: str = "", undetectable: bool = False):
        # Xpath for buttons
        # <span class="css-1ev1cvs">Continue with Google</span>

        button = {
            'no': "//button[contains(text(), 'Generate')]",
            'download': '//button[@id="download-model-image"]',
            'test': "//a[text()='App Center']",
            'signin': '//button[contains(@class,"social-auth-btn") and span[text()="Continue with Google"]]',
            'google': "//span[@class='middle' and text()='Login with Google']"
        }

        txt_box = {
            'prompt_box': "//textarea[@class='model-input-text-input']"
        }

        elements = {}
        elements.update(button)
        elements.update(txt_box)

        super().__init__(elements, website_url=website_url, speed_limiter=speed_limiter, log_value=log_value,
                         headless=headless, debug_name=debug_name, profile=profile, undetectable=undetectable)

        self.speed_limiter = speed_limiter
        if user_info != "null":
            self.username = user_info[0]
            self.password = user_info[1]
        # self.wait_for('tag_name', element_path="body", wait_time=10)
        # self.login()
        time.sleep(self.speed_limiter)

    def login(self):
        print(self.driver.page_source)
        input("press enter")
        # self.google_auth(self.username, self.password)


if __name__ == "__main__":
    proxy_details = {
        'hostname': 'dc.smartproxy.com',
        'port': '10098',
        'username': '',
        'password': '',
        'ip': ''
    }
    scraper = MainWebScraper(website_url="https://pinterest.com/login",
                             log_value=2, speed_limiter=1.5, headless=False, debug_name="Test", profile="Profile 98",
                             undetectable=False, proxy_info=proxy_details)
    # scraper.click_button("xpath", button_path="//a[text()='App Center']")
    # scraper.click_button("xpath", button_type="test")
    input("Press Enter")
    scraper.quit_scraper()
    input("E?")
