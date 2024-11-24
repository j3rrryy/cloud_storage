from datetime import date
from email.mime import multipart, text

from aiosmtplib import SMTP

from config import load_config


class Mail:
    _config = load_config()

    @classmethod
    async def verification(cls, message: dict[str, str], smtp: SMTP) -> None:
        msg = multipart.MIMEMultipart("alternative")
        msg["Subject"] = "Confirm Your Email"
        msg["From"] = cls._config.smtp.username
        msg["To"] = message["email"]
        verification_url = (
            cls._config.app.verification_url + message["verification_token"]
        )

        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Confirm Your Email</title>
            <style>
                .email-container {{
                    font-family: Arial, sans-serif;
                    color: #333;
                    text-align: center;
                    padding: 20px;
                    background-color: #f9f9f9;
                    margin: 0 auto;
                    border-radius: 10px;
                    width: 100%;
                    max-width: 600px;
                }}
                .email-header {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px 0;
                    border-radius: 5px;
                    font-size: 24px;
                    font-weight: bold;
                }}
                .email-content {{
                    margin: 20px 0;
                }}
                .email-footer {{
                    margin-top: 30px;
                    font-size: 12px;
                    color: #888;
                }}
                .button {{
                    display: inline-block;
                    padding: 10px 20px;
                    background-color: #4CAF50;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    margin-top: 20px;
                }}
                .button:hover {{
                    background-color: #45a049;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="email-header">
                    Confirm Your Email
                </div>
                <div class="email-content">
                    <p>Hello, {message['username']}!</p>
                    <p>Please confirm your email address by clicking the button below:</p>
                    <a href="{verification_url}" class="button">Confirm Email</a>
                    <p>This link is valid for 3 days.</p>
                </div>
                <div class="email-footer">
                    <p>If you didn't request this, you can safely ignore this email.</p>
                    <p>&copy; {date.today().year} {cls._config.app.name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        msg.attach(text.MIMEText(html_content, "html"))
        await smtp.send_message(msg)

    @classmethod
    async def info(cls, message: dict[str, str], smtp: SMTP) -> None:
        msg = multipart.MIMEMultipart("alternative")
        msg["Subject"] = "Login Information"
        msg["From"] = cls._config.smtp.username
        msg["To"] = message["email"]

        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Login Information</title>
            <style>
                .email-container {{
                    font-family: Arial, sans-serif;
                    color: #333;
                    text-align: center;
                    padding: 20px;
                    background-color: #f9f9f9;
                    margin: 0 auto;
                    border-radius: 10px;
                    width: 100%;
                    max-width: 600px;
                }}
                .email-header {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px 0;
                    border-radius: 5px;
                    font-size: 24px;
                    font-weight: bold;
                }}
                .email-content {{
                    margin: 20px 0;
                }}
                .email-footer {{
                    margin-top: 30px;
                    font-size: 12px;
                    color: #888;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="email-header">
                    Login Information
                </div>
                <div class="email-content">
                    <p>Hello, {message['username']}!</p>
                    <p>We noticed a login to your account from the following IP address: <strong>{message['user_ip']}</strong></p>
                    <p>Browser: <strong>{message['browser']}</strong></p>
                </div>
                <div class="email-footer">
                    <p>If this wasn't you, please change your password.</p>
                    <p>&copy; {date.today().year} {cls._config.app.name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        msg.attach(text.MIMEText(html_content, "html"))
        await smtp.send_message(msg)

    @classmethod
    async def reset(cls, message: dict[str, str], smtp: SMTP) -> None:
        msg = multipart.MIMEMultipart("alternative")
        msg["Subject"] = "Reset Your Password"
        msg["From"] = cls._config.smtp.username
        msg["To"] = message["email"]

        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Reset Your Password</title>
            <style>
                .email-container {{
                    font-family: Arial, sans-serif;
                    color: #333;
                    text-align: center;
                    padding: 20px;
                    background-color: #f9f9f9;
                    margin: 0 auto;
                    border-radius: 10px;
                    width: 100%;
                    max-width: 600px;
                }}
                .email-header {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px 0;
                    border-radius: 5px;
                    font-size: 24px;
                    font-weight: bold;
                }}
                .email-content {{
                    margin: 20px 0;
                }}
                .reset-code {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #4CAF50;
                    margin: 20px 0;
                }}
                .email-footer {{
                    margin-top: 30px;
                    font-size: 12px;
                    color: #888;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="email-header">
                    Reset Your Password
                </div>
                <div class="email-content">
                    <p>Hello, {message['username']}!</p>
                    <p>Use the following code to reset your password:</p>
                    <div class="reset-code">{message['code']}</div>
                    <p>This code is valid for 10 minutes.</p>
                </div>
                <div class="email-footer">
                    <p>If you didn't request this, you can safely ignore this email.</p>
                    <p>&copy; {date.today().year} {cls._config.app.name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        msg.attach(text.MIMEText(html_content, "html"))
        await smtp.send_message(msg)
