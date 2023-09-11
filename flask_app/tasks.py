from datetime import datetime, timedelta
import time
from flask import redirect, render_template, request, send_file, session, url_for
import flask
import boto3
from botocore.exceptions import ClientError
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def print_task(seconds):
    print("Starting task")
    for num in range(seconds):
        print(num, ". Hello World!")
        time.sleep(1)
    print("Task completed")


def sendWelcomeEmail():
    from app import app
    print('send welcome email')
    subject = "Welcome to Medium"
    with app.app_context():
        emailBody = flask.render_template('welcome.html', email="test@example.com", name="John")

    ses_send_single_email("test@example.com", subject, emailBody)


def ses_send_single_email(to_address, subject, html_body, attachment=None, from_address='test@example.com',
                          from_name='Notifications', reply_to_address='test@example.com',email_id=''):
    # For testing email
    cc_addresses = []
    bcc_addresses = []

    destination = dict(ToAddresses=[to_address + " <" + to_address + ">"], CcAddresses=cc_addresses,
                       BccAddresses=bcc_addresses)

    # Create a new SES resource and specify a region.
    aws_session = boto3.Session()
    client = aws_session.client('ses', region_name='add_region_name')
    try:
        if email_id != '':
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = from_address
            msg['To'] = to_address
            msg['Cc'] = ', '.join(cc_email_list)
            msg.attach(MIMEText(html_body, 'html'))
            destination = {'ToAddresses': ['test@example.com'], 'CcAddresses': [], 'BccAddresses': []}
            msg.preamble = 'Multipart message.\n'
            # attachments = Email.objects.get(id=email_id)['attachments']
            for attachment in attachments:
                part = MIMEApplication(bytes(attachment['file']))
                part.add_header('Content-Disposition', 'attachment', filename=attachment['filename'])
                msg.attach(part)

            response = client.send_raw_email(
                Source=msg['From'],
                Destinations=[to_address],
                RawMessage={'Data': msg.as_string()}
            )
        else:
            response = client.send_email(
                Destination=destination,
                Message=dict(Body=dict(Html=dict(Charset="UTF-8", Data=html_body)),
                             Subject=dict(Charset="UTF-8", Data=subject)),
                Source=from_name + " <" + from_address + ">",
                ReplyToAddresses=[reply_to_address],
            )

    except ClientError as e:
        print(e.response['Error']['Message'])

        # email logging
        from app import logger_stdout

        logger_stdout.info("-------------------------------------from exception")
        logger_stdout.info("Processing user: " + str(to_address))
        logger_stdout.info("Processing subject : " + str(subject))
        logger_stdout.info("Processing date : " + str(datetime.utcnow()))
        logger_stdout.info("Status : Failed")
        logger_stdout.info("Error message" + str(e.response['Error']['Message']))
        logger_stdout.info("-------------------------------------")

        pass
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])

        # email logging
        from app import logger_stdout

        logger_stdout.info("-------------------------------------from else")
        logger_stdout.info("Processing user: " + str(to_address))
        logger_stdout.info("Processing subject : " + str(subject))
        logger_stdout.info("Processing date : " + str(datetime.utcnow()))
        logger_stdout.info("MessageId : " + str(response.get('MessageId', '')))
        logger_stdout.info("ResponseMetadata HTTPStatusCode : " + str(response['ResponseMetadata']['HTTPStatusCode']))
        if response['ResponseMetadata']['HTTPStatusCode'] == 200 or response['ResponseMetadata'][
            'HTTPStatusCode'] == 202:
            logger_stdout.info("Status : Sent")
        else:
            logger_stdout.info("Status : Failed")
        logger_stdout.info("-------------------------------------")

        return response
