#!/usr/bin/env python3
# Dòng trên cho hệ điều hành biết cách chạy file Python này khi gọi trực tiếp.

# Import các thư viện chuẩn cần thiết
import argparse  # Thư viện để phân tích tham số dòng lệnh
import os  # Thư viện làm việc với biến môi trường, đường dẫn
import smtplib  # Thư viện chuẩn để gửi email qua SMTP
import ssl  # Thư viện tạo ngữ cảnh SSL/TLS an toàn
import sys  # Thư viện tương tác với hệ thống (in ra stderr, thoát mã)
import mimetypes  # Thư viện đoán kiểu MIME của file đính kèm
from email.message import EmailMessage  # Lớp hỗ trợ tạo email hiện đại (MIME)
from pathlib import Path  # Hỗ trợ thao tác đường dẫn hệ thống tệp
from typing import Iterable, List, Optional  # Gợi ý kiểu cho code rõ ràng hơn


def parse_recipients(value: Optional[str]) -> List[str]:
    # Hàm chuyển chuỗi email ngăn cách bởi dấu phẩy thành danh sách email
    if not value:
        # Nếu không có giá trị, trả về danh sách rỗng
        return []
    # Tách bằng dấu phẩy, loại bỏ khoảng trắng dư thừa, bỏ phần rỗng
    return [addr.strip() for addr in value.split(",") if addr.strip()]


def add_attachments(message: EmailMessage, attachment_paths: Iterable[str]) -> None:
    # Hàm thêm các tệp đính kèm vào đối tượng EmailMessage
    for path_str in attachment_paths:
        # Chuẩn hóa đường dẫn: mở rộng ~, chuyển sang đường dẫn tuyệt đối
        file_path = Path(path_str).expanduser().resolve()
        # Kiểm tra tồn tại và là file
        if not file_path.exists() or not file_path.is_file():
            # Nếu không hợp lệ, báo lỗi rõ ràng
            raise FileNotFoundError(f"Attachment not found: {file_path}")

        # Đoán kiểu MIME (vd: image/png, application/pdf)
        guessed_type, encoding = mimetypes.guess_type(str(file_path))
        # Mặc định nếu không đoán được
        maintype, subtype = ("application", "octet-stream")
        if guessed_type:
            # Nếu đoán được, tách main/sub type
            maintype, subtype = guessed_type.split("/", 1)

        # Đọc dữ liệu nhị phân của file
        with open(file_path, "rb") as f:
            file_data = f.read()

        # Thêm vào email với loại MIME và tên file tương ứng
        message.add_attachment(
            file_data,
            maintype=maintype,
            subtype=subtype,
            filename=file_path.name,
        )


def build_message(
    sender: str,  # Địa chỉ email người gửi
    to_addrs: List[str],  # Danh sách người nhận chính
    cc_addrs: List[str],  # Danh sách người nhận CC
    subject: str,  # Tiêu đề email
    text_body: Optional[str] = None,  # Nội dung dạng text thuần
    html_body: Optional[str] = None,  # Nội dung dạng HTML
    attachments: Optional[List[str]] = None,  # Danh sách đường dẫn tệp đính kèm
) -> EmailMessage:
    # Hàm dựng đối tượng EmailMessage hoàn chỉnh từ các tham số

    if not text_body and not html_body:
        # Yêu cầu phải có ít nhất text hoặc html
        raise ValueError("You must provide at least --text or --html content")

    # Tạo đối tượng email rỗng
    message = EmailMessage()
    # Thiết lập trường From
    message["From"] = sender
    # Thiết lập trường To (nối danh sách bằng dấu phẩy)
    message["To"] = ", ".join(to_addrs)
    # Nếu có CC thì thêm trường Cc
    if cc_addrs:
        message["Cc"] = ", ".join(cc_addrs)
    # Thiết lập tiêu đề
    message["Subject"] = subject

    # Xử lý nội dung: có cả text và html -> tạo email multipart/alternative
    if text_body and html_body:
        message.set_content(text_body)
        message.add_alternative(html_body, subtype="html")
    elif html_body:
        # Chỉ có HTML: thêm nội dung text dự phòng để tương thích client không hỗ trợ HTML
        message.set_content("This email contains HTML content. Please use an HTML-capable client.")
        message.add_alternative(html_body, subtype="html")
    else:
        # Chỉ có text
        message.set_content(text_body or "")

    # Nếu có file đính kèm, thêm vào
    if attachments:
        add_attachments(message, attachments)

    # Trả về đối tượng email đã dựng xong
    return message


