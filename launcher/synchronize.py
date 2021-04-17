from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os
import re

from defines import DRIVE_FOLDER, RESULT_FOLDER

# elements to reach into drive account
DRIVE_FOLDER_IMGS = 'images'
DRIVE_CSV_RESULTS = 'Results_project'
CSV_RESULT_SHEET_ORD = "Orders!A:"  # fin calculée
CSV_RESULT_SHEET_MAP = "Map_coordinates!A:"  # fin calculée
CSV_RESULT_SHEET_EXE = "Executions!A:"  # fin calculée

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
    def __init__(self, path):
        self.path = path
        self.configfile = ""
        self.datafile = ""

        credsDrive = self.get_cred(TOKEN_DRIVE, SCOPES_DRIVE, CREDS_DRIVE)
        credsSheet = self.get_cred(TOKEN_SHEET, SCOPES_SHEET, CREDS_SHEET)

        self.serviceDrive = build('drive', 'v3', credentials=credsDrive)
        self.serviceSheet = build('sheets', 'v4', credentials=credsSheet)

        self.results_id = ""
        self.img_folder_id = ""
        query = f"name='{DRIVE_CSV_RESULTS}' or\
                  name='{DRIVE_FOLDER_IMGS}'"
        # pylint: disable=maybe-no-member
        for file in self.serviceDrive.files().list(q=query).execute()["files"]:
            if file['mimeType'] == CSV and file['name'] == DRIVE_CSV_RESULTS:
                self.results_id = file['id']

            elif file['mimeType'] == FOLDER and file['name'] == DRIVE_FOLDER_IMGS:
                self.img_folder_id = file['id']

        if not self.results_id or not self.img_folder_id:
            print("Verify names between drive and synchronize.py")
            exit()

        self.config_id = None
        self.input_id = None
        self.folder_id = None
        self.imgs_id = []

    def get_cred(self, token_file, scope, cred_file):
        cred = None
        token_file = self.path+DRIVE_FOLDER+"\\"+token_file

        if os.path.exists(token_file):
            cred = Credentials.from_authorized_user_file(token_file, scope)

        if not cred or not cred.valid:
            if cred and cred.expired and cred.refresh_token:
                cred.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.path+DRIVE_FOLDER+"\\"+cred_file, scope)
                cred = flow.run_local_server(port=0)

            with open(token_file, 'w') as token:
                token.write(cred.to_json())

        return cred

    def set_configfile(self, configfile):
        self.configfile = configfile

        query = f"name='{configfile}'"
        # pylint: disable=maybe-no-member
        for file in self.serviceDrive.files().list(q=query).execute()["files"]:
            if file['mimeType'] == DOC and file['name'] == configfile:
                self.config_id = file['id']

        if not self.config_id:
            print("Verify config filename between drive and input args")
            exit()

        return self

    def set_datafile(self, datafile):
        self.datafile = datafile

        query = f"name='{datafile}'"
        # pylint: disable=maybe-no-member
        for file in self.serviceDrive.files().list(q=query).execute()["files"]:
            if file['mimeType'] == DOC and file['name'] == datafile:
                self.input_id = file['id']

        if not self.input_id:
            print("Verify data filename between drive and config file")
            exit()

        return self

    def get_config(self):
        # pylint: disable=maybe-no-member
        return self.serviceDrive.files() \
                .export(fileId=self.config_id, mimeType="text/plain") \
                .execute().decode("utf-8")[1:]  # remove BOM character

    def get_input(self):
        # pylint: disable=maybe-no-member
        return self.serviceDrive.files() \
                .export(fileId=self.input_id, mimeType="text/plain") \
                .execute().decode("utf-8")

    def remove_imgs(self, regex, extension):
        query = f"'{self.img_folder_id}' in parents and mimeType='image/{extension}'"

        # pylint: disable=maybe-no-member
        for file in self.serviceDrive.files().list(q=query).execute()["files"]:
            if not regex.match(file["name"]):
                continue

            self.serviceDrive.files().delete(fileId=file["id"]).execute()

    def upload_imgs(self, is_gif):
        reg = "^"+self.datafile+"_[0-9]+.{0}$"

        extension = "gif" if is_gif else "png"
        self.remove_imgs(re.compile(r""+reg.format(extension)), extension)

        regex = re.compile(r""+reg.format("gif" if is_gif else "png"))

        file_metadata = {'name': '', 'parents': [self.img_folder_id]}

        for file in os.listdir(self.path+RESULT_FOLDER):
            if not regex.match(file):
                continue

            file_metadata['name'] = file

            media = MediaFileUpload(self.path+RESULT_FOLDER+"\\"+file, mimetype='image/gif')

            # pylint: disable=maybe-no-member
            res = self.serviceDrive.files().create(body=file_metadata,
                                                   media_body=media,
                                                   fields='id')\
                                           .execute()
            self.imgs_id.append(res["id"])

    def upload_csv(self, valuesOrders, valuesCoords, valuesExes):
        bodyOrd = {'values': valuesOrders}
        bodyMap = {'values': valuesCoords}
        bodyExe = {'values': valuesExes}

        # for i, img_id in enumerate(self.imgs_id):
        #     bodyOrd["values"][i+1].append(IMG_URL_ACCESS+img_id)

        # save outputs on drive
        # pylint: disable=maybe-no-member
        drive_csv = self.serviceSheet.spreadsheets().values()
        csv_id = self.results_id

        csv_range_ord = CSV_RESULT_SHEET_ORD+shift_letter('A', len(valuesOrders[0]))
        csv_range_map = CSV_RESULT_SHEET_MAP+shift_letter('A', len(valuesCoords[0]))
        csv_range_exe = CSV_RESULT_SHEET_EXE+shift_letter('A', len(valuesExes[0]))

        drive_csv.clear(spreadsheetId=csv_id, range=csv_range_ord).execute()
        drive_csv.clear(spreadsheetId=csv_id, range=csv_range_map).execute()
        drive_csv.clear(spreadsheetId=csv_id, range=csv_range_exe).execute()

        drive_csv.update(spreadsheetId=csv_id, range=csv_range_ord, body=bodyOrd, valueInputOption="USER_ENTERED").execute()
        drive_csv.update(spreadsheetId=csv_id, range=csv_range_map, body=bodyMap, valueInputOption="USER_ENTERED").execute()
        drive_csv.update(spreadsheetId=csv_id, range=csv_range_exe, body=bodyExe, valueInputOption="USER_ENTERED").execute()


def shift_letter(letter, shift):
    start = ord('a') if letter.islower() else ord('A')
    return chr((ord(letter) - start + shift) % 26 + start)
