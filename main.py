from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from secrets import secrets
import datetime as dt
import requests

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/documents','https://www.googleapis.com/auth/drive']

def authenticate():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
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
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    docService = build('docs', 'v1', credentials=creds)
    driveService = build('drive', 'v3', credentials=creds)

    return (docService,driveService)

def validateDate():
    f = open("dates.txt", "r")
    f.seek(0)
    targetDatesArr = f.read().split("\n")
    targetDatesArr = map(lambda date: dt.datetime.strptime(date, "%Y-%m-%d") - dt.timedelta(days=1), targetDatesArr)

    if (dt.date.today() not in targetDatesArr):
        print("Script should not run today as defined in dates.txt")
        return False

    return True

def main():
    # Slack
    slackUrl = secrets['slackUrl']

    # if (dt.date.isoweekday != 5):
    #     print("It's not Friday!")
    #     return

    if (not validateDate()):
        return

    service = authenticate()
    docService = service[0]
    driveService = service[1]
    folderId = secrets['destFolderId']

    targetDate = dt.date.today + dt.timedelta(days=1)

    print(targetDate)
    body = {
        'title': f'Strat Bi-Weekly Meeting {targetDate}'
    }
    doc = docService.documents().create(body=body).execute()
    docId = doc.get('documentId')
    docUrl = 'https://docs.google.com/document/d/{0}/edit'.format(docId)

    file = driveService.files().update(fileId= docId, fields='parents').execute()
    prevParents = ",".join(file.get('parents'))

    file = driveService.files().update(fileId=docId, addParents =folderId,removeParents=prevParents,fields='id,parents').execute()

    print(docUrl)

    title = 'Bi Weekly Meeting\n'
    subTitle= f'Date: {targetDate}\n'
    header1 = 'VP Updates:\n'
    header2 = 'Coordinator Updates\n'
    body2 = f'{secrets["coordinators"]["person1"]}:\n\n{secrets["coordinators"]["person2"]}:\n\n{secrets["coordinators"]["person3"]}:\n\n'
    header3 = 'Next Meeting:'

    docBody = [
        {
            'insertText': {
                'location': {
                    'index': 1
                },
                'text': header3 + '\n'
            }
        },
        {
            'updateTextStyle': {
                'range': {
                    'startIndex': 1,
                    'endIndex': len(header3)+1
                },
                'textStyle': {
                    'bold': True,
                    'fontSize': {
                        'magnitude': 12,
                        'unit': 'PT'
                    }
                },
                'fields': 'bold, fontSize'
            }
        },
        {
            'insertText': {
                'location': {
                    'index': 1
                },
                'text': body2 + '\n'
            }
        },
        {
            'updateTextStyle': {
                'range': {
                    'startIndex': 1,
                    'endIndex': len(body2)+1
                },
                'textStyle': {
                    'bold': False,
                    'fontSize': {
                        'magnitude': 12,
                        'unit': 'PT'
                    }
                },
                'fields': 'bold, fontSize'
            }
        },
        {
            'insertText': {
                'location': {
                    'index': 1
                },
                'text':header2+ '\n'
            }
        },
        {
            'updateTextStyle': {
                'range': {
                    'startIndex': 1,
                    'endIndex': len(header2)+1
                },
                'textStyle': {
                    'bold': True,
                    'fontSize': {
                        'magnitude': 12,
                        'unit': 'PT'
                    }
                },
                'fields': 'bold, fontSize'
            }
        },
        {
            'insertText': {
                'location': {
                    'index': 1
                },
                'text':header1+ '\n'
            }
        },
        {
            'updateTextStyle': {
                'range': {
                    'startIndex': 1,
                    'endIndex': len(header1)+1
                },
                'textStyle': {
                    'bold': True,
                    'fontSize': {
                        'magnitude': 12,
                        'unit': 'PT'
                    }
                },
                'fields': 'bold, fontSize'
            }
        },
        {
            'insertText': {
                'location': {
                    'index': 1
                },
                'text':subTitle + '\n'
            }
        },
        {
            'updateTextStyle': {
                'range': {
                    'startIndex': 1,
                    'endIndex': len(subTitle)+1
                },
                'textStyle': {
                    'bold': False,
                    'fontSize': {
                        'magnitude': 12,
                        'unit': 'PT'
                    }
                },
                'fields': 'bold, fontSize'
            }
        },
        {
            'insertText': {
                'location': {
                    'index': 1,
                },
                'text': title  + '\n'
            }
        },
        {
            'updateTextStyle': {
                'range': {
                    'startIndex': 1,
                    'endIndex': len(title)+1
                },
                'textStyle': {
                    'bold': True,
                    'fontSize': {
                        'magnitude': 14,
                        'unit': 'PT'
                    }
                },
                'fields': 'bold, fontSize'
            }
        }
    ]

    result = docService.documents().batchUpdate(documentId=docId, body={'requests': docBody}).execute()

    print(result)




    slackMessage = {
        'text': f'<@channel> Hey guys, just a reminder that we have a meeting on {targetDate} at 5:30pm.\n\nReact one you\'ve filled out your meeting minutes <{docUrl}|here>'
    }

    request = requests.post(slackUrl, json=slackMessage)
    print(request)



if __name__ == "__main__":
    main()