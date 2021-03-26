# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START drive_quickstart]
from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/drive']

def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
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
    service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API
    results_id = "1-Dg3F45vqORbB9wY-zmI-8WttOK8JaQlnIfE48l96mc"
    folder_id = "1RW4Eqrg-bbDv29ezJdyBggHAyHeWgqkq"
    file_id = "1aKlM6mZCSWie7IAZ_GcI1ZEY1HKtMVYKubNnYmNCrnw"
    res = service.files().list(q="name='M1_S2project_deliverySystemOptimization'").execute()
    res = service.files().export(fileId=file_id, mimeType="text/plain").execute()

    res = service.files().list(q="name='results' and '{}' in parents".format(folder_id)).execute()
    print(res)

    file_metadata = {
        'name': "results",
        'mimiType': "application/vnd.google-apps.spreadsheet",
    }

    media = MediaFileUpload(filename="test.csv",mimetype="text/csv")
    res = service.files().update(fileId= results_id, body=file_metadata, media_body=media).execute()
    print(res)

    
if __name__ == '__main__':
    main()
# [END drive_quickstart]