def send_email(
    host: str,  # Tên máy chủ SMTP
    port: int,  # Cổng kết nối SMTP
    username: str,  # Tên đăng nhập (thường là email)
    password: str,  # Mật khẩu hoặc app password
    use_ssl: bool,  # Dùng SSL (465) hay STARTTLS (587)
    sender: str,  # Địa chỉ email người gửi
    to_addrs: List[str],  # Danh sách người nhận
    cc_addrs: List[str],  # Danh sách CC
    bcc_addrs: List[str],  # Danh sách BCC (ẩn)
    subject: str,  # Tiêu đề
    text_body: Optional[str],  # Nội dung text
    html_body: Optional[str],  # Nội dung HTML
    attachments: Optional[List[str]],  # File đính kèm
    timeout: float = 30.0,  # Thời gian chờ SMTP
) -> None:
    # Hàm gửi email: tạo kết nối SMTP, đăng nhập (nếu có), gửi thư

    # Phải có ít nhất một người nhận bất kỳ trong To/Cc/Bcc
    if not to_addrs and not cc_addrs and not bcc_addrs:
        raise ValueError("You must provide at least one recipient via --to/--cc/--bcc")

    # Dựng nội dung thư
    message = build_message(
        sender=sender,
        to_addrs=to_addrs,
        cc_addrs=cc_addrs,
        subject=subject,
        text_body=text_body,
        html_body=html_body,
        attachments=attachments,
    )

    # Hợp nhất danh sách tất cả người nhận (loại trùng bằng set)
    all_recipients = list({*to_addrs, *cc_addrs, *bcc_addrs})

    # Nếu chọn SSL: dùng SMTP_SSL (thường cổng 465)
    if use_ssl:
        context = ssl.create_default_context()  # Tạo ngữ cảnh SSL an toàn mặc định
        with smtplib.SMTP_SSL(host=host, port=port, context=context, timeout=timeout) as server:
            # Nếu có username, tiến hành đăng nhập
            if username:
                server.login(username, password)
            # Gửi thư
            server.send_message(message, from_addr=sender, to_addrs=all_recipients)
    else:
        # STARTTLS (thường cổng 587): kết nối thường rồi nâng cấp TLS
        with smtplib.SMTP(host=host, port=port, timeout=timeout) as server:
            server.ehlo()  # Chào server, khai báo khả năng
            try:
                server.starttls(context=ssl.create_default_context())  # Nâng cấp kết nối lên TLS
                server.ehlo()  # Chào lại sau khi vào TLS
            except smtplib.SMTPException:
                # Một số server không hỗ trợ STARTTLS; bỏ qua nếu thất bại
                pass
            if username:
                server.login(username, password)  # Đăng nhập SMTP
            server.send_message(message, from_addr=sender, to_addrs=all_recipients)  # Gửi thư


def env_default(name: str, default: Optional[str] = None) -> Optional[str]:
    # Hàm tiện ích: lấy giá trị từ biến môi trường, nếu không có thì dùng mặc định
    return os.environ.get(name, default)


def build_arg_parser() -> argparse.ArgumentParser:
    # Hàm tạo bộ phân tích tham số dòng lệnh
    parser = argparse.ArgumentParser(
        description="Send an email via SMTP (supports TLS/SSL, HTML, and attachments)",
    )

    # Thông số kết nối SMTP
    parser.add_argument("--host", default=env_default("SMTP_HOST", "smtp.gmail.com"), help="SMTP server host")
    parser.add_argument("--port", type=int, default=int(env_default("SMTP_PORT", "587")), help="SMTP server port")
    parser.add_argument("--user", default=env_default("SMTP_USER"), help="SMTP username (email)")
    parser.add_argument("--password", default=env_default("SMTP_PASS"), help="SMTP password or app password")
    parser.add_argument("--use-ssl", action="store_true", default=env_default("SMTP_SSL", "false").lower() in {"1", "true", "yes"}, help="Use SSL (port 465) instead of STARTTLS")

    # Trường địa chỉ người gửi và người nhận
    parser.add_argument("--from", dest="sender", default=env_default("MAIL_FROM"), help="From email address")
    parser.add_argument("--to", required=False, default=env_default("MAIL_TO"), help="Comma-separated recipient emails")
    parser.add_argument("--cc", default=env_default("MAIL_CC", ""), help="Comma-separated CC emails")
    parser.add_argument("--bcc", default=env_default("MAIL_BCC", ""), help="Comma-separated BCC emails")

    # Tiêu đề và nội dung
    parser.add_argument("--subject", required=True, help="Email subject")
    parser.add_argument("--text", default=None, help="Plain text body")
    parser.add_argument("--html", default=None, help="HTML body")

    # File đính kèm (cho phép nhiều file)
    parser.add_argument("--attach", nargs="*", default=[], help="Attachment file paths")

    # Thời gian chờ giao tiếp SMTP
    parser.add_argument("--timeout", type=float, default=float(env_default("SMTP_TIMEOUT", "30")), help="SMTP timeout in seconds")

    # Trả về đối tượng parser đã cấu hình
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    # Hàm main: nhận argv (nếu không truyền thì lấy sys.argv), phân tích và gửi email
    parser = build_arg_parser()  # Tạo parser tham số
    args = parser.parse_args(argv)  # Phân tích tham số đầu vào

    # Chuẩn hóa chuỗi email thành danh sách
    to_addrs = parse_recipients(args.to)
    cc_addrs = parse_recipients(args.cc)
    bcc_addrs = parse_recipients(args.bcc)

    # Kiểm tra thiếu các tham số bắt buộc (có thể lấy từ biến môi trường)
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

    # Nếu thiếu, báo lỗi và trả về mã 2
    if missing:
        parser.error("Missing required options: " + ", ".join(missing))
        return 2

    try:
        # Thực hiện gửi email
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
        # Nếu không lỗi, in thông báo thành công và trả mã 0
        print("Email sent successfully")
        return 0
    except Exception as exc:
        # Gặp lỗi: in ra stderr và trả mã 1
        print(f"Failed to send email: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    # Nếu chạy trực tiếp file này, gọi hàm main và thoát theo mã trả về
    raise SystemExit(main())