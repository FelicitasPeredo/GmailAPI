import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import email
import base64

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']




def get_messages(service, msg_id):
    try:
        message = service.users().messages().get(userId='me', id=msg_id, format='raw').execute()
        msg_raw = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
        msg_str = email.message_from_bytes(msg_raw)
        content_type = msg_str.get_content_maintype()
        if content_type == 'multipart':
            content = msg_str.get_payload()
            plain_text = content[0].get_payload()
            html_text = content[1].get_payload()
            print(f'Message body: {plain_text}')
            return plain_text
        else:
            print(f'Message body: {msg_str.get_payload()}')
            return msg_str.get_payload()
            

    except HttpError as error:
        print(f'An error occurred: {error}')

def search_messages(service):
    try:
        search_id = service.users().messages().list(userId='me', q='PERREO').execute()
        number_results = search_id['resultSizeEstimate']
        final_list = []
        if number_results>=1:
            message_ids = search_id['messages']
            for ids in message_ids:
                final_list.append(ids['id'])
            print(final_list)
            return final_list
        else:
            print('Empty results')
    except HttpError as error:
        print(f'An error occurred: {error}')


def get_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service

service = get_service()
ids_list = search_messages(service)
if ids_list != None:
    for id in ids_list:
        get_messages(service, id)