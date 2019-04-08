import base64
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
import mimetypes
import os

import flask
import googleapiclient.discovery as google_disc
import google.auth.transport.requests as google_req
import src.google_api.authorization as auth

app = flask.current_app

def build_service():
    creds = auth.get_user_creds()
    if creds is not None:
        service = google_disc.build('gmail', 'v1', credentials=creds)
        app.logger.debug('[gmail.build_service] Success building service object')
        return service
    else:
        app.logger.error('[gmail.build_service] Failed building service object')
        return None

def query_labels():
    service = build_service()
    if service is None:
        return []
    try:
        response = service.users().labels().list(userId='me').execute()
        labels = response['labels']
        return labels
    except Exception:
        msg = ['[gmail.query_labels] Failed to query labels']
        app.logger.warning(msg)
        return []

def query_mail_ids(label_ids, query=''):
    mail_ids = []
    service = build_service()
    if service is None:
        return mail_ids

    try:
        response = service.users().messages().list(userId='me', labelIds=label_ids, q=query).execute()
        if 'messages' in response:
            mail_ids.extend(response['messages'])
        # Currently does not process page token to reduce load during development
        # while 'nextPageToken' in response:
        #     page_token = response['nextPageToken']
        #     response = service.users().messages().list(userId='me', q=query, pageToken=page_token).execute()
        #     emails.extend(response['messages'])
    except Exception as error:
        msg = '[gmail.query_inbox] An error occured: %s' % error
        app.logger.error(msg)
    app.logger.debug('[gmail.query_inbox] Finished querying mail ids')
    return mail_ids

def query_mailbox(label_ids, query=''):
    mail_ids = query_mail_ids(label_ids, query=query)
    service = build_service()
    if service is None:
        return []
    mails = []
    try:
        for m_id in mail_ids:
            mail = service.users().messages().get(userId='me', id=m_id['id']).execute()
            mails.append(mail)
    except Exception as error:
        msg = '[gmail.mailbox] An error occured: %s' % error
        app.logger.error(msg)
    app.logger.debug('[gmail.mailbox] Finished querying inbox')
    return mails

def query_mail(mail_id):
    service = build_service()
    if service is None:
        return None
    mail = None
    try:
        mail = service.users().messages().get(userId='me', id=mail_id).execute()
        parsed_mail = parse_mail(mail)
        return parsed_mail
    except Exception as error:
        msg = '[gmail.query_mail] An error occured: %s' % error
        app.logger.error(msg)
    app.logger.debug('[gmail.query_mail] Finished querying mail')
    return mail

def query_mail_raw(mail_id):
    service = build_service()
    if service is None:
        return None
    mail = None
    try:
        mail = service.users().messages().get(userId='me', id=mail_id, format='raw').execute()
    except Exception as error:
        msg = '[gmail.query_mail] An error occured: %s' % error
        app.logger.error(msg)
    app.logger.debug('[gmail.query_mail] Finished querying mail')
    return mail

def send_mail(mail_details):
    try:
        required_param = ['sender', 'to', 'subject', 'text']
        for rp in required_param:
            if rp not in mail_details:
                raise KeyError(rp)
    except KeyError as error:
        msg = '[gmail.send_mail] Mail details are incomplete: %s' % error
        app.logger.error(msg)
        return {'error' : msg}

    sender = mail_details['sender']
    to = mail_details['to']
    subject = mail_details['subject']
    msg_text = mail_details['text']
    if 'attachments' not in mail_details:
        attachments = None
    else:
        attachments = mail_details['attachments']
    msg_body = create_message(sender, to, subject, msg_text, attachment_list=attachments)
    service = build_service()
    if service is None:
        app.logger.error('[gmail.send_mail] Failed to build service')
        return None
    try:
        send_response = service.users().messages().send(userId='me', body=msg_body).execute()
        return send_response
    except Exception as error:
        msg = '[gmail.send_mail] An error occurred: %s' % error
        app.logger.error(msg)
        return {'error': msg}


def parse_mail(message_obj):
    mail_parts = {}
    mail_parts['headers'] = {}
    mail_parts['parts'] = []
    for h in message_obj['payload']['headers']:
        mail_parts['headers'][h['name']] = h['value']
    parse_mail_data(mail_parts['parts'], message_obj['payload'])
    return(mail_parts)

def parse_mail_data(data_container, message_obj):
    if 'parts' in message_obj:
        for item in message_obj['parts']:
            parse_mail_data(data_container, item)
    else:
        data_container.append(message_obj)

def get_mail_attachment(msg_id, attch_id):
    service = build_service()
    attachement = service.users().messages().attachments().get(id=attch_id, messageId=msg_id, userId='me').execute()
    return attachement

# adapted from gmail documentation
def create_message(sender, to, subject, message_text, attachment_list=None):
    """Create a message for an email.

    Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.
        attachment_list = list of path to attachment files

    Returns:
        An object containing a base64url encoded email object.
    """
    if attachment_list is not None or attachment_list != []:
        pass
        # TODO: handle attachments
        #return create_message_with_attachments(sender, to, subject, message_text, attachment_list=attachment_list)

    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['date'] = formatdate(localtime=True)
    message['subject'] = subject

    # Add text as plain text
    msg = MIMEText(message_text, 'plain')
    message.attach(msg)
    # Add text as html
    msg = MIMEText(message_text, 'html')
    message.attach(msg)
    
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

# adapted from gmail documentation
def create_message_with_attachments(sender, to, subject, message_text, attachment_list):
    """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.
    file_dir: The directory containing the file to be attached.
    filename: The name of the file to be attached.

  Returns:
    An object containing a base64url encoded email object.
  """
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['date'] = formatdate(localtime=True)
    message['subject'] = subject

    # Add text as plain text
    msg = MIMEText(message_text, 'plain')
    message.attach(msg)
    # Add text as html
    msg = MIMEText(message_text, 'html')
    message.attach(msg)

    for path in attachment_list:
        content_type, encoding = mimetypes.guess_type(path)
        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'
            main_type, sub_type = content_type.split('/', 1)

        if main_type == 'text':
            fp = open(path, 'rb')
            msg = MIMEText(fp.read(), _subtype=sub_type)
            fp.close()
        elif main_type == 'image':
            fp = open(path, 'rb')
            msg = MIMEImage(fp.read(), _subtype=sub_type)
            fp.close()
        elif main_type == 'audio':
            fp = open(path, 'rb')
            msg = MIMEAudio(fp.read(), _subtype=sub_type)
            fp.close()
        else:
            fp = open(path, 'rb')
            msg = MIMEBase(main_type, sub_type)
            msg.set_payload(fp.read())
            fp.close()

        msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(path))
        message.attach(msg)

    return {'raw': base64.urlsafe_b64encode(message.as_bytes().decode())}