# MM - 2024.06.26.
# Modulzáró project
# Könyv kölcsönző alkalmazás (selenium teszt)

import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import random


logger = logging.getLogger('my_logger')
logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    format='%(asctime)s - %(levelname)s - %(message)s',  # Define log message format
    filename='app.log',  # Specify the log file
    filemode='a'  # Append mode
)

class SeleniumTest:
    def __init__(self, start_url):
        self.start_url = start_url
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        logger.info('Initialized Selenium WebDriver', extra={'start_url': start_url})

    def open_start_page(self):
        self.driver.get(self.start_url)
        logger.info('Opened start page: %s', self.driver.current_url)


    def search_for_book(self):
        search_button = WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div/form/input[2]')))
        search_button.click()
        logger.info('Clicked "Search" button')

    def select_random_book(self):
        current_url = self.driver.current_url
        if '/search' in current_url:
            logger.info('Navigated to the search page: %s', current_url)
        if "http://127.0.0.1:5001/search" in self.driver.current_url:
            checkboxes = self.driver.find_elements(By.CSS_SELECTOR, 'table input[type="checkbox"]')
            submit_selection_button = self.driver.find_element(By.XPATH, '/html/body/div/div[2]/form/button')
            available_checkboxes = [checkbox for checkbox in checkboxes if checkbox.is_displayed()]
            if available_checkboxes:
                selected_checkbox = random.choice(available_checkboxes)
                selected_checkbox.click()
                logger.info('Successfully selected and clicked a random checkbox')
                submit_selection_button.click()
                logger.info('Clicked "Submit Selection" button')


    def confirm_book(self):
        current_url = self.driver.current_url
        if '/process_selection' in current_url:
            logger.info('Navigated to the search page: %s', current_url)
        if "http://127.0.0.1:5001/process_selection" in self.driver.current_url:
            confirm_button = self.driver.find_element(By.XPATH, '/html/body/div/div[3]/form/button')
            confirm_button.click()
            logger.info('Clicked "Confirm Books" button')

    def confirm_rent(self):
        current_url = self.driver.current_url
        if '/rent_confirmation?' in current_url:
            logger.info('Navigated to the search page: %s', current_url)
        if "http://127.0.0.1:5001/rent_confirmation?" in self.driver.current_url:
            first_name = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'firstName')))
            last_name = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'lastName')))
            first_name.send_keys("test")
            last_name.send_keys("test")
            logger.info("Successfully sent the first and last name")
            confirm_rent_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/form/input[4]')))
            confirm_rent_button.click()
            logger.info('Clicked "Confirm Rent" button')

    def book_return_start(self):
        current_url = self.driver.current_url
        if 'http://127.0.0.1:5001/' in current_url:
            logger.info('Navigated to the search page: %s', current_url)
        if 'http://127.0.0.1:5001/' in self.driver.current_url:
            book_return_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[1]/form[1]/button')))
            book_return_button.click()
            logger.info('Clicked "Book Return" button')

    def find_return_book(self):
        current_url = self.driver.current_url
        if '/return_book' in current_url:
            logger.info('Navigated to the search page: %s', current_url)
        if 'http://127.0.0.1:5001/return_book' in self.driver.current_url:
            first_name = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'firstName')))
            last_name = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'lastName')))
            first_name.send_keys("test")
            last_name.send_keys("test")
            logger.info("Successfully sent the first and last name")
            confirm_button = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, '/html/body/form[1]/button')))
            confirm_button.click()
            logger.info('Clicked "Confirm" button')

    def return_book_finish(self):
        current_url = self.driver.current_url
        if '/return_confirmation' in current_url:
            logger.info('Navigated to the search page: %s', current_url)
        if 'http://127.0.0.1:5001/return_confirmation' in self.driver.current_url:
            check_box = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/form[2]/table/tbody/tr/td[6]/input')))
            check_box.click()
            logger.info("Successfully selected and clicked the checkbox")
            submit_selection = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, '/html/body/form[2]/button')))
            submit_selection.click()
            logger.info('Clicked "Submit Selection" button')


    def rent_book(self):
        self.search_for_book()
        self.select_random_book()
        self.confirm_book()
        self.confirm_rent()

    def return_book(self):
        self.book_return_start()
        self.find_return_book()
        self.return_book_finish()

    def rent_return_test(self):
        self.rent_book()
        self.return_book()

    def run_test(self):
        try:
            self.open_start_page()
            self.rent_return_test()
            logger.info('Selenium test completed successfully!')
        except Exception as e:
            logger.error('Error during Selenium test', extra={'exception': str(e)})
            logger.critical('Critical error occurred', extra={'exception': str(e)})
        finally:
            self.driver.quit()  # Close the WebDriver instance
            logger.info('Closed WebDriver')
