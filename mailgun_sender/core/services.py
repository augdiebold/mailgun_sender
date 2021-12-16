import requests
from django.conf import settings


def send_mail(_from, to, subject, text):
    url = f"https://api.mailgun.net/v3/{settings.EMAIL_DOMAIN}/messages"
    api_key = settings.EMAIL_API_KEY

    response = requests.post(
        url,
        auth=("api", api_key),
        data={"from": _from,
              "to": to.replace(' ', '').split(','),
              "subject": subject,
              "text": text},
    )

    return response
