"""An Email Backend."""

from typing import Any

from pybpmn_server.mail import Emailable


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
