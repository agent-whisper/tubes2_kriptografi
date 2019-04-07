import flask
import os
import requests

import google_auth_oauthlib.flow as google_flow
import google.oauth2.credentials as google_creds

app = flask.current_app

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
            app.logger.debug('[authorization.create_flow_from_config] Success creating flow object')
        flow.redirect_uri = oauth2callback_uri
        return flow
    except KeyError as exc:
        print(exc)
        err_msg = '[authorization.create_flow_from_config] Failed to create flow object during authorization; Check configuration file.'
        app.logger.error(err_msg)
        return None

def authorize(oauth2callback_uri, config):
    flow = create_flow_from_config(oauth2callback_uri, config)
    if flow is None:
        err_msg = '[authorization.authorize] Failed to create flow object during authorization; Check configuration file.'
        return err_msg

    authorization_url, state = flow.authorization_url(
        access_type = config['oauth_config']['access_type'],
        include_granted_scopes =  config['oauth_config']['include_granted_scopes']
    )
    flask.session['state'] = state
    app.logger.debug('[authorization.authorize] success generating authorization url')
    return flask.redirect(authorization_url)

def run_oauth2(app_home_uri, oauth2callback_uri, config):
    flow = create_flow_from_config(oauth2callback_uri, config, use_state=True)
    if flow is None:
        err_msg = '[authorization.run_oauth2] Failed to create flow object when requesting access token; Check configuration file.'
        return err_msg

    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)
    flask.session['credentials'] = credentials_to_dict(flow.credentials)
    app.logger.debug('[authorization.run_oauth2] success generating credentials')
    return flask.redirect(app_home_uri)

def revoke_creds():
    if not is_authorized():
        err_msg = '[authorization.revoke_creds] User credentials do not exist'
        app.logger.debug(err_msg)
        return err_msg

    user_creds = get_user_creds()
    if user_creds is not None:
        revoke = requests.post('https://accounts.google.com/o/oauth2/revoke',
            params={'token': user_creds.token},
            headers = {'content-type': 'application/x-www-form-urlencoded'})

        status_code = getattr(revoke, 'status_code')
        if status_code == 200:
            msg = '[authorization.revoke_creds] User credential has been revoked.'
            app.logger.debug(msg)
            return msg
        else:
            msg = '[authorization.revoke_creds] An error occurred.'
            app.logger.error(msg)
            return msg
    else:
        msg = '[authorization.revoke_creds] User credential does not exist.'
        app.logger.debug(msg)
        return msg

def clear_creds():
    if is_authorized():
        del flask.session['credentials']
        app.logger.debug('[authorization.clear_creds] success clearing user credentials')
    else:
        app.logger.debug('[authorization.clear_creds] no credentials to clear')
    return 'User credentials have been cleared.'

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def get_user_creds():
    try:
        user_creds = google_creds.Credentials(
            **flask.session['credentials']
        )
        return user_creds
    except KeyError:
        app.logger.debug('[authorization.get_user_creds] no credentials found')        
        return None


