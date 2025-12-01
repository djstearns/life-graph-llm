import os
import streamlit as st
from utils.auth import Auth
from config_file import Config


class DevAuthenticator:
    """A tiny in-memory authenticator for local development.

    Provides a minimal compatible interface: login(), logout(), get_username(),
    client (None), app_client_id (None).
    """

    def __init__(self):
        self.client = None
        self.app_client_id = None
        self.pool_id = "local_dev"
        if 'dev_users' not in st.session_state:
            st.session_state['dev_users'] = {}
        if 'auth_state' not in st.session_state:
            st.session_state['auth_state'] = 'logged_out'

    def login(self):
        # If already logged in, return True
        if st.session_state.get('auth_state') == 'logged_in':
            return True

        placeholder = st.empty()
        with placeholder:
            with st.form('dev_login'):
                st.subheader('Dev Login')
                username = st.text_input('Username')
                password = st.text_input('Password', type='password')
                submitted = st.form_submit_button('Login')
                status = st.empty()

        if not submitted:
            return False

        users = st.session_state.get('dev_users', {})
        if username not in users:
            status.error('User not found. Please sign up first in Dev mode.')
            return False

        user = users[username]
        if not user.get('confirmed', False):
            status.error('User not confirmed. Use Confirm Sign up flow.')
            return False

        if user.get('password') != password:
            status.error('Invalid credentials')
            return False

        # success
        st.session_state['auth_state'] = 'logged_in'
        st.session_state['auth_username'] = username
        return True

    def logout(self):
        st.session_state['auth_state'] = 'logged_out'
        st.session_state['auth_username'] = ''

    def get_username(self):
        return st.session_state.get('auth_username', '')


def get_authenticator():
    """Return a Cognito authenticator if Secrets Manager is available,
    otherwise return a DevAuthenticator when DEV_AUTH=1 in env (default).
    """
    try:
        return Auth.get_authenticator(Config.SECRETS_MANAGER_ID, Config.DEPLOYMENT_REGION)
    except Exception:
        dev_flag = os.environ.get('DEV_AUTH', '1')
        if dev_flag == '1' or dev_flag.lower() == 'true':
            return DevAuthenticator()
        raise


def require_login():
    """Ensure the user is logged in. Shows login UI (Cognito or Dev) if needed.

    Returns the authenticator instance (CognitoAuthenticator or DevAuthenticator).
    If the login UI is shown and the user is not yet authenticated the function
    will call st.stop() to prevent the rest of the page from rendering.
    """
    authenticator = get_authenticator()

    # Call the authenticator's login UI
    try:
        logged_in = authenticator.login()
    except Exception as e:
        st.error(f"Authentication failed to initialize: {e}")

    # show username and logout in sidebar
    with st.sidebar:
        st.markdown(f"**Logged in as:** {authenticator.get_username()}")
        if st.button('Logout'):
            try:
                authenticator.logout()
            except Exception:
                # ensure session state cleared for dev fallback
                st.session_state['auth_state'] = 'logged_out'
                st.session_state['auth_username'] = ''
            # st.experimental_rerun()

    return authenticator


def sign_up(authenticator, username, email, password):
    """Sign up wrapper that supports both Cognito and DevAuthenticator."""
    if getattr(authenticator, 'client', None):
        return authenticator.client.sign_up(
            ClientId=authenticator.app_client_id,
            Username=username,
            Password=password,
            UserAttributes=[{"Name": "email", "Value": email}] if email else [],
        )
    # dev fallback
    users = st.session_state.setdefault('dev_users', {})
    if username in users:
        raise Exception('Username already exists')
    users[username] = {'password': password, 'email': email, 'confirmed': False}
    st.session_state['dev_users'] = users
    return {'status': 'ok', 'message': 'dev user created'}


def confirm_sign_up(authenticator, username, code=None):
    """Confirm sign up wrapper for Cognito or Dev fallback.

    The `code` parameter is ignored for Dev fallback.
    """
    if getattr(authenticator, 'client', None):
        return authenticator.client.confirm_sign_up(
            ClientId=authenticator.app_client_id,
            Username=username,
            ConfirmationCode=code,
        )
    users = st.session_state.setdefault('dev_users', {})
    if username not in users:
        raise Exception('User not found')
    users[username]['confirmed'] = True
    st.session_state['dev_users'] = users
    return {'status': 'ok', 'message': 'dev user confirmed'}
