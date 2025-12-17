PASSWORD_RESET_HEADER = "Password reset"

PASSWORD_RESET_CONTENT = """
    <p>Hello, {username}!</p>
    <p>Use the following code to reset your password:</p>
    <div class="reset-code">{code}</div>
    <p>This code is valid for 10 minutes.</p>
"""

PASSWORD_RESET_FOOTER = (
    "<p>If you did not request this, you can safely ignore this email.</p>"
)
