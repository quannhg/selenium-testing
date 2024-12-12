from base_editor_test import BaseEditorTest


class TestItalic(BaseEditorTest):
    def italic_text(self):
        self.select_all_editor_content()

        """Aligns the text right if the button is not already pressed."""
        align_button_selector = '[data-mce-name="italic"]'
        button = self.find_element(align_button_selector)

        # Check aria-pressed attribute before clicking
        if button.get_attribute("aria-pressed") != "true":
            self.click(align_button_selector)

    def verify_italic_text(self):
        self.switch_to_frame(0)
        self.click("p")
        self.click("html")
        """Verifies if the text in TinyMCE is righted."""
        self.safe_verify_element_present('[data-id="id_s__summary"] em')
        self.switch_to_default_content()

    def test_italic(self):
        """Main test function to run the align right test."""
        url = "https://sandbox.moodledemo.net/"
        data = self.read_data_from_csv('test_italic.csv')

        # Assuming only one row of credentials in the CSV for this test scenario
        for row in data:
            username = row['username']
            password = row['password']
            editor_content = row['editor_content']
            skip_test = row.get('_skip_', 'False').lower() == 'true'

            # Skip processing if this row is marked to skip
            if skip_test:
                print(f"Skipping test for username: {username}")
                continue

            self.open_page_with_retries(url)
            self.set_window_size(1550, 878)
            self.sleep(1)

            self.login(username, password)
            self.click("a:contains('Settings')")

            self.switch_and_update_editor_content(editor_content)
            self.italic_text()
            self.verify_italic_text()

            self.logout()