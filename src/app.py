import base64
import email
import os

from bs4 import BeautifulSoup as bs
import flask
from src.cryptography.chill_cipher.chill import Chill
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
    # TODO: read these three from request
    try_decrypt = True
    key = 'ChillKey'
    show = 'text'

    if (try_decrypt and key == ''):
        return 'Error: No key provided'
    if mail is not None:
        mail_parts = parse_mail(mail_id, mail)
        if show == 'text':
            if try_decrypt:
                mail_content = decrypt_text(mail_parts['text'], key)
            else:
                mail_content = mail_parts['text']
        elif show == 'html':
            mail_content = mail_parts['html']
            mail_content = insert_embed_img(mail_id, mail_parts['attachments'], mail_content)
        return mail_content
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
    # TODO: Fill these two from request
    use_encryption = True
    key = 'ChillKey'

    # TODO: Fill the mail details from requests
    mail_details = {}
    mail_details['sender'] = flask.session['credentials']['client_id']
    mail_details['to'] = '13515050@std.stei.itb.ac.id'
    mail_details['subject'] = 'TUBES 2 KRIPTO - AFTER CIPHER'

    """ Embed images do not show up when viewed from gmail because the image is standard base64 (not base64url) """
    mail_details['html'] = '<h1>THIS IS A PLACEHOLDER HTML</h1><img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAMAAAApB0NrAAAAV1BMVEX///+VyOyByITK4/Wp0vDA48Hr9fvv+PCcy+3Q6tHy+P2Jy4yRz5Oh1qOiz+7f8eDk8fqZ0puw3bKw1vHE4PTQ5/f4/P6p2au44LrI58nX7tjn9ej3/Pfv4affAAAApElEQVR42t2SyQ6DMAwFAyEbCQ103/7/O3vAxiovQVzbuVkaafQkq59BNzPeVpWxYfqacj2wolWNMyvdjpLdWXJm5rlRerWE2ygN5BhxYFMgJ75Z0bgpkRTotoVNhpxEdyelBdcSGUrCkZwblIQs87HETOTcS6XV/IQlIfJ6LK3mD7WSzI9uKXn4PZr/kNJFFchfpZMqMkEJCQZKCJaQ3kvpD/gA5qQFlI8k1AIAAAAASUVORK5CYII=" alt="varvy.com" class=logo width="30" height="30"/>'
    
    with open('test_email.txt', 'r') as f:
        mail_details['text'] = f.read()        
    # TODO: Sign the mail text
    # give_sign = True
    # if (give_sign):
    #     mail_details['text'] = ecceg.sign(mail_details['text'], key)
    if (use_encryption):
        mail_details['text'] = encrypt_text(mail_details['text'], key)
    
    # TODO: Add attachments from client upload
    mail_details['attachments'] = []
    mail_details['attachments'].append('/home/fariz/Documents/kuliah/semester8/kripto/tubes2_kriptografi/instance/key.png')
    mail_details['attachments'].append('/home/fariz/Documents/kuliah/semester8/kripto/tubes2_kriptografi/instance/opm.jpeg')
    send_response = gmail_api.send_mail(mail_details)
    html = ''
    
    if send_response is None:
        return 'Send message failed :('
    elif 'error' in send_response:
        return send_response['error']
    html = 'SEND RESPONSE<br><br>'
    html += str(send_response) + '<br>'
    
    html += 'Content:<br>'
    html += str(mail_details)
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
def decode_mail_data(data, double_encoded=False):
    raw = base64.urlsafe_b64decode(data)
    raw = base64.urlsafe_b64decode(raw.decode())
    return raw.decode()

def create_datastore(msg_id):
    try:
        os.mkdir('instance/datastore/' + msg_id)
    except FileExistsError:
        pass

def convert_b64url_to_b64(data):
    data_as_bytes = base64.urlsafe_b64decode(data)
    return base64.standard_b64encode(data_as_bytes)

def parse_mail(mail_id, mail_obj):
    mail_parts = {}
    mail_parts['mail_id'] = mail_id
    mail_parts['text'] = ''
    mail_parts['html'] = ''
    mail_parts['attachments'] = []
    idx = 0
    attachment_in_mail_index = []
    for p in mail_obj['parts']:
        if p['mimeType'] == 'text/plain':
            mail_parts['text'] = (decode_mail_data(p['body']['data']))
        elif p['mimeType'] == 'text/html':
            mail_parts['html'] = (decode_mail_data(p['body']['data']))
        elif p['filename'] != '':
            attachment_in_mail_index.append(idx)
        idx += 1
        
    mail_parts['attachments'] = []
    for i in attachment_in_mail_index:
        mail_parts['attachments'].append({
            'name': mail_obj['parts'][i]['filename'],
            'size': mail_obj['parts'][i]['body']['size'],
            'id': mail_obj['parts'][i]['body']['attachmentId'],
            'type':mail_obj['parts'][i]['mimeType']
        })
    return mail_parts

def insert_embed_img(mail_id, attachment_list, html):
    mail_html = bs(html, 'html.parser')
    for att in attachment_list:
        embedded_img = (mail_html.find("img", alt=att['name']))
        if embedded_img is not None:
            attachment = gmail_api.get_mail_attachment(mail_id, att['id'])
            image_data = convert_b64url_to_b64(attachment['data'])
            embedded_img['src'] = 'data:' + att['type'] + ';base64,' + image_data.decode()
    return mail_html.prettify()

def encrypt_text(text, key):
    ch = Chill(plain_text=text, key=key)
    ch.encrypt()
    return ch.cipher_text

def decrypt_text(text, key):
    ch = Chill(plain_text='this is just a placeholder!', cipher_text=text, key=key)
    ch.decrypt()
    return ch.plain_text

def write_to_file(content, filedir):
    with open(filedir, 'w') as f:
        f.write(content)