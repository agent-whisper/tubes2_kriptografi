from flask import Flask, url_for, redirect

app = Flask(__name__)

@app.route('/')
def index():
    return 'index'

@app.route('/auth/authorize')
def auth_creds():
    return 'auth_creds'

@app.route('/auth/revoke')
def revoke_creds():
    return 'revoke_creds'

@app.route('/auth/clear')
def clear_creds():
    return 'clear creds'

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

