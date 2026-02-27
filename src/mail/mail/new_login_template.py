NEW_LOGIN_HEADER = {
    "en": "New sign-in to your {app_name} account 🔐",
    "ru": "Новый вход в аккаунт {app_name} 🔐",
}

NEW_LOGIN_CONTENT = {
    "en": """
        <p>Hi <strong>{username}</strong>,</p>
        <p>We noticed a new sign-in to your {app_name} account:</p>
        <div class="info-box">
            <p>📍 <strong>Location:</strong> {country_code}</p>
            <p>🌐 <strong>IP address:</strong> {user_ip}</p>
            <p>💻 <strong>Device:</strong> {browser}</p>
        </div>
    """,
    "ru": """
        <p>Привет, <strong>{username}</strong>!</p>
        <p>Зафиксирован новый вход в ваш аккаунт {app_name}:</p>
        <div class="info-box">
            <p>📍 <strong>Страна:</strong> {country_code}</p>
            <p>🌐 <strong>IP-адрес:</strong> {user_ip}</p>
            <p>💻 <strong>Устройство:</strong> {browser}</p>
        </div>
    """,
}

NEW_LOGIN_FOOTER = {
    "en": "<p>If this wasn’t you, reset your password immediately.</p>",
    "ru": "<p>Если это были не вы, сбросьте пароль немедленно.</p>",
}
