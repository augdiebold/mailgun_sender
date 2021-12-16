from django.conf import settings
from django.test import TestCase
from unittest.mock import patch, Mock

from mailgun_sender.core.services import send_mail


class TestMail(TestCase):
    @patch('mailgun_sender.core.services.requests.post')
    def test_send_mail(self, mock_post):
        """
        When the email is sent, should return a response with status_code = 200 and a standard content message
        from mailgun informing that the mail has been queued.
        """

        sample_mail = {
            "_from": "test@mailgun.com",
            "to": "test_receiver@mailgun.com",
            "subject": "test sample",
            "text": "mailgun test"
        }

        expected_resp = {
            "id": "<sample_id12345>",
            "message": "Queued. Thank you."
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = expected_resp

        mock_post.return_value = mock_response

        resp = send_mail(**sample_mail)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), expected_resp)
        mock_post.assert_called_once_with(
            f'https://api.mailgun.net/v3/{settings.EMAIL_DOMAIN}/messages',
            auth=('api', settings.EMAIL_API_KEY),
            data={
                'from': 'test@mailgun.com',
                'to': ['test_receiver@mailgun.com'],
                'subject': 'test sample',
                'text': 'mailgun test'
            }
        )
