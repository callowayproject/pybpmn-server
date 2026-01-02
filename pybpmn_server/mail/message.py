"""Basic Email message management."""

import email.message
import mimetypes
from collections import namedtuple
from datetime import datetime, timezone
from email.headerregistry import Address, AddressHeader
from email.message import EmailMessage as PythonEmailMessage
from email.message import MIMEPart
from email.policy import Policy
from email.policy import default as default_policy
from email.utils import make_msgid
from functools import singledispatchmethod
from pathlib import Path
from typing import Any, Optional, Sequence, TypeAlias

from pybpmn_server.mail import get_connection
from pybpmn_server.mail.backends.base import BaseEmailBackend

# Default MIME type to use on attachments (if it is not explicitly given and cannot be guessed).
DEFAULT_ATTACHMENT_MIME_TYPE = "application/octet-stream"

EmailAlternative = namedtuple("EmailAlternative", ["content", "mimetype"])
EmailAttachment = namedtuple("EmailAttachment", ["filename", "content", "mimetype"])

EmailAttachmentType: TypeAlias = EmailAttachment | MIMEPart | tuple[str, bytes, str]

# TODO: Add testing to EmailMessage


class EmailMessage:
    """
    A container for email information.

    Initialize a single email message (which can be sent to multiple recipients).
    """

    content_subtype = "plain"

    # Undocumented charset to use for text/* message bodies and attachments.
    # If None, defaults to settings.DEFAULT_CHARSET.
    encoding = None

    def __init__(  # NOQA: C901
        self,
        subject: str = "",
        body: str = "",
        from_email: Optional[str] = None,
        to: Optional[Sequence[str]] = None,
        *,
        bcc: Optional[Sequence[str]] = None,
        connection: Optional[BaseEmailBackend] = None,
        attachments: Optional[EmailAttachmentType] = None,
        headers: Optional[dict[str, str]] = None,
        cc: Optional[Sequence[str]] = None,
        reply_to: Optional[Sequence[str]] = None,
    ) -> None:
        from pybpmn_server.common.default_configuration import settings

        if to:
            if isinstance(to, str):
                raise TypeError('"to" argument must be a list or tuple')
            self.to = list(to)
        else:
            self.to = []
        if cc:
            if isinstance(cc, str):
                raise TypeError('"cc" argument must be a list or tuple')
            self.cc = list(cc)
        else:
            self.cc = []
        if bcc:
            if isinstance(bcc, str):
                raise TypeError('"bcc" argument must be a list or tuple')
            self.bcc = list(bcc)
        else:
            self.bcc = []
        if reply_to:
            if isinstance(reply_to, str):
                raise TypeError('"reply_to" argument must be a list or tuple')
            self.reply_to = list(reply_to)
        else:
            self.reply_to = []
        self.from_email = from_email or settings.email.default_from_email
        self.subject = subject
        self.body = body or ""
        self.attachments: list[EmailAttachmentType] = []
        if attachments:
            for attachment in attachments:
                if isinstance(attachment, MIMEPart):
                    self.attach(attachment)
                else:
                    self.attach(*attachment)
        self.extra_headers = headers or {}
        self.connection = connection

    def get_connection(self, fail_silently: bool = False) -> BaseEmailBackend:
        """
        Return the email backend to use to send the message.
        """
        if not self.connection:
            self.connection = get_connection(fail_silently=fail_silently)
        return self.connection

    def message(self, *, policy: Policy = default_policy) -> PythonEmailMessage:
        r"""
        Constructs and returns a Python `email.message.EmailMessage` object representing the message to be sent.

        If you ever need to extend the EmailMessage class, you'll probably want to override this method to put the
        content you want into the Python EmailMessage object.

        Args:
            policy: allows specifying the set of rules for updating and serializing the representation of the message.
                It must be an `email.policy.Policy` object. Defaults to `email.policy.default`. In certain cases you
                may want to use `SMTP`, `SMTPUTF8`, or a custom policy. For example,
                `pybpmn_server.mail.backends.smtp.EmailBackend` uses the `SMTP` policy to ensure `\r\n` line endings
                as required by the SMTP protocol.

        Returns:
            The constructed email message object.
        """
        from pybpmn_server.common.default_configuration import settings

        msg = PythonEmailMessage(policy=policy)
        self._add_bodies(msg)
        self._add_attachments(msg)

        msg["Subject"] = str(self.subject)
        msg["From"] = str(self.extra_headers.get("From", self.from_email))
        self._set_list_header_if_not_empty(msg, "To", self.to)
        self._set_list_header_if_not_empty(msg, "Cc", self.cc)
        self._set_list_header_if_not_empty(msg, "Reply-To", self.reply_to)

        # Email header names are case-insensitive (RFC 2045), so we have to
        # accommodate that when doing comparisons.
        header_names = [key.lower() for key in self.extra_headers]
        if "date" not in header_names:
            msg["Date"] = datetime.now().astimezone() if settings.email.use_localtime else datetime.now(timezone.utc)
        if "message-id" not in header_names:
            # Use cached DNS_NAME for performance
            msg["Message-ID"] = make_msgid(domain=settings.domain_name)
        self._idna_encode_address_header_domains(msg)
        return msg

    def recipients(self) -> list[str]:
        """
        Return a list of all recipients of the email (includes direct addressees as well as Cc and Bcc entries).
        """
        return [e_mail for e_mail in (self.to + self.cc + self.bcc) if e_mail]

    def send(self, fail_silently: bool = False) -> Any:
        """Send the email message."""
        if not self.recipients():
            # Don't bother creating the network connection if there's nobody to send to.
            return 0
        return self.get_connection(fail_silently).send_messages([self])

    @singledispatchmethod
    def attach(
        self, filename: Optional[str] = None, content: Optional[str | bytes] = None, mimetype: Optional[str] = None
    ) -> None:
        """
        Attach a file with the given filename and content.

        The filename can be omitted, and the mimetype is guessed, if not provided.

        For a text/* mimetype (guessed or specified), when a bytes object is
        specified as content, decode it as UTF-8. If that fails, set the
        mimetype to DEFAULT_ATTACHMENT_MIME_TYPE and don't decode the content.
        """
        if content is None:
            raise ValueError("content must be provided.")

        mimetype = mimetype or mimetypes.guess_type(filename)[0] or DEFAULT_ATTACHMENT_MIME_TYPE
        basetype, _subtype = mimetype.split("/", 1)

        if basetype == "text" and isinstance(content, bytes):
            try:
                content = content.decode()
            except UnicodeDecodeError:
                # If mimetype suggests the file is text, but it's actually binary, read() raises a UnicodeDecodeError.
                mimetype = DEFAULT_ATTACHMENT_MIME_TYPE

        self.attachments.append(EmailAttachment(filename, content, mimetype))

    @attach.register
    def _(self, filename: MIMEPart, content: None = None, mimetype: None = None) -> None:
        """Attach a MIMEBase subclass into the resulting message attachments."""
        self.attachments.append(filename)

    def attach_file(self, path: Path | str, mimetype: Optional[str] = None) -> None:
        """
        Attach a file from the filesystem.

        Set the mimetype to DEFAULT_ATTACHMENT_MIME_TYPE if it isn't specified and cannot be guessed.

        For a text/* mimetype (guessed or specified), decode the file's content as UTF-8.
        If that fails, set the mimetype to DEFAULT_ATTACHMENT_MIME_TYPE and don't decode the content.
        """
        path = Path(path)
        with path.open("rb") as file:
            content = file.read()
            self.attach(path.name, content, mimetype)

    def _add_bodies(self, msg: PythonEmailMessage) -> None:
        if self.body or not self.attachments:
            body = self.body or ""
            body.encode(encoding="utf8", errors="surrogateescape")
            msg.set_content(body, subtype=self.content_subtype, charset="utf8")

    def _add_attachments(self, msg: PythonEmailMessage) -> None:
        """Add attachments to the message."""
        if not self.attachments:
            return

        msg.make_mixed()
        for attachment in self.attachments:
            if isinstance(attachment, email.message.MIMEPart):
                msg.attach(attachment)  # type: ignore[arg-type]
            else:
                self._add_attachment(msg, *attachment)

    def _add_attachment(self, msg: PythonEmailMessage, filename: str, content: Any, mimetype: str) -> None:
        """Add an attachment to the message."""
        encoding = self.encoding or "utf-8"
        maintype, subtype = mimetype.split("/", 1)

        if maintype == "text" and isinstance(content, bytes):
            # This duplicates logic from EmailMessage.attach() to properly
            # handle EmailMessage.attachments not created through attach().
            try:
                content = content.decode()
            except UnicodeDecodeError:
                mimetype = DEFAULT_ATTACHMENT_MIME_TYPE
                maintype, subtype = mimetype.split("/", 1)

        # See email.contentmanager.set_content() docs for the cases here.
        if maintype == "text":
            # For text/*, content must be str, and maintype cannot be provided.
            msg.add_attachment(content, subtype=subtype, filename=filename, charset=encoding)
        elif maintype == "message":
            # For message/*, content must be email.message.EmailMessage (or
            # legacy email.message.Message), and maintype cannot be provided.
            if isinstance(content, EmailMessage):
                # Django EmailMessage.
                content = content.message(policy=msg.policy)
            elif not isinstance(content, (PythonEmailMessage, email.message.Message)):
                content = email.message_from_bytes(content, policy=msg.policy)
            msg.add_attachment(content, subtype=subtype, filename=filename)
        else:
            # For all other types, content must be bytes-like, and both
            # maintype and subtype must be provided.
            msg.add_attachment(
                content,
                maintype=maintype,
                subtype=subtype,
                filename=filename,
            )

    def _set_list_header_if_not_empty(self, msg: PythonEmailMessage, header: str, values: list[Any]) -> None:
        """
        Set msg's header, either from self.extra_headers, if present, or from the values argument if not empty.
        """
        try:
            msg[header] = self.extra_headers[header]
        except KeyError:
            if values:
                msg[header] = ", ".join(str(v) for v in values)

    def _idna_encode_address_header_domains(self, msg: PythonEmailMessage) -> None:
        """
        If msg.policy does not permit utf8 in headers, IDNA encode all non-ASCII domains in its address headers.
        """
        # Avoids a problem where Python's email incorrectly converts non-ASCII
        # domains to RFC 2047 encoded-words:
        # https://github.com/python/cpython/issues/83938.
        # This applies to the domain only, not to the localpart (username).
        # There is no RFC that permits any 7-bit encoding for non-ASCII
        # characters before the '@'.
        if not getattr(msg.policy, "utf8", False):
            # Not using SMTPUTF8, so apply IDNA encoding in all address
            # headers. IDNA encoding does not alter domains that are already
            # ASCII.
            for field, value in msg.items():
                if isinstance(value, AddressHeader) and any(not addr.domain.isascii() for addr in value.addresses):
                    msg.replace_header(
                        field,
                        [
                            Address(
                                display_name=addr.display_name,
                                username=addr.username,
                                domain=addr.domain.encode("idna").decode("ascii"),
                            )
                            for addr in value.addresses
                        ],
                    )


