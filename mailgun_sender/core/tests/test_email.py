from django.conf import settings
from django.test import TestCase
from unittest.mock import patch, Mock

from mailgun_sender.core.models import Email


class EmailModelTest(TestCase):
    def setUp(self):

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

    @patch('mailgun_sender.core.models.requests.post')
    def test_send_success(self, mock_post):
        """
        When the email is sent, should return a response with status_code = 200 and a standard content message
        from mailgun informing that the mail has been queued.

        When succeeded Email object status should be changed to ('2', 'sent')
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
            f"https://api.mailgun.net/v3/{settings.EMAIL_DOMAIN}/messages",
            auth=('api', settings.EMAIL_API_KEY),
            data={
                'from': 'test@mailgun.com',
                'to': ['test_receiver@mailgun.com'],
                'subject': 'test sample',
                'text': 'mailgun test'
            }
        )

    @patch('mailgun_sender.core.models.requests.post')
    def test_send_failed(self, mock_post):

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
            f"https://api.mailgun.net/v3/{settings.EMAIL_DOMAIN}/messages",
            auth=('api', settings.EMAIL_API_KEY),
            data={
                'from': 'test@mailgun.com',
                'to': [''],
                'subject': 'test sample',
                'text': 'mailgun test'
            }
        )

