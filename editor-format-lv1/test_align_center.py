from base_editor_test import BaseEditorTest


class TestAlignCenter(BaseEditorTest):
    def align_text_center(self):
        """Aligns the text center if the button is not already pressed."""
        self.select_all_editor_content()

        align_button_selector = '[data-mce-name="aligncenter"]'
        button = self.find_element(align_button_selector)

        # Check aria-pressed attribute before clicking
        if button.get_attribute("aria-pressed") != "true":
            self.click(align_button_selector)

    def verify_text_alignment(self):
        """Verifies if the text in TinyMCE is centered."""
        self.switch_to_frame(0)
        self.click("p")
        self.click("html")
        self.safe_verify_element_present('[data-id="id_s__summary"] > [style*="text-align: center;"]')
        self.switch_to_default_content()

    def test_align_center(self):
        """Main test function to run the align center test."""
        url = "https://sandbox.moodledemo.net/"
        data = self.read_data_from_csv('test_align_center.csv')

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
            self.align_text_center()
            self.verify_text_alignment()

            self.logout()