import csv
import re
from seleniumbase import BaseCase
from selenium.common.exceptions import WebDriverException, NoSuchElementException

class BaseEditorTest(BaseCase):
    """Base class for tests involving editor interactions and authentication."""

    def read_data_from_csv(self, filename):
        """Reads data from a CSV file and processes escape sequences."""
        data = []

        # Regular expression to match escape sequences
        escape_sequence_re = re.compile(r'\\.')

        def unescape(match):
            """Converts escape sequences to their intended characters."""
            seq = match.group(0)
            if seq == r'\\':
                return '\\'
            elif seq == r'\n':
                return '\n'
            elif seq == r'\t':
                return '\t'
            elif seq == r'\"':
                return '\"'
            elif seq == r'\'':
                return '\''
            # Add more cases for different escape sequences if necessary
            return seq  # Returns unchanged if not a recognized escape

        # Open the CSV file
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                processed_row = {
                    key: escape_sequence_re.sub(unescape, value.strip("'"))
                    for key, value in row.items()
                }
                data.append(processed_row)

        return data

    def open_page_with_retries(self, url, max_retries=3):
        """Attempts to open a page, retries up to max_retries times if it fails."""
        retry_count = 0
        success = False

        while not success and retry_count < max_retries:
            try:
                self.open(url)
                success = True
            except WebDriverException as e:
                retry_count += 1
                print(f"Attempt {retry_count} of {max_retries} failed: {e}")
                self.sleep(2)  # Wait before retrying

        if not success:
            self.fail(f"Failed to open the page {url} after {max_retries} attempts")

    def login(self, username, password, max_retries=3):
        """Logs into the application with provided username and password."""
        retry_count = 0
        logged_in = False

        # self.sleep(2) # Wait for the page to load before attempting to log in

        self.click(".usermenu .login a")
        while retry_count < max_retries and not logged_in:
            self.clear("#username")
            self.update_text("#username", username)
            self.clear("#password")
            self.update_text("#password", password)
            self.click("#loginbtn")

            if self.is_element_visible(".userinitials"):
                logged_in = True
            else:
                retry_count += 1
                print(f"Login attempt {retry_count} failed. Retrying...")
                self.sleep(2)  # Wait before retrying

        if not logged_in:
            self.fail("Failed to log in after multiple attempts")

    def switch_and_update_editor_content(self, content):
        """Switches to the TinyMCE editor and updates its content."""
        self.switch_to_frame(0, 20)
        self.sleep(1)
        self.clear("#tinymce")
        self.update_text("#tinymce", content)
        self.switch_to_default_content()

    def logout(self):
        """Logs out from the application."""
        if self.is_element_present("#user-menu-toggle"):
            self.click("#user-menu-toggle")
        else:
            self.click("#action-menu-toggle-0")

        self.click("a:contains('Log out')")

    def select_all_editor_content(self):
        """Selects all content within the TinyMCE editor."""
        self.switch_to_frame(0)
        self.wait_for_element_visible("#tinymce")
        self.execute_script(
            """
            var editor = document.getElementById('tinymce');
            if (document.createRange && window.getSelection) {
                var range = document.createRange();
                range.selectNodeContents(editor);
                var sel = window.getSelection();
                sel.removeAllRanges();
                sel.addRange(range);
            }
            """
        )
        self.switch_to_default_content()

    def safe_verify_element_present(self, selector, retries=3, wait_time=1):
        """
        Safely verifies if an element is present with retry logic.

        Args:
            selector (str): The CSS selector of the element to check.
            retries (int): The number of times to retry checking for the element.
            wait_time (int or float): The number of seconds to wait between retries.
        """
        attempt = 0
        while attempt < retries:
            elements = self.find_elements(selector)
            if len(elements) > 0:
                return True
            else:
                print(f"Element not found. Retry attempt {attempt + 1} of {retries}.")
                self.sleep(wait_time)
                attempt += 1

        # If element is still not found after all retries, assert failure
        assert len(elements) > 0, f"Element with selector '{selector}' not found after {retries} retries."

    def safe_verify_element_not_present(self, selector, retries=3, wait_time=1):
        """
        Safely verifies if an element is not present with retry logic.

        Args:
            selector (str): The CSS selector of the element to check.
            retries (int): The number of times to retry checking for the element.
            wait_time (int or float): The number of seconds to wait between retries.
        """
        attempt = 0
        while attempt < retries:
            elements = self.find_elements(selector)
            if len(elements) == 0:
                return True
            else:
                print(f"Element still found. Retry attempt {attempt + 1} of {retries}.")
                self.sleep(wait_time)
                attempt += 1

        # If element is still found after all retries, assert failure
        assert len(elements) == 0, f"Element with selector '{selector}' still present after {retries} retries."