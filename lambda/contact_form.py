import json
import boto3
import os

ses = boto3.client('ses', region_name='eu-west-1')

SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
RECIPIENT_EMAIL = os.environ.get('RECIPIENT_EMAIL')

def lambda_handler(event, context):

    if event.get('requestContext', {}).get('http', {}).get('method') == 'OPTIONS':
        return cors_response(200, 'OK')

    try:
        body = json.loads(event.get('body', '{}'))
        name = body.get('name', '').strip()
        email = body.get('email', '').strip()
        subject = body.get('subject', 'No subject').strip()
        message = body.get('message', '').strip()

        if not all([name, email, message]):
            return cors_response(400, json.dumps({
                'error': 'Name, email and message are required'
            }))

        ses.send_email(
            Source=SENDER_EMAIL,
            Destination={'ToAddresses': [RECIPIENT_EMAIL]},
            Message={
                'Subject': {
                    'Data': f'Portfolio Contact: {subject} — from {name}'
                },
                'Body': {
                    'Text': {
                        'Data': (
                            f"Name: {name}\n"
                            f"Email: {email}\n"
                            f"Subject: {subject}\n\n"
                            f"Message:\n{message}"
                        )
                    },
                    'Html': {
                        'Data': f"""
                        <html>
                        <body style="font-family:Arial,sans-serif;max-width:600px">
                          <h2 style="color:#0D4F47">New Portfolio Message</h2>
                          <p><strong>From:</strong> {name}</p>
                          <p><strong>Email:</strong> <a href="mailto:{email}">{email}</a></p>
                          <p><strong>Subject:</strong> {subject}</p>
                          <hr/>
                          <p><strong>Message:</strong></p>
                          <p style="background:#f5f5f5;padding:1rem;border-radius:4px">{message}</p>
                          <hr/>
                          <small style="color:#999">Sent from Charity Maina Portfolio</small>
                        </body>
                        </html>
                        """
                    }
                }
            }
        )

        return cors_response(200, json.dumps({'message': 'Message sent successfully!'}))

    except Exception as e:
        print(f"Error: {str(e)}")
        return cors_response(500, json.dumps({'error': str(e)}))


def cors_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST,OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Content-Type': 'application/json'
        },
        'body': body
    }
