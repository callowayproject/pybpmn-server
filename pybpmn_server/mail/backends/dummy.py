"""
Dummy email backend that does nothing.
"""

from pybpmn_server.mail import BaseEmailBackend, Emailable


class EmailBackend(BaseEmailBackend):
    """A dummy email backend that does nothing."""

    def send_messages(self, email_messages: list[Emailable]) -> int:
        """Do nothing and return the number of messages sent."""
        return len(list(email_messages))
