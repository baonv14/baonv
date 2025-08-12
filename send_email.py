#!/usr/bin/env python3
import argparse
import os
import smtplib
import ssl
import sys
import mimetypes
from email.message import EmailMessage
from pathlib import Path
from typing import Iterable, List, Optional


def parse_recipients(value: Optional[str]) -> List[str]:
    if not value:
        return []
    return [addr.strip() for addr in value.split(",") if addr.strip()]


def add_attachments(message: EmailMessage, attachment_paths: Iterable[str]) -> None:
    for path_str in attachment_paths:
        file_path = Path(path_str).expanduser().resolve()
        if not file_path.exists() or not file_path.is_file():
            raise FileNotFoundError(f"Attachment not found: {file_path}")

        guessed_type, encoding = mimetypes.guess_type(str(file_path))
        maintype, subtype = ("application", "octet-stream")
        if guessed_type:
            maintype, subtype = guessed_type.split("/", 1)

        with open(file_path, "rb") as f:
            file_data = f.read()

        message.add_attachment(
            file_data,
            maintype=maintype,
            subtype=subtype,
            filename=file_path.name,
        )


def build_message(
    sender: str,
    to_addrs: List[str],
    cc_addrs: List[str],
    subject: str,
    text_body: Optional[str] = None,
    html_body: Optional[str] = None,
    attachments: Optional[List[str]] = None,
) -> EmailMessage:
    if not text_body and not html_body:
        raise ValueError("You must provide at least --text or --html content")

    message = EmailMessage()
    message["From"] = sender
    message["To"] = ", ".join(to_addrs)
    if cc_addrs:
        message["Cc"] = ", ".join(cc_addrs)
    message["Subject"] = subject

    if text_body and html_body:
        message.set_content(text_body)
        message.add_alternative(html_body, subtype="html")
    elif html_body:
        # Provide an empty plain text fallback to improve client compatibility
        message.set_content("This email contains HTML content. Please use an HTML-capable client.")
        message.add_alternative(html_body, subtype="html")
    else:
        message.set_content(text_body or "")

    if attachments:
        add_attachments(message, attachments)

    return message


def send_email(
    host: str,
    port: int,
    username: str,
    password: str,
    use_ssl: bool,
    sender: str,
    to_addrs: List[str],
    cc_addrs: List[str],
    bcc_addrs: List[str],
    subject: str,
    text_body: Optional[str],
    html_body: Optional[str],
    attachments: Optional[List[str]],
    timeout: float = 30.0,
) -> None:
    if not to_addrs and not cc_addrs and not bcc_addrs:
        raise ValueError("You must provide at least one recipient via --to/--cc/--bcc")

    message = build_message(
        sender=sender,
        to_addrs=to_addrs,
        cc_addrs=cc_addrs,
        subject=subject,
        text_body=text_body,
        html_body=html_body,
        attachments=attachments,
    )

    all_recipients = list({*to_addrs, *cc_addrs, *bcc_addrs})

    if use_ssl:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(host=host, port=port, context=context, timeout=timeout) as server:
            if username:
                server.login(username, password)
            server.send_message(message, from_addr=sender, to_addrs=all_recipients)
    else:
        with smtplib.SMTP(host=host, port=port, timeout=timeout) as server:
            server.ehlo()
            try:
                server.starttls(context=ssl.create_default_context())
                server.ehlo()
            except smtplib.SMTPException:
                pass
            if username:
                server.login(username, password)
            server.send_message(message, from_addr=sender, to_addrs=all_recipients)


def env_default(name: str, default: Optional[str] = None) -> Optional[str]:
    return os.environ.get(name, default)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Send an email via SMTP (supports TLS/SSL, HTML, and attachments)",
    )

    parser.add_argument("--host", default=env_default("SMTP_HOST", "smtp.gmail.com"), help="SMTP server host")
    parser.add_argument("--port", type=int, default=int(env_default("SMTP_PORT", "587")), help="SMTP server port")
    parser.add_argument("--user", default=env_default("SMTP_USER"), help="SMTP username (email)")
    parser.add_argument("--password", default=env_default("SMTP_PASS"), help="SMTP password or app password")
    parser.add_argument("--use-ssl", action="store_true", default=env_default("SMTP_SSL", "false").lower() in {"1", "true", "yes"}, help="Use SSL (port 465) instead of STARTTLS")

    parser.add_argument("--from", dest="sender", default=env_default("MAIL_FROM"), help="From email address")
    parser.add_argument("--to", required=False, default=env_default("MAIL_TO"), help="Comma-separated recipient emails")
    parser.add_argument("--cc", default=env_default("MAIL_CC", ""), help="Comma-separated CC emails")
    parser.add_argument("--bcc", default=env_default("MAIL_BCC", ""), help="Comma-separated BCC emails")

    parser.add_argument("--subject", required=True, help="Email subject")
    parser.add_argument("--text", default=None, help="Plain text body")
    parser.add_argument("--html", default=None, help="HTML body")

    parser.add_argument("--attach", nargs="*", default=[], help="Attachment file paths")

    parser.add_argument("--timeout", type=float, default=float(env_default("SMTP_TIMEOUT", "30")), help="SMTP timeout in seconds")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    to_addrs = parse_recipients(args.to)
    cc_addrs = parse_recipients(args.cc)
    bcc_addrs = parse_recipients(args.bcc)

    missing: List[str] = []
    if not args.sender:
        missing.append("--from or MAIL_FROM")
    if not (to_addrs or cc_addrs or bcc_addrs):
        missing.append("--to/--cc/--bcc or MAIL_TO/MAIL_CC/MAIL_BCC")
    if not args.user:
        missing.append("--user or SMTP_USER")
    if args.password is None:
        missing.append("--password or SMTP_PASS")
    if not args.subject:
        missing.append("--subject")
    if not args.text and not args.html:
        missing.append("--text or --html")

    if missing:
        parser.error("Missing required options: " + ", ".join(missing))
        return 2

    try:
        send_email(
            host=args.host,
            port=args.port,
            username=args.user,
            password=args.password,
            use_ssl=args.use_ssl,
            sender=args.sender,
            to_addrs=to_addrs,
            cc_addrs=cc_addrs,
            bcc_addrs=bcc_addrs,
            subject=args.subject,
            text_body=args.text,
            html_body=args.html,
            attachments=args.attach,
            timeout=args.timeout,
        )
        print("Email sent successfully")
        return 0
    except Exception as exc:
        print(f"Failed to send email: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())