from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import config

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

youtube_service = None
flow = None

def get_auth_url():
    global flow
    flow = Flow.from_client_config(
        config.CLIENT_SECRET_JSON,
        scopes=SCOPES,
        redirect_uri='urn:ietf:wg:oauth:2.0:oob'
    )

    auth_url, _ = flow.authorization_url(prompt='consent')
    return auth_url

def get_authenticated_service():
    global youtube_service, flow
    if youtube_service is not None:
        return youtube_service, flow.credentials.token

    if flow is None:
        raise ValueError("Flow is not initialized. Call get_auth_url() first.")

    if not config.AUTH_CODE:
        raise ValueError("Authorization code not provided")

    flow.fetch_token(code=config.AUTH_CODE)
    credentials = flow.credentials
    youtube_service = build("youtube", "v3", credentials=credentials)
    return youtube_service, credentials.token
