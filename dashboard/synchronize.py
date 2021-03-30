from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
import csv
import pathlib
import os

# elements to reach into drive account
DRIVE_CSV_RESULTS = 'results_project'
DRIVE_FOLDER_IMGS = 'images'

# global credentials to access drive account
CREDS_DRIVE = 'credentialsDrive.json'
CREDS_SHEET = 'credentialsSheets.json'

# If modifying these scopes, delete json token files
SCOPES_DRIVE = ['https://www.googleapis.com/auth/drive.metadata.readonly',
                'https://www.googleapis.com/auth/drive']
SCOPES_SHEET = ['https://www.googleapis.com/auth/spreadsheets']

# filenames with temporary access token
TOKEN_DRIVE = 'tokenDrive.json'
TOKEN_SHEET = 'tokenSheets.json'

# alias of googleapiclient.discovery library
FOLDER = 'application/vnd.google-apps.folder'
CSV = 'application/vnd.google-apps.spreadsheet'
DOC = 'application/vnd.google-apps.document'
IMG_URL_ACCESS = "https://drive.google.com/uc?export=view&id="


class Synchronize:
    def __init__(self, filename):  # path
        self.path = str(pathlib.Path(__file__).parent.absolute())+"\\"

        credsDrive = self.get_cred(TOKEN_DRIVE, SCOPES_DRIVE, CREDS_DRIVE)
        credsSheet = self.get_cred(TOKEN_SHEET, SCOPES_SHEET, CREDS_SHEET)

        self.serviceDrive = build('drive', 'v3', credentials=credsDrive)
        self.serviceSheet = build('sheets', 'v4', credentials=credsSheet)

        self.input_id = ""
        self.results_id = ""
        self.img_folder_id = ""

        query = f"name='{filename}' or\
                name='{DRIVE_CSV_RESULTS}' or\
                name='{DRIVE_FOLDER_IMGS}'"
        # pylint: disable=maybe-no-member
        for file in self.serviceDrive.files().list(q=query).execute()["files"]:
            if file['mimeType'] == DOC and file['name'] == filename:
                self.input_id = file['id']

            elif file['mimeType'] == CSV and file['name'] == DRIVE_CSV_RESULTS:
                self.results_id = file['id']

            elif file['mimeType'] == FOLDER and file['name'] == DRIVE_FOLDER_IMGS:
                self.img_folder_id = file['id']

        if not self.input_id or not self.results_id or not self.img_folder_id:
            print("Verify names between drive and synchronize.py")
            exit()

        self.imgs_id = []
        self.folder_id = None

    def get_cred(self, token_file, scope, cred_file):
        cred = None
        token_file = self.path+token_file

        if os.path.exists(token_file):
            cred = Credentials.from_authorized_user_file(token_file, scope)

        if not cred or not cred.valid:
            if cred and cred.expired and cred.refresh_token:
                cred.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.path+cred_file, scope)
                cred = flow.run_local_server(port=0)

            with open(token_file, 'w') as token:
                token.write(cred.to_json())

        return cred

    def read_input_file(self):
        # pylint: disable=maybe-no-member
        return self.serviceDrive.files() \
                .export(fileId=self.input_id, mimeType="text/plain") \
                .execute().decode("utf-8")

    def remove_imgs(self):
        query = f"'{self.img_folder_id}' in parents"

        # pylint: disable=maybe-no-member
        for file in self.serviceDrive.files().list(q=query).execute()["files"]:
            self.serviceDrive.files().delete(fileId=file["id"]).execute()

    def upload_imgs(self):
        self.remove_imgs()

        file_metadata = {'name': '', 'parents': [self.img_folder_id]}

        for file in os.listdir(f"{self.path}..\\png_imgs"):
            file_metadata['name'] = file

            media = MediaFileUpload(f"{self.path}..\\png_imgs\\{file}", mimetype='image/gif')

            # pylint: disable=maybe-no-member
            res = self.serviceDrive.files().create(body=file_metadata,
                                                   media_body=media,
                                                   fields='id')\
                                           .execute()
            self.imgs_id.append(res["id"])

    def upload_csv(self, valuesPath, valuesCities):
        bodyPath = {'values': valuesPath}
        bodyCities = {'values': valuesCities}

        for i, img_id in enumerate(self.imgs_id):
            bodyPath["values"][i+1].append(IMG_URL_ACCESS+img_id)

        # save outputs on drive
        # pylint: disable=maybe-no-member
        drive_csv = self.serviceSheet.spreadsheets().values()
        drive_csv.clear(spreadsheetId=self.results_id, range="paths!A:KN").execute()
        drive_csv.clear(spreadsheetId=self.results_id, range="cities!A:KN").execute()

        drive_csv.update(spreadsheetId=self.results_id, range="paths!A:KN", body=bodyPath, valueInputOption="USER_ENTERED").execute()
        drive_csv.update(spreadsheetId=self.results_id, range="cities!A:KN", body=bodyCities, valueInputOption="USER_ENTERED").execute()
