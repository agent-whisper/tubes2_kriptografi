import base64
import email
import os

from bs4 import BeautifulSoup as bs
import flask
import src.google_api.authorization as auth
import src.google_api.gmail as gmail_api
import yaml

app = flask.Flask(__name__)

# Load the app configurations
try:
    with open('config.yml', 'r') as stream:
        config = yaml.safe_load(stream)
except FileNotFoundError:
    print('[main] Config file not found.')
    exit()

try:
    app.secret_key = config['app']['secret_key']
except KeyError:
    print('[main] App secret key not found; Check config file.')
    exit()

# App routes
@app.route('/')
def index():
    if not auth.is_authorized():
        return flask.redirect(flask.url_for('authorize_creds'))
    return 'index'

@app.route('/auth/authorize')
def authorize_creds():
    oauth2callback_uri = flask.url_for('oauth2callback', _external=True)
    return auth.authorize(oauth2callback_uri, config)

@app.route('/auth/oauth2callback')
def oauth2callback():
    home_uri = flask.url_for('index', _external=True)
    oauth2callback_uri = flask.url_for('oauth2callback', _external=True)
    return auth.run_oauth2(home_uri, oauth2callback_uri, config)

@app.route('/auth/revoke')
def revoke():
    return auth.revoke_creds()

@app.route('/auth/clear')
def clear_creds():
    return auth.clear_creds()

@app.route('/mails/')
def mails():
    return flask.redirect(flask.url_for('query_inbox'))

@app.route('/mails/inbox/')
def query_inbox():
    mails = gmail_api.query_mailbox(config['mail_labels']['inbox'], query='kripto')
    html = 'INBOX <br><br>'
    for m in mails:
        html += 'mail id: ' + m['id'] + '<br>'
        for h in m['payload']['headers']:
            if h['name'] == 'From':
                html += 'FROM: ' + h['value'] + '<br>'
            elif h['name'] == 'Date':
                html += 'DATE: ' + h['value'] + '<br>'
            elif h['name'] == 'Subject':
                html += 'SUBJECT: ' + h['value'] + '<br>'
        html += 'SNIPPET: ' + m['snippet'] + '<br><br>'

    return html

@app.route('/mails/<string:mail_id>')
def query_mail(mail_id):
    mail = gmail_api.query_mail(mail_id)
    if mail is not None:
        mail_html, attachments = parse_mail_html(mail_id, mail)
        print(attachments)
        return mail_html
    else:
        return 'Email was not found'

@app.route('/mails/<string:mail_id>/attachments/<string:attachment_id>')
def download_attachment(mail_id, attachment_id):
    attachment_obj = gmail_api.get_mail_attachment(mail_id, attachment_id)
    html = 'THIS IS AN ATTACHMENT IN BASE64URL<br><br>'
    html += str(attachment_obj)
    return html

@app.route('/mails/sent')
def sent_mail():
    return flask.redirect(flask.url_for('query_outbox'))
    
@app.route('/mails/outbox/')
def query_outbox():
    mails = gmail_api.query_mailbox(config['mail_labels']['outbox'], query='kripto')
    html = 'OUTBOX <br><br>'
    for m in mails:
        html += 'mail id: ' + m['id'] + '<br>'
        for h in m['payload']['headers']:
            if h['name'] == 'To':
                html += 'TO: ' + h['value'] + '<br>'
            elif h['name'] == 'Date':
                html += 'DATE: ' + h['value'] + '<br>'
            elif h['name'] == 'Subject':
                html += 'SUBJECT: ' + h['value'] + '<br>'
        html += 'SNIPPET: ' + m['snippet'] + '<br><br>'
    return html

@app.route('/mails/labels')
def query_labels():
    labels = gmail_api.query_labels()
    html = 'LABELS<br><br>'
    for l in labels:
        html += str(l) + '<br>'
    return html

@app.route('/mails/send')
def send_email():
    return 'send email'


@app.route('/cryptography/chill_cipher/encrypt')
def encrypt():
    return 'encrypt'

@app.route('/cryptography/chill_cipher/decrypt')
def decrypt():
    return 'decrypt'

@app.route('/signature/ecceg/gen_key')
def gen_key():
    return 'gen_key'

@app.route('/signature/ecceg/sign')
def create_sign():
    return 'create_sign'

@app.route('/signature/ecceg/verify')
def verify_sign():
    return 'verify_sign'

def decode_mail_data(data):
    raw = base64.urlsafe_b64decode(data.encode('ASCII'))
    mail_content = email.message_from_bytes(raw)
    return (mail_content)

def create_datastore(msg_id):
    try:
        os.mkdir('instance/datastore/' + msg_id)
    except FileExistsError:
        pass

def convert_b64url_to_b64(data):
    data_as_bytes = base64.urlsafe_b64decode(data)
    return base64.standard_b64encode(data_as_bytes)

def parse_mail_html(mail_id, mail_obj):
    html = ''
    attachments = {'mail_id': mail_id}
    attachments['items'] = []
    attachment_in_mail_index = []
    idx = 0
    for p in mail_obj['parts']:
        try:
            if p['mimeType'] == 'text/html':
                html += str(decode_mail_data(p['body']['data'])) + '<br>'
            elif p['filename'] != '':
                attachment_in_mail_index.append(idx)
        except KeyError:
            html +=  'no data <br>'
        idx += 1
    mail_html = bs(html, 'html.parser')
    for i in attachment_in_mail_index:
        embedded_img = (mail_html.find("img", alt=mail_obj['parts'][i]['filename']))
        if embedded_img is not None:
            attachment = gmail_api.get_mail_attachment(mail_id, mail_obj['parts'][i]['body']['attachmentId'])
            image_data = convert_b64url_to_b64(attachment['data'])
            embedded_img['src'] = 'data:' + mail_obj['parts'][i]['mimeType'] + ';base64,' + image_data.decode()
        else:
            attachments['items'].append({
                'name': mail_obj['parts'][i]['filename'],
                'size': attachment['size'],
                'id': mail_obj['parts'][i]['body']['attachmentId'],
            })
    return mail_html.prettify(), attachments
