"""Backend implementations for sending emails."""

from email.message import EmailMessage as PythonEmailMessage
from email.policy import Policy
from email.policy import default as default_policy
from typing import Any, Optional, Protocol

from pybpmn_server.common.utils import import_string


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


class BaseEmailBackend:
    """
    Base class for email backend implementations.

    Borrowed from Django's EmailBackend class.

    Subclasses must at least overwrite send_messages().

    open() and close() can be called indirectly by using a backend object as a
    context manager:

       with backend as connection:
           # do something with connection
           pass
    """

    def __init__(self, fail_silently: bool = False, **kwargs):
        self.fail_silently = fail_silently

    def open(self) -> bool:
        """
        Open a network connection.

        This method can be overwritten by backend implementations to
        open a network connection.

        It's up to the backend implementation to track the status of
        a network connection if it's needed by the backend.

        This method can be called by applications to force a single
        network connection to be used when sending mails. See the
        send_messages() method of the SMTP backend for a reference
        implementation.

        The default implementation does nothing.
        """
        return True

    def close(self) -> None:
        """Close a network connection."""
        pass

    def __enter__(self):
        try:
            self.open()
        except Exception:
            self.close()
            raise
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()

    def send_messages(self, email_messages: list[Emailable]) -> int:
        """
        Send one or more EmailMessage objects and return the number of email messages sent.
        """
        raise NotImplementedError("subclasses of BaseEmailBackend must override send_messages() method")


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
