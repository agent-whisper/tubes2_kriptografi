import base64
import email
import os

from bs4 import BeautifulSoup as bs
import flask
import src.google.api.authorization as auth
import src.google.api.gmail as gmail_api
import yaml

app = flask.Flask(__name__)

# Load the app configurations
try:
    with open('config.yml', 'r') as stream:
        config = yaml.safe_load(stream)
except FileNotFoundError:
    app.logger.error('[main] Config file not found.')
    exit()

try:
    app.secret_key = config['app']['secret_key']
except KeyError:
    app.logger.error('[main] App secret key not found; Check config file.')
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
        return mail_html
    else:
        return 'Email was not found'

@app.route('/mails/<string:mail_id>/attachments/<string:attachment_id>')
def download_attachment(mail_id, attachment_id):
    attachment_obj = gmail_api.get_mail_attachment(mail_id, attachment_id)
    html = 'THIS IS AN ATTACHMENT IN BASE64URL<br><br>'
    html += str(attachment_obj)
    return html

@app.route('/mails/sent/')
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
    mail_details = {}
    mail_details['sender'] = flask.session['credentials']['client_id']
    mail_details['to'] = '13515050@std.stei.itb.ac.id'
    mail_details['subject'] = 'tubes 2 kripto; test send message'

    """ Embed images do not show up when viewed from gmail because the image is standard base64 (not base64url) """
    mail_details['text'] = 'test sending message from python script <3<br><img alt="small2.png" height="128" src="data:image/png;base64,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" width="128"/>'

    mail_details['attachments'] = []
    mail_details['attachments'].append('/home/fariz/Documents/kuliah/semester8/kripto/tubes2_kriptografi/instance/key.png')
    mail_details['attachments'].append('/home/fariz/Documents/kuliah/semester8/kripto/tubes2_kriptografi/instance/opm.jpeg')
    send_response = gmail_api.send_mail(mail_details)

    if send_response is None:
        return 'Send message failed :('
    elif 'error' in send_response:
        return send_response['error']
    html = 'SEND RESPONSE<br><br>'
    html += str(send_response)
    return html


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

# Utility functions
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
        print(mail_obj['parts'][i])
        if embedded_img is not None:
            attachment = gmail_api.get_mail_attachment(mail_id, mail_obj['parts'][i]['body']['attachmentId'])
            image_data = convert_b64url_to_b64(attachment['data'])
            embedded_img['src'] = 'data:' + mail_obj['parts'][i]['mimeType'] + ';base64,' + image_data.decode()
        else:
            attachments['items'].append({
                'name': mail_obj['parts'][i]['filename'],
                'size': mail_obj['parts'][i]['body']['size'],
                'id': mail_obj['parts'][i]['body']['attachmentId'],
            })
    return mail_html.prettify(), attachments
