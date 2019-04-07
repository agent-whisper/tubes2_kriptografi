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

@app.route('/mails/inbox/')
def query_inbox():
    mails = gmail_api.query_inbox(query='kripto')
    html = 'INBOX <br>'
    for m in mails:
        html += m['id'] + '<br>'
        html += m['snippet'] + '<br><br>'
    return html

@app.route('/mails/inbox/<string:mail_id>')
def query_mail(mail_id):
    # mail = gmail_api.query_mail_raw(mail_id)
    # mail_obj = decode_mail_data(mail['raw'])
    # if mail_obj.is_multipart():
    #     for payload in mail_obj.get_payload():
    #         print(payload.get_payload())
    # else:
    #     print(payload.get_payload())
    # return 'under construction'

    mail = gmail_api.query_mail(mail_id)
    attachment_index = []
    if mail is not None:
        html = ''
        idx = 0
        for p in mail['parts']:
            try:
                if p['mimeType'] == 'text/html':
                    html += str(decode_mail_data(p['body']['data'])) + '<br>'
                elif p['filename'] != '':
                    attachment = gmail_api.get_mail_attachment(mail_id, p['body']['attachmentId'])
                    p['body']['data'] = convert_b64url_to_b64(attachment['data'])
                    attachment_index.append(idx)
            except KeyError:
                html +=  'no data <br>'
            idx += 1
        mail_html = bs(html, 'html.parser')
        for i in attachment_index:
            embedded_img = (mail_html.find("img", alt=mail['parts'][i]['filename']))
            if embedded_img is not None:
                embedded_img['src'] = 'data:' + mail['parts'][i]['mimeType'] + ';base64,' + mail['parts'][i]['body']['data'].decode()
        return mail_html.prettify()
    else:
        return 'Email was not found'

@app.route('/mails/send')
def send_email():
    return 'send email'

@app.route('/mails/outbox/')
def outbox():
    return 'outbox'

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