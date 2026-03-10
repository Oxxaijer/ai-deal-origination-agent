import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()


def send_email_alert(deal: dict):
    enabled = os.getenv("EMAIL_ALERTS", "false").lower() == "true"
    if not enabled:
        return False, "Email alerts are disabled."

    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    alert_to_email = os.getenv("ALERT_TO_EMAIL")

    subject = f"High-Scoring Deal Alert: {deal.get('company_name', 'Unknown Company')}"

    body = f"""
Company: {deal.get('company_name')}
Industry: {deal.get('industry')}
Event Type: {deal.get('event_type')}
Funding Detected: {deal.get('funding_detected')}
Funding Amount: {deal.get('funding_amount')}
Region: {deal.get('country_or_region')}
Overall Score: {deal.get('overall_score')}
Investment Signal: {deal.get('investment_signal')}

Summary:
{deal.get('summary')}

Reasoning:
{deal.get('reasoning')}

Article:
{deal.get('url')}
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = smtp_username
    msg["To"] = alert_to_email

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, [alert_to_email], msg.as_string())
        server.quit()
        return True, "Email alert sent."
    except Exception as e:
        return False, str(e)