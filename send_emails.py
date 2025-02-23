import smtplib
import pandas as pd
import json
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from tqdm import tqdm
from termcolor import colored

def load_smtp_config():
    with open('config/smtp_config.json', 'r') as file:
        return json.load(file)

def send_email(smtp_config, to_address, subject, body, attachments=[]):
    msg = MIMEMultipart()
    msg['From'] = smtp_config['username']
    msg['To'] = to_address
    msg['Subject'] = subject

    tracking_pixel_url = f"http://yourserver.com/tracking_pixel?email={to_address}"
    body_with_tracking = body.replace("{{tracking_pixel}}", tracking_pixel_url)
    unique_link = f"http://yourserver.com/click?email={to_address}"
    body_with_tracking = body_with_tracking.replace("{{unique_link}}", unique_link)
    
    msg.attach(MIMEText(body_with_tracking, 'html'))

    for attachment in attachments:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(attachment, 'rb').read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={attachment}')
        msg.attach(part)

    try:
        server = smtplib.SMTP(smtp_config['host'], smtp_config['port'])
        server.starttls()
        server.login(smtp_config['username'], smtp_config['password'])
        server.sendmail(smtp_config['username'], to_address, msg.as_string())
        server.quit()
        print(colored(f"Email sent to {to_address}", 'green'))
    except Exception as e:
        print(colored(f"Failed to send email to {to_address}: {e}", 'red'))

def rotate_smtp_config(smtp_configs, index):
    return smtp_configs[index % len(smtp_configs)]

def load_email_list(file_path):
    return pd.read_csv(file_path)

def main():
    smtp_configs = load_smtp_config()['smtp_servers']
    email_list = load_email_list('data/email_list.csv')

    for index, row in tqdm(email_list.iterrows(), total=email_list.shape[0], desc="Processing emails"):
        smtp_config = rotate_smtp_config(smtp_configs, index)
        send_email(
            smtp_config,
            row['email'],
            "Subject",
            open('config/email_templates/template1.html').read(),
            ['data/attachments/file1.pdf']
        )
        time.sleep(10)  # Add a 10-second delay between emails to avoid being flagged as spam

if __name__ == "__main__":
    main()
