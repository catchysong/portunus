from zappa.asynchronous import task

from authentication.models import User
from shared.email import PortunusMailer


@task
def force_password_reset(email):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return

    user.set_unusable_password()
    user.save()

    PortunusMailer.send_lockout_email(user)
