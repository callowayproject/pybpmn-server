"""Backend implementations for sending emails."""

from email.message import EmailMessage as PythonEmailMessage
from email.policy import Policy
from email.policy import default as default_policy
from typing import Any, Optional, Protocol

from pybpmn_server.common.utils import import_string
from pybpmn_server.mail.backends.base import BaseEmailBackend


class Emailable(Protocol):
    """Something that is emailable by a backend."""

    content_subtype: str
    subject: str
    body: str
    from_email: Optional[str]
    to: Optional[list[str]]
    bcc: Optional[list[str]]
    attachments: Optional[Any]
    extra_headers: Optional[dict[str, str]]
    cc: Optional[list[str]]
    reply_to: Optional[list[str]]

    def message(self, *, policy: Policy = default_policy) -> PythonEmailMessage:
        """Constructs and returns a Python `email.message.EmailMessage` object representing the message to be sent."""
        ...

    def recipients(self) -> list[str]:
        """
        Return a list of all recipients of the email (includes direct addressees as well as Cc and Bcc entries).
        """
        ...


OUTBOX: list[Emailable] = []  # Used by the locmem backend


def get_connection(backend: Optional[str] = None, *, fail_silently: bool = False, **kwds: Any) -> BaseEmailBackend:
    """
    Load an email backend and return an instance of it.

    If `backend` is None (default), use settings.email.backend.

    Both fail_silently and other keyword arguments are used in the
    constructor of the backend.
    """
    from pybpmn_server.common.configuration import settings

    klass = import_string(backend or settings.email.backend)
    return klass(fail_silently=fail_silently, **kwds)


def send_mail(
    recipient_list: list[str],
    subject: str,
    body: str,
    from_email: Optional[str] = None,
    *,
    fail_silently: bool = False,
    connection: Optional[BaseEmailBackend] = None,
    html_message: Optional[str] = None,
) -> int:
    """
    Easy wrapper for sending a single message to a recipient list.

    All members of the recipient list will see the other recipients in the 'To' field.

    If from_email is None, use the DEFAULT_FROM_EMAIL setting.
    """
    from .message import EmailMultiAlternatives

    connection = connection or get_connection(fail_silently=fail_silently)
    mail = EmailMultiAlternatives(subject, body, from_email, recipient_list, connection=connection)

    if html_message:
        mail.attach_alternative(html_message, "text/html")

    return mail.send()
