import os
from datetime import date
from email.mime import text
from email.mime.multipart import MIMEMultipart

import pytest

from dto import InfoMailDTO, ResetMailDTO, VerificationMailDTO
from mail import MailSender

from .mocks import BROWSER, CODE, EMAIL, USER_IP, USERNAME, VERIFICATION_TOKEN


@pytest.mark.asyncio
async def test_verification(mock_smtp):
    mail = VerificationMailDTO(USERNAME, EMAIL, VERIFICATION_TOKEN)

    await MailSender.verification(mail, mock_smtp)
    mock_smtp.send_message.assert_awaited_once()

    msg = mock_smtp.send_message.call_args[0][0]
    assert isinstance(msg, MIMEMultipart)
    assert msg["Subject"] == "Confirm Your Email"
    assert msg["From"] == os.environ["MAIL_USERNAME"]
    assert msg["To"] == mail.email

    payload = msg.get_payload()
    assert isinstance(payload, list)
    assert len(payload) == 1

    verification_url = os.environ["VERIFICATION_URL"] + mail.verification_token
    expected_html = f"""
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
                    <p>Hello, {mail.username}!</p>
                    <p>Please confirm your email address by clicking the button below:</p>
                    <a href="{verification_url}" class="button">Confirm Email</a>
                    <p>This link is valid for 3 days.</p>
                </div>
                <div class="email-footer">
                    <p>If you didn't request this, you can safely ignore this email.</p>
                    <p>&copy; {date.today().year} {os.environ["APP_NAME"]}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

    assert isinstance(payload[0], text.MIMEText)
    actual_html_bytes = payload[0].get_payload(decode=True)
    charset = payload[0].get_content_charset() or "utf-8"
    actual_html = bytes(actual_html_bytes).decode(charset)

    assert actual_html == expected_html


@pytest.mark.asyncio
async def test_info(mock_smtp):
    mail = InfoMailDTO(USERNAME, EMAIL, USER_IP, BROWSER)

    await MailSender.info(mail, mock_smtp)
    mock_smtp.send_message.assert_awaited_once()

    msg = mock_smtp.send_message.call_args[0][0]
    assert isinstance(msg, MIMEMultipart)
    assert msg["Subject"] == "Login Information"
    assert msg["From"] == os.environ["MAIL_USERNAME"]
    assert msg["To"] == mail.email

    payload = msg.get_payload()
    assert isinstance(payload, list)
    assert len(payload) == 1

    expected_html = f"""
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
                    <p>Hello, {mail.username}!</p>
                    <p>We noticed a login to your account from the following IP address: <strong>{mail.user_ip}</strong></p>
                    <p>Browser: <strong>{mail.browser}</strong></p>
                </div>
                <div class="email-footer">
                    <p>If this wasn't you, please change your password.</p>
                    <p>&copy; {date.today().year} {os.environ["APP_NAME"]}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

    assert isinstance(payload[0], text.MIMEText)
    actual_html_bytes = payload[0].get_payload(decode=True)
    charset = payload[0].get_content_charset() or "utf-8"
    actual_html = bytes(actual_html_bytes).decode(charset)

    assert actual_html == expected_html


@pytest.mark.asyncio
async def test_reset(mock_smtp):
    mail = ResetMailDTO(USERNAME, EMAIL, CODE)

    await MailSender.reset(mail, mock_smtp)
    mock_smtp.send_message.assert_awaited_once()

    msg = mock_smtp.send_message.call_args[0][0]
    assert isinstance(msg, MIMEMultipart)
    assert msg["Subject"] == "Reset Your Password"
    assert msg["From"] == os.environ["MAIL_USERNAME"]
    assert msg["To"] == mail.email

    payload = msg.get_payload()
    assert isinstance(payload, list)
    assert len(payload) == 1

    expected_html = f"""
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
                    <p>Hello, {mail.username}!</p>
                    <p>Use the following code to reset your password:</p>
                    <div class="reset-code">{mail.code}</div>
                    <p>This code is valid for 10 minutes.</p>
                </div>
                <div class="email-footer">
                    <p>If you didn't request this, you can safely ignore this email.</p>
                    <p>&copy; {date.today().year} {os.environ["APP_NAME"]}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

    assert isinstance(payload[0], text.MIMEText)
    actual_html_bytes = payload[0].get_payload(decode=True)
    charset = payload[0].get_content_charset() or "utf-8"
    actual_html = bytes(actual_html_bytes).decode(charset)

    assert actual_html == expected_html
