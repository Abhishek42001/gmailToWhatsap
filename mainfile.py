from __future__ import print_function
import base64
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from twilio.rest import Client 
from email_reply_parser import EmailReplyParser


# If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]


def main(email,whatsapnumber):
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
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

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        if len(email)==0:
            results = service.users().messages().list(userId='me',maxResults=1,labelIds=['UNREAD']).execute()
        else:
            results = service.users().messages().list(userId='me',maxResults=1,q='from:'+email,labelIds=['UNREAD']).execute()
        messages = results.get('messages')
        if not messages:
            print("No New messages found")
            return

        #####twillio setup
        account_sid = 'ACe8204da223184afdee29bcfc90980869' 
        auth_token = '64d5e629736879505ff7fabaf5c6c4f8' 
        client = Client(account_sid, auth_token) 
        #####

        for message in messages:
            txt = service.users().messages().get(userId='me', id=message['id']).execute()
            
            service.users().messages().modify(userId='me', id=message['id'], body={
                'removeLabelIds': ['UNREAD']
            }).execute()
            payload=txt['payload']
            parts = payload.get('parts')[0]
            data = parts['body']['data']
            data = data.replace("-","+").replace("_","/")
            decodedmsg=base64.b64decode(data).decode('utf-8')
            print(EmailReplyParser.parse_reply(decodedmsg))
            #sending new mail from email id to whatsap
            
            message = client.messages.create( 
                from_='whatsapp:+14155238886',  
                body=decodedmsg,      
                to='whatsapp:+91'+whatsapnumber 
            ) 
            print("Message sent successfully")
            
        # if not labels:
        #     print('No labels found.')
        #     return
        # print('Labels:')
        # for label in labels:
        #     print(label['name'])
            

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        # message = client.messages.create( 
        #         from_='whatsapp:+14155238886',  
        #         body="You Have received a mail which can not be seen here...",      
        #         to='whatsapp:+91'+whatsapnumber 
        # ) 
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    email=""
    whatsapnumber=""
    while True:
        n=int(input("Select an option :\n 1).Send Every Mail's body  2).Send only from specific email's body:\n\t"))
        if n==1:
            while len(whatsapnumber)!=10:
                whatsapnumber=input("Enter your whatsap number to receive mails: ")
                if(len(whatsapnumber)!=10):
                    print("Whatsap number must be of 10 digits: ")
            break
        elif n==2:
            email=input("Enter email id: ")
            while len(whatsapnumber)!=10:
                whatsapnumber=input("Enter your whatsap number to receive mails : ")
                if(len(whatsapnumber)!=10):
                    print("Whatsap number must be of 10 digits")
            break
        else:
            print("Please choose correct option(available options are 1 and 2).: ")
    while True:
        main(email,whatsapnumber)
