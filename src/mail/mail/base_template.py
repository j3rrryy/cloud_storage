BASE_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{header}</title>
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
            .reset-code {{
                font-size: 32px;
                font-weight: bold;
                color: #4CAF50;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="email-header">{header}</div>
            <div class="email-content">{content}</div>
            <div class="email-footer">
                {footer}
                <p>&copy; {year} {app_name}. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
"""
