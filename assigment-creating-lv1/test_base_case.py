from base_create_assignment_test import BaseCreateAssigmentTest


class TestBaseCase(BaseCreateAssigmentTest):
    def test_base_case(self):
        """Main test function to run the align center test."""

        data = self.read_data_from_csv('test_base_case.csv')

        # Assuming only one row of credentials in the CSV for this test scenario
        for row in data:
            username = row['username']
            password = row['password']
            assignment_name = row['assignment_name']
            description = row['description']
            show_description = row['show_description']
            enable_allow_submissions_from = row['enable_allow_submissions_from']
            allow_submissions_from_minute = row['allow_submissions_from_minute']
            allow_submissions_from_hour = row['allow_submissions_from_hour']
            enable_online_text_submission = row['enable_online_text_submission']
            skip_test = row.get('_skip_', False)

            # Skip processing if this row is marked to skip
            if skip_test:
                print(f"Skipping test for username: {username}")
                continue

            self.login(username, password)
            self.create_assignment(
                assignment_name, description, show_description,
                enable_allow_submissions_from, allow_submissions_from_minute, allow_submissions_from_hour,
                enable_online_text_submission
            )

            self.assert_element(f'[data-value="{assignment_name}"]')

            self.logout()