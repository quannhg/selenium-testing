import csv
import re
from seleniumbase import BaseCase
from selenium.common.exceptions import WebDriverException, NoSuchElementException

class CreateAssigmentTest(BaseCase):
    """Test create assignment by single csv data file."""
    username_sel = "#username"
    password_sel = "#password"
    login_btn_sel = "#loginbtn"
    assignment_name_sel = "#id_name1"
    description_sel = "#tinymce1"
    show_description_sel = "#id_showdescription1"
    allow_submissions_from_sel = "#id_allowsubmissionsfromdate_calendar .icon1"
    submissions_from_minute_sel = "#id_allowsubmissionsfromdate_minute1"
    submissions_from_hour_sel = "#id_allowsubmissionsfromdate_hour1"
    enable_online_text_submission_sel = "#id_assignsubmission_onlinetext_enabled1"
    url = "https://sandbox.moodledemo.net/"

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
                self.clear(self.username_sel)
                self.update_text(self.username_sel, username)
                self.clear(self.password_sel)
                self.update_text(self.password_sel, password)
                self.click(self.login_btn_sel)

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

    def create_course_if_needed(self, username= 'admin', password= 'sandbox24', url="https://sandbox.moodledemo.net", should_login=False):
        """Test Course Creation with Login/Logout."""

        # Open the course site and log in
        self.open_page_with_retries(url)
        self.set_window_size(1550, 878)
        self.sleep(1)

        if(should_login):
            self.login(username, password)

        # Check if the course already exists
        if self.is_element_visible('a:contains("L01.25-Q")'):
            if should_login: self.logout()
            return

        print("Course does not exist, creating course...\n")
        self.click('a:contains("My courses")')

        self.click('[id="action_bar"] .btn-primary')
        self.update_text("#id_fullname", "L01.25-Q")
        self.update_text("#id_shortname", "L01.25-Q")
        self.update_text("#id_idnumber", "L01.25-Q-001")

        try:
            self.click("#id_saveanddisplay")
        except Exception:
            print("Course creation encountered an error, possibly already existing.")

        self.click('[data-key="home"]')

        if(should_login):
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
        self.update_text(self.assignment_name_sel, assignment_name)
        if show_description:
            self.click(self.show_description_sel)
        self.enter_description_in_editor(description)

    def enter_description_in_editor(self, description):
        """Interacts with TinyMCE editor to set the description."""
        self.switch_to_frame(0)
        self.update_text(self.description_sel, description)
        self.switch_to_default_content()

    def configure_submission_time(self, enable_allow_submissions_from,
                                  allow_submissions_from_minute, allow_submissions_from_hour):
        """Configures the submission time settings."""
        if enable_allow_submissions_from:
            self.click(self.allow_submissions_from_sel)
            self.sleep(1)
            self.click(".yui3-calendar-row:nth-of-type(2) :last-child")
            self.select_option_by_text(self.submissions_from_minute_sel, allow_submissions_from_minute)
            self.select_option_by_text(self.submissions_from_minute_sel, allow_submissions_from_hour)
        else:
            self.click("#id_allowsubmissionsfromdate_enabled")
        if (self.assert_allow_submissions_from_sel):
            self.safe_verify_element_present(self.assert_allow_submissions_from_sel)

    def configure_online_text_submission(self, enable_online_text_submission):
        """Configures online text submission settings."""
        if enable_online_text_submission:
            self.click(self.enable_online_text_submission_sel)
        if self.online_text_submission_sel:
            self.safe_verify_element_present(self.online_text_submission_sel)

    def delete_assignment(self):
        """Deletes the created assignment."""

        activities = self.find_elements(".activity-grid .activity-actions")
        activities[-1].click() # Assume the last activity is the newest assignment

        delete_buttons = self.find_elements("#action-menu-5-menu > a:nth-child(9)")
        self.sleep(1)
        if delete_buttons:
            delete_buttons[0].click()
        self.sleep(1)  # Ensure deletion has occurred

    def test_create_assignment(self):
        """Test function to run multiple assignment tests."""

        data = self.read_data_from_csv('test_create_assignment.csv')

        for idx, row in enumerate(data):
            # Use a fallback for 'test_name' from the row dictionary
            test_name = row.get('test_name', f'Test_{idx + 1}')

            # Extracting other fields from the CSV row
            username = row['username']
            password = row['password']
            assignment_name = row['assignment_name']
            description = row['description']
            show_description = row.get('show_description', 'False')
            enable_allow_submissions_from = row.get('enable_allow_submissions_from', 'False')
            allow_submissions_from_minute = row.get('allow_submissions_from_minute', '00')
            allow_submissions_from_hour = row.get('allow_submissions_from_hour', '00')
            enable_online_text_submission = row.get('enable_online_text_submission', 'False')
            skip_test = row.get('_skip_', False)

            self.username_sel = row.get('username_sel', self.username_sel)
            self.password_sel = row.get('password_sel', self.password_sel)
            self.login_btn_sel = row.get('login_btn_sel', self.login_btn_sel)
            assert_element_sel = row.get('assert_element_sel', None)
            self.assignment_name_sel = row.get('assignment_name_sel', self.assignment_name_sel)
            self.description_sel = row.get('description_sel', self.description_sel)
            self.show_description_sel = row.get('show_description_sel', self.show_description_sel)
            self.allow_submissions_from_sel = row.get("allow_submissions_from_sel", self.allow_submissions_from_sel)
            self.submissions_from_minute_sel = row.get("submissions_from_minute_sel", self.submissions_from_minute_sel)
            self.submissions_from_hour_sel = row.get("submissions_from_hour_sel", self.submissions_from_hour_sel)
            self.enable_online_text_submission_sel = row.get("enable_online_text_submission_sel", self.enable_online_text_submission_sel)
            self.assert_allow_submissions_from_sel = row.get("assert_allow_submissions_from_sel", None)
            self.online_text_submission_sel = row.get("online_text_submission_sel", None)

            self.url = row.get("url", self.url)

            if skip_test:
                print(f"Skipping test: {test_name}\n")
                continue

            print(f"Running test: {test_name}\n")

            # Open the course site and log in
            self.open_page_with_retries(self.url)
            self.set_window_size(1550, 878)
            self.sleep(1)

            self.login(username, password)

            self.create_course_if_needed(username=username, password=password, url=self.url)

            self.create_assignment(
                assignment_name, description, show_description,
                enable_allow_submissions_from, allow_submissions_from_minute, allow_submissions_from_hour,
                enable_online_text_submission
            )

            self.assert_element(assert_element_sel)

            self.logout()