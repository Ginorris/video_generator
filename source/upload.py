import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


SCOPES = ['https://www.googleapis.com/auth/drive.file']


def authenticate_google_drive():
    """
    returns credentials if the JWT exists and its valid, 
    else refreshes the JWT or prompts the user to log in.
    """
    creds = None    
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no valid credentials available, prompt the user to log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

    return creds


def upload_file(service, file_path, file_name):
    file_metadata = {'name': file_name}
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f'File ID: {file.get("id")}')


def main():
    # Authenticate and build the service
    creds = authenticate_google_drive()
    service = build('drive', 'v3', credentials=creds)

    # Specify the file to upload
    file_path = r'C:\Users\rizzu\Documents\Projects\tiktok\app\media\to_post\feb\02-02-2024\1adpebu.mp4'
    file_name = 'uploaded_file.ext'

    # Upload the file
    upload_file(service, file_path, file_name)


if __name__ == '__main__':
    main()


