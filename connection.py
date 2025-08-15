import os.path
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
import re

from bs4 import BeautifulSoup

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def clean_email_text(text):
    cleaned = re.sub(r'[\r\n]+', ' ', text)
    final_cleaned = re.sub(' +', ' ', cleaned)
    return final_cleaned.strip()

def find_messages():
  
    creds = get_creds()

    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        results = (
            service.users().messages().list(userId="me", labelIds=["INBOX"]).execute()
        )
        messages = results.get("messages", [])

        if not messages:
            print("No messages found.")
            return

        format_messages = []
        for message in messages:
            
            msg = (
                service.users().messages().get(userId="me", id=message["id"]).execute()
            )
          
            SubjectLine = "Subject: "

            BodyLine = ""
            
            FromSender = "Sender: "
            # Found an edge case?
            if (msg['payload']['body']['size'] == 0):
               continue           
            BodyLine += msg['payload']['body']['data']
            
            decoded_bytes = base64.urlsafe_b64decode(BodyLine + '=' * (4 - len(BodyLine) % 4))

            soup = BeautifulSoup(decoded_bytes, 'html.parser')
            Body_Text = clean_email_text(soup.get_text())         
            for i in msg['payload']['headers']:
               if (i['name'] == 'Subject'):
                  SubjectLine += i['value']
               if (i['name'] == 'From'):
                  FromSender += i['value']
               
            Complete_Message = "Message ID: " + message["id"] + "\n" + FromSender + "\n" + SubjectLine + "\n" + "Body: " + Body_Text
            
            format_messages.append(Complete_Message)

       
        return format_messages 

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")

        return []
def get_creds():
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  creds = None

  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    with open("token.json", "w") as token:
      token.write(creds.to_json())
    
  return creds
    

if __name__ == "__main__":
  
  messages = find_messages()
  