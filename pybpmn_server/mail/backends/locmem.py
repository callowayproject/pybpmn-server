"""
Backend for test environment.
"""

import copy

from pybpmn_server import mail
from pybpmn_server.mail import Emailable
from pybpmn_server.mail.backends.base import BaseEmailBackend


class EmailBackend(BaseEmailBackend):
    """
    An email backend for use during test sessions.

    The test connection stores email messages in a dummy outbox,
    rather than sending them out on the wire.

    The dummy outbox is accessible through the outbox instance attribute.
    """

    def send_messages(self, messages: list[Emailable]) -> int:
        """Redirect messages to the dummy outbox."""
        msg_count = 0
        for message in messages:  # .message() triggers header validation
            message.message()
            mail.OUTBOX.append(copy.deepcopy(message))
            msg_count += 1
        return msg_count
