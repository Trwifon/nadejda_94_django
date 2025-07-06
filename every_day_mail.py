import os
import smtplib
import schedule
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def send_email():
    sender_email = "nad94@abv.bg"
    receiver_email = "nad94@abv.bg"
    subject = "Daily dump"
    body = "Please find the attached document."
    password = "pinacle"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    filename = "dump_records.sql"  # Specify your file path
    attachment = open("d:\postgre_dump\dump_records.sql", "rb")

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f"attachment; filename= {filename}")

    msg.attach(part)

    server = smtplib.SMTP_SSL('smtp.abv.bg', 465)
    server.login(sender_email, password)

    text = msg.as_string()
    server.sendmail(sender_email, receiver_email, text)
    server.quit()

    print("Email sent successfully!")

    return

def dump_postgre_db():
    os.system('SET PGPASSWORD = Proba123+')
    os.system('D:\Postgre_dump\dump_new')
    print("Postgre dumped successfully!")

    return

schedule.every().day.at("17:30").do(dump_postgre_db) #make dump
schedule.every().day.at("17:31").do(send_email) # send_email


while True:
    schedule.run_pending()