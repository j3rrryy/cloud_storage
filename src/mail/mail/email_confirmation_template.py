EMAIL_CONFIRMATION_HEADER = "Email confirmation"

EMAIL_CONFIRMATION_CONTENT = """
    <p>Hello, {username}!</p>
    <p>Please confirm your email address by clicking the button below:</p>
    <a href="{confirmation_url}" class="button">Confirm email</a>
    <p>This link is valid for 3 days.</p>
"""

EMAIL_CONFIRMATION_FOOTER = """
    <p>If you did not request this, you can safely ignore this email.</p>
"""
