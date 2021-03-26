from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from apiclient.http import MediaFileUpload

import requests
import csv
import pathlib
import os

# If modifying these scopes, delete the file token.json.
SCOPESDRIVE = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive']
SCOPESSHEET = ['https://www.googleapis.com/auth/spreadsheets']

results_id = None
folder_id = None
image_folder_id = None
input_id = None
imgs_id = []

serviceDrive = None
serviceSheet = None
path = None

def remove_images():
    if not serviceDrive:
        init()
    #remove existing images
    res = serviceDrive.files().list(q="'{}' in parents".format(image_folder_id)).execute()
    for file in res["files"]:
         serviceDrive.files().delete(fileId=file["id"]).execute()

def upload_images():
    if not serviceDrive:
        init()

    #upload img         
    for file in os.listdir(path+"..\output_images"):
        file_metadata = {
            'name': file,
            'parents': [image_folder_id]
        }
        media = MediaFileUpload(str(pathlib.Path(__file__).parent.absolute())+f"\..\output_images\{file}", mimetype='image/gif')
        res = serviceDrive.files().create(body=file_metadata,
                                            media_body=media,
                                            fields='id').execute()
        imgs_id.append(res["id"])

def upload_res():
    if not serviceSheet:
        init()
    valueCities = []
    valuesPath = []
    with open(path+"paths.csv") as csvfile:
        for lineNb,line in enumerate(csv.reader(csvfile)):
            valuesPath.append(line)

    with open(path+"cities.csv") as csvfile:
        for line in csv.reader(csvfile):
            valueCities.append(line)
    
    bodyPath = {
        'values': valuesPath
    }
    bodyCities = {
        'values': valueCities
    }
    
    for i in range(len(imgs_id)):
        bodyPath["values"][i+1].append("https://drive.google.com/uc?export=view&id="+imgs_id[i])

    #save outputs on drive
    serviceSheet.spreadsheets().values().clear(spreadsheetId=results_id, range="paths!A:KN").execute()
    serviceSheet.spreadsheets().values().clear(spreadsheetId=results_id, range="cities!A:KN").execute()

    serviceSheet.spreadsheets().values().update(spreadsheetId=results_id, range="paths!A:KN", body=bodyPath,valueInputOption="USER_ENTERED").execute()
    serviceSheet.spreadsheets().values().update(spreadsheetId=results_id, range="cities!A:KN", body=bodyCities,valueInputOption="USER_ENTERED").execute()


def get_inputs():
    if not serviceDrive:
        init()
    res = serviceDrive.files().export(fileId=input_id, mimeType="text/plain").execute().decode("utf-8")
    print(res)
    return res

    

def init():
    global path 
    path = str(pathlib.Path(__file__).parent.absolute())+"\\"

    credsDrive = None
    credsSheets = None
    if os.path.exists(path+'tokenDrive.json'):
        credsDrive = Credentials.from_authorized_user_file(path+'tokenDrive.json', SCOPESDRIVE)
    if not credsDrive or not credsDrive.valid:
        if credsDrive and credsDrive.expired and credsDrive.refresh_token:
            credsDrive.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                path+'credentialsDrive.json', SCOPESDRIVE)
            credsDrive = flow.run_local_server(port=0)
        with open(path+'tokenDrive.json', 'w') as token:
            token.write(credsDrive.to_json())

    if os.path.exists(path+'tokenSheets.json'):
        credsSheets = Credentials.from_authorized_user_file(path+'tokenSheets.json', SCOPESSHEET)
    if not credsSheets or not credsSheets.valid:
        if credsSheets and credsSheets.expired and credsSheets.refresh_token:
            credsSheets.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                path+'credentialsSheets.json', SCOPESSHEET)
            credsSheets = flow.run_local_server(port=0)
        with open(path+'tokenSheets.json', 'w') as token:
            token.write(credsSheets.to_json())

    global serviceDrive, serviceSheet, image_folder_id, results_id, input_id
    serviceDrive = build('drive', 'v3', credentials=credsDrive)
    serviceSheet = build('sheets', 'v4', credentials=credsSheets)


    res = serviceDrive.files().list().execute()
    for file in res["files"]:
        if file['mimeType'] == 'application/vnd.google-apps.folder' and file['name'] == "images":
            image_folder_id = file['id']
        elif file['mimeType'] == 'application/vnd.google-apps.spreadsheet' and file['name'] == "results_project":
            results_id = file['id']
        elif file['mimeType'] == 'application/vnd.google-apps.document' and file['name'] == "input_data":
            input_id = file['id']  


#Pr0j3ctM1S2Is3n