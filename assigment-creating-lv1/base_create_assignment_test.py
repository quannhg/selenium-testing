import csv
import re
from seleniumbase import BaseCase
from selenium.common.exceptions import WebDriverException, NoSuchElementException

class BaseCreateAssigmentTest(BaseCase):
    """Base class for tests involving course & assignment creation and authentication."""

    def setUp(self):
        super().setUp()
        self.create_course()

        # Open the course site and log in
        url = "https://sandbox.moodledemo.net/"
        self.open_page_with_retries(url)
        self.set_window_size(1550, 878)
        self.sleep(1)

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

        def convert_value(value):
            """Tries to convert the string to a boolean, int, or float."""
            if (value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"')):
                return value.strip("'\"")

            # Handle booleans
            if value.lower() == 'true':
                return True
            elif value.lower() == 'false':
                return False

            # Handle numbers
            try:
                int_value = int(value)
                return int_value
            except ValueError:
                pass

            try:
                float_value = float(value)
                return float_value
            except ValueError:
                pass

            return value

        # Open the CSV file
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                processed_row = {
                    key: convert_value(escape_sequence_re.sub(unescape, value))
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

    def create_course(self):
        """Test Course Creation with Login/Logout."""
        url = "https://sandbox.moodledemo.net/"
        username = 'admin'
        password = 'sandbox24'

        # Open the course site and log in
        self.open_page_with_retries(url)
        self.set_window_size(1550, 878)
        self.sleep(1)

        self.login(username, password)

        # Check if the course already exists
        if self.is_element_visible('a:contains("L01.25-Q")'):
            print("Course already exists, skipping course creation.")
            self.logout()
            return

        self.click('a:contains("My courses")')

        self.click('[id="action_bar"] .btn-primary')
        self.update_text("#id_fullname", "L01.25-Q")
        self.update_text("#id_shortname", "L01.25-Q")
        self.update_text("#id_idnumber", "L01.25-Q-001")

        try:
            self.click("#id_saveanddisplay")
        except Exception:
            print("Course creation encountered an error, possibly already existing.")

        self.logout()

    def create_assignment(self, assignment_name, description, show_description,
                          enable_allow_submissions_from, allow_submissions_from_minute,
                          allow_submissions_from_hour, enable_online_text_submission):
        """Create an assignment using helper functions."""
        self.open_course("L01.25-Q")
        self.enter_edit_mode_and_add_assignment()
        self.set_assignment_details(assignment_name, description, show_description)
        self.configure_submission_time(enable_allow_submissions_from,
                                       allow_submissions_from_minute, allow_submissions_from_hour)
        self.configure_online_text_submission(enable_online_text_submission)
        self.click("#id_submitbutton2")

    def open_course(self, course_name):
        """Navigates to the specified course."""
        self.click(f'a:contains("{course_name}")')

    def enter_edit_mode_and_add_assignment(self):
        """Switch to edit mode and add a new assignment."""
        self.click('.custom-switch')
        self.wait_for_element_visible(".activity-add-text", timeout=5)
        self.click(".activity-add-text")
        self.click_xpath("//div[contains(@class, 'optionname') and contains(text(), 'Assignment')]")

    def set_assignment_details(self, assignment_name, description, show_description):
        """Sets the name and description for the assignment."""
        self.update_text("#id_name", assignment_name)
        if show_description:
            self.click("#id_showdescription")
        self.enter_description_in_editor(description)

    def enter_description_in_editor(self, description):
        """Interacts with TinyMCE editor to set the description."""
        self.switch_to_frame(0)
        self.update_text("#tinymce", description)
        self.switch_to_default_content()

    def configure_submission_time(self, enable_allow_submissions_from,
                                  allow_submissions_from_minute, allow_submissions_from_hour):
        """Configures the submission time settings."""
        if enable_allow_submissions_from:
            self.click("#id_allowsubmissionsfromdate_calendar .icon")
            self.sleep(1)
            self.click(".yui3-calendar-row:nth-of-type(2) :last-child")
            self.select_option_by_text("#id_allowsubmissionsfromdate_minute", allow_submissions_from_minute)
            self.select_option_by_text("#id_allowsubmissionsfromdate_hour", allow_submissions_from_hour)
        else:
            self.click("#id_allowsubmissionsfromdate_enabled")
            self.safe_verify_element_present('#id_allowsubmissionsfromdate_calendar.disabled')

    def configure_online_text_submission(self, enable_online_text_submission):
        """Configures online text submission settings."""
        if enable_online_text_submission:
            self.click("#id_assignsubmission_onlinetext_enabled")
            self.safe_verify_element_present("//*[@id='fgroup_id_assignsubmission_onlinetext_wordlimit_group_label']")
        else:
            self.safe_verify_element_present('//*[@data-groupname="assignsubmission_onlinetext_wordlimit_group" and contains(@style, "display: none;")]')

    def delete_assignment(self):
        """Deletes the created assignment."""

        activities = self.find_elements(".activity-grid .activity-actions")
        activities[-1].click() # Assume the last activity is the newest assignment

        delete_buttons = self.find_elements("#action-menu-5-menu > a:nth-child(9)")
        self.sleep(1)
        if delete_buttons:
            delete_buttons[0].click()
        self.sleep(1)  # Ensure deletion has occurred