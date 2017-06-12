import re
from random import choice
from string import ascii_uppercase
from django.core.mail import send_mail
from smtplib import SMTPException
from django.template.loader import get_template
from django.conf import settings

# below regex is good for 90% cases - to achieve 100% go below
# http://stackoverflow.com/questions/201323/using-a-regular-expression-to-validate-an-email-address
EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


def is_valid_email(email):
    if not EMAIL_REGEX.match(email):
        return False
    return True


def is_string_blank(string_value):
    if string_value and string_value.strip():
        return False

    return True


def get_random_code(code_length=10):
    """
    Generates the random code
    :param code_length: set the code length
    :return: randomized the code length
    """
    return ''.join(choice(ascii_uppercase) for i in range(code_length))


def send_registration_mail(username, email, code, api_url):
    subject = settings.EMAIL_SUBJECTS['SUBJECT_REGISTRATION']
    from_email = settings.EMAIL_HOST_USER
    recipient = email

    email_context = {
        'username': username,
        'code': code,
        'api_url': api_url,
        'verification_link': settings.BASE_WEBSITE_URL +
                             "/website/confirm_email?code=" + code + "&email=" + email
    }

    message = get_template('registration.html').render(email_context)

    try:
        send_mail(subject, message, from_email, [recipient], fail_silently=False,
                  html_message=message)     # FIXME: either use separate thread or celery
    except SMTPException as e:
        return False

    return True


def send_invitation_mail(invited_by, email, code, api_url):
    subject = settings.EMAIL_SUBJECTS['SUBJECT_INVITATION']
    from_email = settings.EMAIL_HOST_USER
    recipient = email

    email_context = {
        'invited_by': invited_by,
        'recipient': recipient,
        'code': code,
        'api_url': api_url,
        'verification_link': settings.BASE_WEBSITE_URL +
                             "/website/confirm_email?code=" + code + "&email=" + email
    }

    message = get_template('invitation.html').render(email_context)

    try:
        send_mail(subject, message, from_email, [recipient], fail_silently=False,
                  html_message=message)     # FIXME: either use separate thread or celery
    except SMTPException as e:
        return False

    return True


def send_forgot_password_mail(name, email, code, api_url):
    subject = settings.EMAIL_SUBJECTS['SUBJECT_FORGOT_PASSWORD']
    from_email = settings.EMAIL_HOST_USER
    recipient = email

    email_context = {
        'name': name,
        'code': code,
        'api_url': api_url,
        'verification_link': settings.BASE_WEBSITE_URL + "/website/reset_password?code=" + code +
                             "&email=" + email
    }

    message = get_template('forgot_password.html').render(email_context)

    try:
        send_mail(subject, message, from_email, [recipient], fail_silently=False,
                  html_message=message)     # FIXME: either use separate thread or celery
    except SMTPException as e:
        return False

    return True


def password_changed_mail(name, email):
    subject = settings.EMAIL_SUBJECTS['SUBJECT_PASSWORD_CHANGED']
    from_email = settings.EMAIL_HOST_USER
    recipient = email

    email_context = {
        'name': name,
    }

    message = get_template('password_changed.html').render(email_context)

    try:
        send_mail(subject, message, from_email, [recipient], fail_silently=False,
                  html_message=message)     # FIXME: either use separate thread or celery
    except SMTPException as e:
        return False

    return True