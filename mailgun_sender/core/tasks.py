from celery import shared_task


@shared_task
def send_mails(pk):
    from .models import Email

    email = Email.objects.get(pk=pk)
    email.send()
