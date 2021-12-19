import requests
from django.conf import settings
from django.db import models

STATUS = [
    ('1', 'pending'),
    ('2', 'sent'),
    ('3', 'failed'),
]


class Email(models.Model):
    _from = models.CharField(choices=[(email, email) for email in settings.EMAIL_ALLOWED_SENDERS], max_length=100)
    to = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    text = models.TextField()
    status = models.CharField(choices=STATUS, max_length=1, default='1')
    sent_at = models.DateTimeField(auto_now_add=True)
    json_response = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.subject

    def send(self):
        url = f"https://api.mailgun.net/v3/{settings.EMAIL_DOMAIN}/messages"
        api_key = settings.EMAIL_API_KEY

        response = requests.post(
            url,
            auth=("api", api_key),
            data={"from": self._from,
                  "to": self.to.replace(' ', '').split(','),
                  "subject": self.subject,
                  "text": self.text},
        )

        self.json_response = response.json()

        self._set_status(response.status_code)

        self.save()

        return response

    def _set_status(self, status_code):
        if status_code == 200:
            self.status = '2'
        else:
            self.status = '3'
