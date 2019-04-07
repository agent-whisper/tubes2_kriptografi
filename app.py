import os

import flask
import src.google_api.authorization as auth
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
    return auth.get_access_token(home_uri, oauth2callback_uri, config)

@app.route('/auth/revoke')
def revoke():
    return auth.revoke_creds()

@app.route('/auth/clear')
def clear_creds():
    return auth.clear_creds()

@app.route('/mails/inbox/')
def inbox():
    return 'inbox'

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

if __name__ == '__main__':
    # Disables OAuthlib's HTTPs verification (Required for running locally).
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    os.environ['FLASK_ENV']='development'
    ip = config['app']['ip']
    port = config['app']['port']
    app.run(ip, port, debug=True)