import pickle
import os.path
import io
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient.http import MediaFileUpload
from apiclient.http import MediaIoBaseDownload

# The scopes are the permissions for the credentials.
# If modifying the scopes, delete the pickle
SCOPES = ['https://www.googleapis.com/auth/drive']

# The authenticator
def authenticate():
    # initialize creds to become the user's credentials
    creds = None
    
    # The file token.pickle stores the user's access and refresh tokens.
    # Created automatically when user authorizes for the first time.
    if os.path.exists('token.pickle'):
       with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
            
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Create our connection to the drive 
    global driveAPI
    driveAPI = build('drive', 'v3', credentials=creds)

# List out the contents of the drive.    
def listdrive():
    # Call the API to get the contents
    results = driveAPI.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    # Print out the contents
    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))

# The snippit to do the upload
def upload():
    # List out the contents of the directory
    for file in os.listdir():
        print(file)

    # Get the users input
    selection = input('Select your file: ')

    # Make a request hash to tell the API what it's getting
    body = {'name': selection, 'mimeType': 'application/octet-stream'}

    # Create the media file upload object and tell it what file to upload,
    media = MediaFileUpload(selection, mimetype = 'application/octet-stream')

    # Create the new file of the uploaded type
    uploader = driveAPI.files().create(body=body, media_body=media).execute()

    # Output success
    print ("Created file '%s' id '%s'." % (uploader.get('name'),
                                           uploader.get('id')))
# The Downloader
def download():
    # Create the list of options to download
    results = driveAPI.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(item['name'])

    # Get user's input
    file_id = input('Please input file name: ')
    dl_id = None
    for item in items:
        
        # Get the item's ID and Name
        if file_id == item['name'] or file_id == item['id']:
            dl_id = item['id']
            dl_name = item['name']

            # Make a request hash to tell the API what it's giving
            request = driveAPI.files().get_media(fileId=dl_id)

            # Perform the download
            fio = io.FileIO(dl_name, 'wb')
            downloader = MediaIoBaseDownload(fio, request)

            # Show status
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print ('Download %d%%.' % int(status.progress() * 100))

    # If the item's not there, let the user know
    if not dl_id:
        print('That file is not in drive')

# Quick code to exit
def quitout():
    # Change stay to false
    global stay
    stay = False

# Display a menu
def menu():
    # Make a dictionary of the choices
    userChoice = {
        'ls': listdrive,
        'dl': download,
        'up': upload,
        'qq': quitout
    }

    # Print out the options
    print('ls - View Files')
    print('dl - Download a File')
    print('up - Upload a File')
    print('qq - Exit')

    # Prompt the user
    selection = input('Please Select an option: ')

    # Create and execute the user's selection
    theRunner = userChoice.get(selection, lambda:
                               'Not a valid selection')
    theRunner()

# Main...    
def main():
    # Make the global stay, and initialize it as true
    global stay
    stay = True

    # Run the authenticatior
    authenticate()

    # Keep returning to the menu
    while stay:
        menu()

# Standard Python start    
if __name__ == '__main__':
    main()


        


