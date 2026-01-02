"""
Dummy email backend that does nothing.
"""

from pybpmn_server.mail import Emailable
from pybpmn_server.mail.backends.base import BaseEmailBackend


class EmailBackend(BaseEmailBackend):
    """A dummy email backend that does nothing."""

    def send_messages(self, email_messages: list[Emailable]) -> int:
        """Do nothing and return the number of messages sent."""
        return len(list(email_messages))
