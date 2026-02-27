EMAIL_CONFIRMATION_HEADER = {
    "en": "Welcome to {app_name}! ✨",
    "ru": "Добро пожаловать в {app_name}! ✨",
}

EMAIL_CONFIRMATION_CONTENT = {
    "en": """
        <p>Hi <strong>{username}</strong>,</p>
        <p>Thanks for joining {app_name}! We're excited to have you on board.</p>
        <p>Please confirm your email address to get started:</p>
        <div class="button-wrapper">
            <a href="{confirmation_url}" class="button">Confirm email address</a>
        </div>
        <div class="info-box">
            <p>⏱️ This link expires in 3 days.</p>
        </div>
    """,
    "ru": """
        <p>Привет, <strong>{username}</strong>!</p>
        <p>Спасибо, что присоединились к {app_name}! Мы рады вас видеть.</p>
        <p>Подтвердите email, чтобы начать работу:</p>
        <div class="button-wrapper">
            <a href="{confirmation_url}" class="button">Подтвердить email</a>
        </div>
        <div class="info-box">
            <p>⏱️ Ссылка действительна 3 дня.</p>
        </div>
    """,
}

EMAIL_CONFIRMATION_FOOTER = {
    "en": '<p class="text-muted">If you didn’t create this account, you can safely ignore this email.</p>',
    "ru": '<p class="text-muted">Если вы не создавали аккаунт, просто проигнорируйте это письмо.</p>',
}
