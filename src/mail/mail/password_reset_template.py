PASSWORD_RESET_HEADER = {
    "en": "Reset your {app_name} password 🔑",
    "ru": "Восстановление пароля {app_name} 🔑",
}

PASSWORD_RESET_CONTENT = {
    "en": """
        <p>Hi <strong>{username}</strong>,</p>
        <p>We received a request to reset your {app_name} password. Use this code to proceed:</p>
        <div class="code-box">
            <p class="reset-code">{code}</p>
        </div>
        <div class="info-box">
            <p>⏱️ Code expires in 10 minutes</p>
            <p>🔒 Never share this code with anyone</p>
        </div>
    """,
    "ru": """
        <p>Привет, <strong>{username}</strong>!</p>
        <p>Мы получили запрос на сброс пароля {app_name}. Используйте код для подтверждения:</p>
        <div class="code-box">
            <p class="reset-code">{code}</p>
        </div>
        <div class="info-box">
            <p>⏱️ Код действителен 10 минут</p>
            <p>🔒 Никому не сообщайте этот код</p>
        </div>
    """,
}

PASSWORD_RESET_FOOTER = {
    "en": '<p class="text-muted">If you didn’t request this, you can safely ignore this email.</p>',
    "ru": '<p class="text-muted">Если вы не запрашивали сброс, просто проигнорируйте это письмо.</p>',
}
