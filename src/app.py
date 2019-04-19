import base64
import email
import os
import json
import uuid

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
    return flask.redirect(flask.url_for('inbox'))

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

@app.route('/logout')
def logout():
    clear_creds()
    return flask.redirect(flask.url_for('index'))

@app.route('/mails/')
def mails():
    return flask.redirect(flask.url_for('query_inbox'))

@app.route('/mails/inbox/')
def query_inbox():
    mails = gmail_api.query_mailbox(config['mail_labels']['inbox'], query='kripto')
    result = []
    for m in mails:
        mail = {}
        mail['mail_id'] = m['id']
        for h in m['payload']['headers']:
            if h['name'].lower() == 'from':
                mail['from'] = h['value']
            elif h['name'].lower() == 'date':
                mail['date'] = h['value']
            elif h['name'].lower() == 'subject':
                mail['subject'] = h['value']
        mail['snippet'] = m['snippet']
        result.append(mail)

    return json.dumps({
        'data': result,
        'status': 'OK'
    })

@app.route('/mails/<string:mail_id>')
def query_mail(mail_id):
    mail = gmail_api.query_mail(mail_id)
    # TODO: read these three from request
    try_decrypt = False
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
        return str(mail)
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
    result = []
    for m in mails:
        mail = {}
        mail['mail_id'] = m['id']
        for h in m['payload']['headers']:
            if h['name'].lower() == 'to':
                mail['to'] = h['value']
            elif h['name'].lower() == 'date':
                mail['date'] = h['value']
            elif h['name'].lower() == 'subject':
                mail['subject'] = h['value']
        mail['snippet'] = m['snippet']
        result.append(mail)

    return json.dumps({
        'data': result,
        'status': 'OK'
    })

@app.route('/mails/labels')
def query_labels():
    labels = gmail_api.query_labels()
    html = 'LABELS<br><br>'
    for l in labels:
        html += str(l) + '<br>'
    return html

@app.route('/mails/send', methods=['POST'])
def send_email():
    if not auth.is_authorized():
        return flask.redirect(flask.url_for('authorize_creds'))
    use_encryption = False if flask.request.form['is_encrypt'] == 'false' else True
    encryption_key = flask.request.form['encryption_key']
    mail_details = {}
    mail_details['sender'] = flask.session['credentials']['client_id']
    mail_details['to'] = flask.request.form['mail_to']
    mail_details['subject'] = flask.request.form['subject']
    mail_details['html'] = ''
    mail_details['text'] = flask.request.form['content']
    # TODO: Sign the mail text
    # give_sign = True
    # if (give_sign):
    #     mail_details['text'] = ecceg.sign(mail_details['text'], key)
    if (use_encryption):
        mail_details['text'] = encrypt_text(mail_details['text'], encryption_key)
    
    # save temp
    filenames = []
    try:
        os.mkdir('temp')
    except FileExistsError:
        pass
    for i in range(0, int(flask.request.form['attachment_count'])):
        file = flask.request.files['file'+ str(i)]
        path = os.path.join(os.getcwd(), 'temp/' + str(uuid.uuid4()) + file.filename)
        filenames.append(path)
        file.save(path)
        print('saved')

    mail_details['attachments'] = []
    for filename in filenames:
        mail_details['attachments'].append(filename)

    send_response = gmail_api.send_mail(mail_details)

    # delete temp
    for filename in filenames:
        if os.path.exists(filename):
          os.remove(filename)
    
    if send_response is None:
        return json.dumps({
            'msg': 'Send mail failed :(',
            'status': 'ERROR'
        })
    elif 'error' in send_response:
        return json.dumps({
            'msg': send_response['error'],
            'status': 'ERROR'
        })
    return json.dumps({
        'msg': send_response,
        'status': 'OK'
    })

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

@app.route('/inbox')
def inbox():
    return flask.render_template('inbox.html')

@app.route('/outbox')
def main():
    return flask.render_template('sent.html')

@app.route('/compose')
def compose():
    return flask.render_template('compose.html')

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
