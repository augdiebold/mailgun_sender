import httpretty
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from unittest.mock import patch, Mock

from mailgun_sender.core.models import Email


@override_settings(EMAIL_BASE_URL='https://api.mailgun.net/v3', EMAIL_DOMAIN='mailgun.com', EMAIL_API_KEY='not_really_a_key')
class EmailModelTest(TestCase):
    @patch('mailgun_sender.core.models._run_send_mail_task')
    def setUp(self, mock_signal):

        self.mock_signal = mock_signal

        self.obj = Email(
            _from="test@mailgun.com",
            to="test_receiver@mailgun.com",
            subject="test sample",
            text="mailgun test",
        )

        self.obj.save()

    def test_create(self):
        """ Email object should be created """

        self.assertTrue(Email.objects.exists())

    def test_invalid_email(self):
        """ To must only accept valid emails. Raises ValidationError if invalid."""
        self.obj.to = "not_valid_emails"

        with self.assertRaises(ValidationError) as ve:
            self.obj.full_clean()

        self.assertIn('Email adresses must be valid.', str(ve.exception))

    @patch('mailgun_sender.core.models.requests.post')
    def test_send_success(self, mock_post):
        """
        When the email is sent, should return a response with status_code = 200 and a standard content message
        from mailgun informing that the mail has been queued.

        When succeeded, Email object status should be changed to ('2', 'sent')
        """

        expected_resp = {
            "id": "<sample_id12345>",
            "message": "Queued. Thank you."
        }

        mock_response = Mock()
        mock_post.return_value = mock_response

        mock_response.status_code = 200
        mock_response.json.return_value = expected_resp

        resp = self.obj.send()

        # Check response status_code
        self.assertEqual(resp.status_code, 200)

        # Check json response
        self.assertEqual(resp.json(), expected_resp)

        # Check Email object status
        self.assertEqual(self.obj.status, '2')

        # Check arguments mock was called
        mock_post.assert_called_once_with(
            f"https://api.mailgun.net/v3/mailgun.com/messages",
            auth=('api', 'not_really_a_key'),
            data={
                'from': 'test@mailgun.com',
                'to': ['test_receiver@mailgun.com'],
                'subject': 'test sample',
                'text': 'mailgun test'
            }
        )

    @patch('mailgun_sender.core.models.requests.post')
    def test_send_failed(self, mock_post):
        """
        When failed, Email object status should be changed to ('3', 'failed')
        """

        self.obj.to = ''
        self.obj.save()

        expected_resp = {"message": "to parameter is not a valid address. please check documentation"}

        mock_response = Mock()
        mock_post.return_value = mock_response

        mock_response.status_code = 400
        mock_response.json.return_value = expected_resp

        self.obj.send()

        # Check Email object status
        self.assertEqual(self.obj.status, '3')

        # Check arguments mock was called
        mock_post.assert_called_once_with(
            f"https://api.mailgun.net/v3/mailgun.com/messages",
            auth=('api', 'not_really_a_key'),
            data={
                'from': 'test@mailgun.com',
                'to': [''],
                'subject': 'test sample',
                'text': 'mailgun test'
            }
        )

    def test_run_send_mail_task_signal(self):
        """
        Check if signal is called for each Email saved.
        """

        self.obj.save()

        # Check if signal was called
        self.assertTrue(self.mock_signal.called)

        # Check if signal was called once
        self.assertEqual(self.mock_signal.call_count, 1)
