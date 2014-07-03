#! /usr/bin/python

# Feign ignorance.
link.put(":No file uploaded.")
link.put("done")

# Delete all the data.
os.system("shred data/storage")

# Send an email, to indicate that you were coerced.
import smtplib
from email.mime.text import MIMEText

msg = MIMEText("Emergency callout.")
msg["Subject"] = "Emergency callout."

s = smtplib.SMTP("smtp.example.com")
s.sendmail("callout@example.com", ["confidant@example.com"], msg.as_string())
s.quit()

