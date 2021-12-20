from django.test import TestCase, override_settings
from unittest.mock import patch, Mock

from mailgun_sender.core.admin import EmailModelAdmin, admin, Email


class EmailModelAdminTest(TestCase):
    @patch('mailgun_sender.core.models._run_send_mail_task')
    def setUp(self, mock_signal):
        self.obj = Email.objects.create(
            _from="test@mailgun.com",
            to="test_receiver@mailgun.com",
            subject="test sample",
            text="mailgun test",
        )

        self.model_admin = EmailModelAdmin(Email, admin.site)

    def test_colored_status(self):
        """It should change color style based on email status"""
        self.assertIn('<b style="color:orange;', self.model_admin.colored_status(self.obj))

    def test_has_action(self):
        """Action send_again should be installed."""
        self.assertIn('send_again', self.model_admin.actions)

    def test_send_again(self):
        """It should send again all selected emails."""
        self.call_action()
        self.assertEqual(2, Email.objects.all().count())

    def test_message(self):
        """It should send a message to the user."""
        mock = self.call_action()
        mock.assert_called_once_with(None, '1 email added.')

    @patch('mailgun_sender.core.models._run_send_mail_task')
    def call_action(self, mock_signal):
        queryset = Email.objects.all()

        mock = Mock()
        old_message_user = EmailModelAdmin.message_user
        EmailModelAdmin.message_user = mock

        self.model_admin.send_again(None, queryset)

        EmailModelAdmin.message_user = old_message_user

        return mock
