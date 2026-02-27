BASE_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{header}</title>
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background-color: #f3f4f6;
                color: #111827;
                line-height: 1.6;
            }}
            .email-wrapper {{
                padding: 40px 20px;
            }}
            .email-container {{
                max-width: 520px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 16px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                overflow: hidden;
            }}
            .email-header {{
                background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
                padding: 32px 24px;
                text-align: center;
            }}
            .header-title {{
                color: #ffffff;
                font-size: 28px;
                font-weight: 700;
                margin: 0;
            }}
            .email-content {{
                padding: 32px 24px;
                text-align: left;
            }}
            .email-content {{
                margin: 0 0 16px;
                color: #374151;
                font-size: 16px;
            }}
            .email-content strong {{
                color: #111827;
            }}
            .button-wrapper {{
                text-align: center;
                margin: 28px 0;
            }}
            .button {{
                display: inline-block;
                padding: 14px 28px;
                background-color: #4f46e5;
                color: #ffffff !important;
                text-decoration: none;
                border-radius: 10px;
                font-weight: 600;
                font-size: 16px;
                transition: background-color 0.2s;
            }}
            .button:hover {{
                background-color: #4338ca;
            }}
            .code-box {{
                background-color: #f3f4f6;
                border: 2px dashed #e5e7eb;
                border-radius: 12px;
                padding: 24px;
                text-align: center;
                margin: 24px 0;
            }}
            .reset-code {{
                font-size: 36px;
                font-weight: 700;
                color: #4f46e5;
                letter-spacing: 4px;
                margin: 0;
                font-family: 'Courier New', monospace;
            }}
            .info-box {{
                background-color: #eef2ff;
                border-left: 4px solid #4f46e5;
                padding: 16px;
                border-radius: 0 8px 8px 0;
                margin: 20px 0;
            }}
            .info-box p {{
                margin: 0;
                color: #3730a3;
                font-size: 14px;
            }}
            .email-footer {{
                background-color: #f9fafb;
                padding: 24px;
                text-align: center;
                border-top: 1px solid #e5e7eb;
            }}
            .email-footer p {{
                margin: 0 0 8px;
                font-size: 13px;
                color: #6b7280;
            }}
            .email-footer .copyright {{
                font-size: 12px;
                color: #9ca3af;
            }}
            @media (prefers-color-scheme: dark) {{
                body {{
                    background-color: #111827;
                    color: #f9fafb;
                }}
                .email-container {{
                    background-color: #1f2937;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
                }}
                .email-content p {{
                    color: #d1d5db;
                }}
                .email-content strong {{
                    color: #f9fafb;
                }}
                .code-box {{
                    background-color: #374151;
                    border-color: #4b5563;
                }}
                .reset-code {{
                    color: #818cf8;
                }}
                .info-box {{
                    background-color: #312e81;
                    border-color: #4f46e5;
                }}
                .info-box p {{
                    color: #c7d2fe;
                }}
                .email-footer {{
                    background-color: #111827;
                    border-color: #374151;
                }}
                .email-footer p {{
                    color: #9ca3af;
                }}
                .email-footer .copyright {{
                    color: #6b7280;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="email-wrapper">
            <div class="email-container">
                <div class="email-header">
                    <h1 class="header-title">{header}</h1>
                </div>
                <div class="email-content">{content}</div>
                <div class="email-footer">
                    {footer}
                    <p class="copyright">&copy; {year} {app_name}. All rights reserved.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
"""
