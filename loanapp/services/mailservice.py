# yourappname/services.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_email(subject, template_name, context, recipient_list):
    # Render HTML content from the template
    html_message = render_to_string(template_name, context)

    # Extract text content by stripping HTML tags
    text_message = strip_tags(html_message)

    # Send the email with both HTML and plain text versions
    send_mail(subject, text_message, 'your-email@example.com', recipient_list, html_message=html_message, fail_silently=False)
