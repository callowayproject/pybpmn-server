"""
Email backend that writes messages to the console instead of sending them.
"""

import sys
import threading
from email.charset import Charset

from pybpmn_server.mail import BaseEmailBackend, Emailable


class EmailBackend(BaseEmailBackend):
    """
    Email backend that writes messages to the console instead of sending them.
    """

    def __init__(self, *args, **kwargs):
        self.stream = kwargs.pop("stream", sys.stdout)
        self._lock = threading.RLock()
        super().__init__(*args, **kwargs)

    def write_message(self, message: Emailable) -> None:
        """Write an Emailable message to the stream."""
        msg = message.message()
        raw_charset = msg.get_charset()
        charset = raw_charset.get_output_charset() if isinstance(raw_charset, Charset) else raw_charset
        charset = charset or "utf-8"
        msg_data_bytes = msg.as_bytes()
        msg_data = msg_data_bytes.decode(charset)
        self.stream.write("%s\n" % msg_data)
        self.stream.write("-" * 79)
        self.stream.write("\n")

    def send_messages(self, email_messages: list[Emailable]) -> int:
        """Write all messages to the stream in a thread-safe way."""
        if not email_messages:
            return 0
        msg_count = 0
        with self._lock:
            try:
                stream_created = self.open()
                for message in email_messages:
                    self.write_message(message)
                    self.stream.flush()  # flush after each message
                    msg_count += 1
                if stream_created:
                    self.close()
            except Exception:
                if not self.fail_silently:
                    raise
        return msg_count
