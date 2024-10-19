from flask import Flask, render_template_string, request
import imaplib
import email
from email.header import decode_header

app = Flask(__name__)

# Thông tin đăng nhập
username = "18phuocandz@gmail.com"
password = "abrn gmms iwum oeyx"

@app.route('/')
def index():
    return """
    <h1>Nhập địa chỉ email cần đọc</h1>
    <form action="/emails" method="post">
        <input type="text" name="target_email" placeholder="Nhập địa chỉ email" required>
        <button type="submit">Xem Email</button>
    </form>
    """

@app.route('/emails', methods=['POST'])
def emails():
    target_email = request.form['target_email']

    # Kết nối đến server IMAP của Gmail
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(username, password)
    mail.select("inbox")

    # Tìm kiếm email gửi đến địa chỉ cụ thể
    status, messages = mail.search(None, f'TO "{target_email}"')
    email_ids = messages[0].split()

    emails = []
    for email_id in email_ids:
        status, msg_data = mail.fetch(email_id, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])
        
        subject, _ = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode()

        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/html":  # Lấy phần HTML
                    body = part.get_payload(decode=True).decode(errors='ignore')
                    break  # Chỉ lấy phần đầu tiên
        else:
            body = msg.get_payload(decode=True).decode(errors='ignore')

        emails.append({'id': email_id.decode(), 'subject': subject, 'body': body})

    mail.logout()

    # Tạo trang HTML với danh sách email
    html = """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <title>Danh Sách Email</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .email { border: 1px solid #ccc; padding: 15px; margin-bottom: 10px; }
            h2 { color: #333; }
        </style>
    </head>
    <body>
        <h1>Danh Sách Email gửi đến {{ target_email }}</h1>
        <div id="emails">
            {% for email in emails %}
                <div class="email">
                    <h2>{{ email.subject }}</h2>
                    <div>{{ email.body|safe }}</div>  <!-- Hiển thị body HTML -->
                </div>
            {% endfor %}
        </div>
        <a href="/">Quay lại</a>
    </body>
    </html>
    """
    
    return render_template_string(html, emails=emails, target_email=target_email)

if __name__ == "__main__":
    app.run(debug=True)
