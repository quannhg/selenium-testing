from base_editor_test import BaseEditorTest


class TestEditorStyle(BaseEditorTest):
    style_button_selector = None

    def number_list_text(self):
        self.select_all_editor_content()

        """Aligns the text right if the button is not already pressed."""
        button = self.find_element(self.style_button_selector)

        # Check aria-pressed attribute before clicking
        if button.get_attribute("aria-pressed") != "true":
            self.click(self.style_button_selector)

    def verify_number_list_text(self, assert_element_sel):
        self.switch_to_frame(0)
        # self.click("p")
        # self.click("html")
        """Verifies if the text in TinyMCE is righted."""
        self.safe_verify_element_present(assert_element_sel)
        self.switch_to_default_content()

    def test_editor_style(self):
        """Main test function to run the align right test."""
        data = self.read_data_from_csv('test_editor_style.csv')

        for idx, row in enumerate(data):
            # Use a fallback for 'test_name' from the row dictionary
            test_name = row.get('test_name', f'Test_{idx + 1}')
            url = row['url']
            
            username = row['username']
            password = row['password']
            editor_content = row['editor_content']
            skip_test = row.get('_skip_', 'False').lower() == 'true'

            self.username_sel = row.get('username_sel', self.username_sel)
            self.password_sel = row.get('password_sel', self.password_sel)
            self.login_btn_sel = row.get('login_btn_sel', self.login_btn_sel)
            assert_element_sel = row.get('assert_element_sel', None)
            self.style_button_selector = row.get('style_button_selector', self.style_button_selector)

            # Skip processing if this row is marked to skip
            if skip_test:
                print(f"Skipping test: {test_name}")
                continue

            print(f"Running test: {test_name}\n")

            self.open_page_with_retries(url)
            self.set_window_size(1550, 878)
            self.sleep(1)

            self.login(username, password)
            self.click("a:contains('Settings')")

            self.switch_and_update_editor_content(editor_content)
            self.number_list_text()
            self.verify_number_list_text(assert_element_sel)

            self.logout()