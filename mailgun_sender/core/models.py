import requests
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import send_mails

STATUS = [
    ('1', 'Pending'),
    ('2', 'Sent'),
    ('3', 'Failed'),
]


class Email(models.Model):
    _from = models.CharField('From', choices=[(email, email) for email in settings.EMAIL_ALLOWED_SENDERS], max_length=100)
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


# Signals

@receiver(post_save, sender=Email)
def run_send_mail_task_handler(sender, instance, created, **kwargs):
    _run_send_mail_task(sender, instance, created, **kwargs)


def _run_send_mail_task(sender, instance, created, **kwargs):
    """
    Call send_mails task for each Email post save when created.

    This function can be mocked.
    """
    if created:
        print('Email object sent to tasks')
        send_mails.delay(instance.pk)

