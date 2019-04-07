import flask
import os
import requests

import google_auth_oauthlib.flow as google_flow
import google.oauth2.credentials as google_creds

def is_authorized():
    return 'credentials' in flask.session

def create_flow_from_config(oauth2callback_uri, config, use_state=False):
    # Load authorization service configuration
    try:
        client_secret_dir = config['client_secret_dir']
        scopes = config['scopes']
        # Set authorization parameters
        if use_state:
            flow = google_flow.InstalledAppFlow.from_client_secrets_file(
                client_secret_dir,
                scopes,
                state=flask.session['state']
            )
        else:
            flow = google_flow.InstalledAppFlow.from_client_secrets_file(
                client_secret_dir,
                scopes,
            )
        flow.redirect_uri = oauth2callback_uri
        return flow
    except KeyError as exc:
        print(exc)
        return None

def authorize(oauth2callback_uri, config):
    flow = create_flow_from_config(oauth2callback_uri, config)
    if flow is None:
        return '[authorization.authorize] Failed to create flow object during authorization; Check configuration file.'

    authorization_url, state = flow.authorization_url(
        access_type = config['oauth_config']['access_type'],
        include_granted_scopes =  config['oauth_config']['include_granted_scopes']
    )
    flask.session['state'] = state
    return flask.redirect(authorization_url)

def get_access_token(app_home_uri, oauth2callback_uri, config):
    flow = create_flow_from_config(oauth2callback_uri, config, use_state=True)
    if flow is None:
        return '[authorization.get_access_token] Failed to create flow object when requesting access token; Check configuration file.'

    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)
    flask.session['credentials'] = credentials_to_dict(flow.credentials)

    return flask.redirect(app_home_uri)

def revoke_creds():
    if not is_authorized():
        return 'User credentials do not exist.'

    user_creds = google_creds.Credentials(
        **flask.session['credentials']
    )

    revoke = requests.post('https://accounts.google.com/o/oauth2/revoke',
        params={'token': user_creds.token},
        headers = {'content-type': 'application/x-www-form-urlencoded'})

    status_code = getattr(revoke, 'status_code')
    if status_code == 200:
        return 'User credential has been revoked.'
    else:
        return '[authorization.revoke_creds] An error occurred.'

def clear_creds():
    if is_authorized():
        del flask.session['credentials']
    return 'User credentials have been cleared.'

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}
