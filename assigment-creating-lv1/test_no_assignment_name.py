from base_create_assignment_test import BaseCreateAssigmentTest
import warnings


class TestNoAssignmentName(BaseCreateAssigmentTest):
    def test_no_assignment_name(self):
        """Main test function to run the align center test."""

        data = self.read_data_from_csv('test_no_assignment_name.csv')

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

            if(assignment_name):
                warnings.warn("WARNING: assignment_name is not empty\n", UserWarning)

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

            # error message for assignment name
            self.assert_element('//div[@class="form-control-feedback invalid-feedback" and @id="id_error_name" and contains(text(), "You must supply a value")]')

            self.logout()