class EmailMultiAlternatives(EmailMessage):
    """
    A version of EmailMessage that makes it easy to send multipart/alternative messages.

    For example, including text and HTML versions of the text is made easier.
    """

    def __init__(
        self,
        subject: str = "",
        body: str = "",
        from_email: Optional[str] = None,
        to: Optional[Sequence[str]] = None,
        *,
        bcc: Optional[Sequence[str]] = None,
        connection: Optional[BaseEmailBackend] = None,
        attachments: Optional[EmailAttachmentType] = None,
        headers: Optional[dict[str, str]] = None,
        cc: Optional[Sequence[str]] = None,
        reply_to: Optional[Sequence[str]] = None,
        alternatives: Optional[list[EmailAlternative]] = None,
    ):
        super().__init__(
            subject,
            body,
            from_email,
            to,
            bcc=bcc,
            connection=connection,
            attachments=attachments,
            headers=headers,
            cc=cc,
            reply_to=reply_to,
        )
        self.alternatives = [EmailAlternative(*alternative) for alternative in (alternatives or [])]

    def attach_alternative(self, content: Optional[str] = None, mimetype: Optional[str] = None) -> None:
        """Attach an alternative content representation."""
        if content is None or mimetype is None:
            raise ValueError("Both content and mimetype must be provided.")
        self.alternatives.append(EmailAlternative(content, mimetype))

    def _add_bodies(self, msg: email.message.EmailMessage) -> None:
        """
        Add the message body and alternatives to the email message.
        """
        if self.body or not self.alternatives:
            super()._add_bodies(msg)
        if self.alternatives:
            msg.make_alternative()
            encoding = self.encoding or "utf-8"
            for alternative in self.alternatives:
                maintype, subtype = alternative.mimetype.split("/", 1)
                content = alternative.content
                if maintype == "text":
                    if isinstance(content, bytes):
                        content = content.decode()
                    msg.add_alternative(content, subtype=subtype, charset=encoding)
                else:
                    msg.add_alternative(content, maintype=maintype, subtype=subtype)

    def body_contains(self, text: str) -> bool:
        """
        Checks that `text` occurs in the email body and in all attached MIME type text/* alternatives.
        """
        if text not in self.body:
            return False

        for content, mimetype in self.alternatives:
            if mimetype.startswith("text/") and text not in content:
                return False
        return True
