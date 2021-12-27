from django.core.validators import EmailValidator

_validate_emails = EmailValidator(message='Email adresses must be valid.')


def validate_to(value):
    for email in value.replace(' ', '').split(','):
        _validate_emails(email)
