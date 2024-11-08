import serial
import smtplib
from email.mime.text import MIMEText

# Configure serial port (make sure to match the port to your Arduino's port)
ser = serial.Serial('COM5', 9600)  # Replace 'COM3' with your Arduino's port

# Email setup
smtp_server = 'smtp.gmail.com'  # For Gmail
smtp_port = 587
sender_email = '2k22cse122@kiot.ac.in'
sender_password = 'gillu567'  # Replace with app password for Gmail
receiver_email = '2k22cse136@kiot.ac.in'

def send_email():
    subject = "Fault Detected in Photodiode Light Detection System"
    body = "A fault has been detected in the photodiode light detection system: Voltage below threshold for 10 minutes."
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    # Send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Secure the connection
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Email sent!")

try:
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()  # Read a line from the Serial port
            print(line)  # Print the Serial output for debugging
            if line == "SEND_EMAIL":
                send_email()  # Send email if "SEND_EMAIL" signal is detected

except KeyboardInterrupt:
    print("Program stopped")
finally:
    ser.close()

