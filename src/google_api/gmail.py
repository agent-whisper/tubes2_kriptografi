import base64
import email

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
        print(response)
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
