import os

from src.app import app, config

if __name__ == '__main__':
    # Disables OAuthlib's HTTPs verification (Required for running locally).
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    os.environ['FLASK_ENV']='development'
    ip = config['app']['ip']
    port = config['app']['port']
    app.run(ip, port, debug=True)