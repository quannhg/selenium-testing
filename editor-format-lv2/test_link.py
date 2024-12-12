from base_editor_test import BaseEditorTest


class TestLink(BaseEditorTest):
    tiny_link_button_selector = None

    def link_text(self, link):
        self.select_all_editor_content()

        """Aligns the text right if the button is not already pressed."""
        button = self.find_element(self.tiny_link_button_selector)

        # Check aria-pressed attribute before clicking
        if button.get_attribute("aria-pressed") != "true":
            self.click(self.tiny_link_button_selector)

        self.update_text("#id_s__summary_tiny_link_urlentry", link)
        self.click(".modal-footer > .btn")

    def verify_link_text(self, link):
        self.switch_to_frame(0)
        self.click("p")
        self.click("html")
        """Verifies if the text in TinyMCE is righted."""
        self.safe_verify_element_present(f'[data-id="id_s__summary"] a[href="{link}"]')
        self.switch_to_default_content()

    def test_link(self):
        """Main test function to run the align right test."""
        data = self.read_data_from_csv('test_link.csv')

        # Assuming only one row of credentials in the CSV for this test scenario
        for row in data:
            url = row['url']
            
            username = row['username']
            password = row['password']
            editor_content = row['editor_content']
            link = row['link']
            skip_test = row.get('_skip_', 'False').lower() == 'true'
            
            self.username_sel = row.get('username_sel', self.username_sel)
            self.password_sel = row.get('password_sel', self.password_sel)
            self.login_btn_sel = row.get('login_btn_sel', self.login_btn_sel)
            self.tiny_link_button_selector = row.get('tiny_link_button_selector', self.tiny_link_button_selector)

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
            self.link_text(link)
            self.verify_link_text(link)

            self.logout()