# BEGIN IMPORT BOILERPLATE
from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
# END IMPORT BOILERPLATE

# BEGIN IMPORT
from apiclient import errors
import base64
from bs4 import BeautifulSoup
import time
import dateutil.parser as parser
from datetime import datetime
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from privatefunc import bodystringmanip # This function deals with private string manipulation
                                        # Contains private data specific to the strings
from privatefunc import interpretbody   # This function deals with string manipulation. 
                                        # Contains private data specific to the strings
from privatefunc import classification_label
# END IMPORT

# BEGIN SCOPE
# If modifying these scopes, delete the file token.json.
# These scopes affect what permissions Google asks the user for.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/gmail.labels',
    'https://www.googleapis.com/auth/gmail.modify'
]
# END SCOPES

# BEGIN PROGRAM
def main():
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.

    # BEGIN BOILERPLATE
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    GMAIL = build('gmail', 'v1', http=creds.authorize(Http()))
    # END BOILERPLATE

    # BEGIN DATA COLLECTION SECTION
    try:
        unrespond_msgs = GMAIL.users().messages().list(userId='me', q='from:[OBFUSCATED]@[OBFUSCATED].com AND label:INBOX AND subject:Action Needed: New Customer').execute()
        msg_list = unrespond_msgs['messages']
        print ("List of unresponded_msgs: ", str(len(msg_list)))

        final_list = [ ] #List object will eventually contain all messages which are from [OBFUSCATED] 

        for msg in msg_list:
            temp_dict = { }
            temp_msg_id = msg['id'] #get id of individual message
            temp_message = GMAIL.users().messages().get(userId='me', id=temp_msg_id).execute() #fetch message using API
            temp_msg_payload = temp_message['payload'] #get payload of message
            temp_msg_header = temp_msg_payload['headers'] #get header of payload

            for one in temp_msg_header: #getting subject lines
                if one['name'] == 'Subject':
                    temp_msg_subject = one['value']
                    temp_dict['Subject'] = temp_msg_subject
                else:
                    pass
        
            for two in temp_msg_header:
                if two['name'] == 'Date':
                    temp_unformat_msg_date = two['value']
                    temp_date_parser = (parser.parse(temp_unformat_msg_date))
                    temp_msg_date = (temp_date_parser.date())
                    temp_dict['Date'] = str(temp_msg_date)
                else:
                    pass

            for three in temp_msg_header:
                if three['name'] == 'From':
                    temp_msg_from = three['value']
                    temp_dict['Sender'] = temp_msg_from
                else:
                    pass

            try:
                temp_msg_parts = temp_msg_payload['parts'] #fetching message parts list
                temp_part_one = temp_msg_parts[0] #fetching first element in parts list
                temp_unformat_msg_body = temp_part_one['body'] #fetching body object
                temp_unformat_msg_body_data = temp_unformat_msg_body['data'] #fetching data from body for decoding
                temp_msg_body_clean_2 = base64.b64decode(temp_unformat_msg_body_data, '-_')
                soup = BeautifulSoup(temp_msg_body_clean_2, "lxml") #create beautiful soup object from 
                temp_msg_body = soup.prettify() #Legible message body
                temp_msg_body = bodystringmanip(temp_msg_body)
                temp_dict['Message body plaintext'] = temp_msg_body
                temp_dict['Message body values'] = interpretbody(temp_msg_body)
                temp_dict['Message id'] = temp_msg_id

            except:
                pass
                print("Failed body")

            print (temp_dict)
            final_list.append(temp_dict) #Adds dictionary item to the final list object, currently unused for anything
        # END DATA COLLECTION SECTION

        # BEGIN SEND EMAIL SECTION
        try:
            for temp_dict in final_list:
                
                myemail = GMAIL.users().getProfile(userId='me').execute()['emailAddress']

                to = temp_dict["Message body values"]["Email"]

                bcc = temp_dict["Message body values"]["BCC"]

                subject = temp_dict["Message body values"]["Subject"]
                send_msg_body = temp_dict["Message body values"]["Email Body"]

                finalmsg = create_email(myemail, to, bcc, subject, send_msg_body)
                send_message(GMAIL,'me',finalmsg)

        except:
            pass
            print("Failed send email section")
        # END SEND EMAIL SECTION

        # BEGIN LABEL CLASSIFICATION SECTION
        try:
            for temp_dict in final_list:
                GMAIL.users().messages().modify(userId='me', id=temp_dict['Message id'],body={ 'addLabelIds': [classification_label]}).execute()
                GMAIL.users().messages().modify(userId='me', id=temp_dict['Message id'],body={ 'removeLabelIds': ['INBOX']}).execute() 

        except:
            pass
            print("Failed label email section")
            results = GMAIL.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])

            if not labels:
                print('No labels found.')
            else:
                print('Labels:')
            for label in labels:
                print(label['name']+ " "+label['id'])
        # END LABEL CLASSIFICATION SECTION

        print ("Total message retrieved: ",str(len(final_list)))

    except:
        pass
        print("No messages currently require responding to!")

# END PROGRAM

# BEGIN GMAIL BOILERPLATE FUNCTION SECTION
def send_message(service, user_id, message):
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
    except:
        pass
        print("Failed send function section")

def create_email(sender, to, bcc, subject, message_body, html_content=None):
    try:
        message = MIMEMultipart('alternative')
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        message['bcc'] = bcc
        body_mime = MIMEText(message_body, 'plain')
        message.attach(body_mime)
        return {'raw': base64.urlsafe_b64encode(bytes(message.as_string(), "utf-8")).decode("utf-8")}
        
    except:
        pass
        print("Failed create_email")
    

# END GMAIL BOILERPLATE FUNCTION SECTION

if __name__ == '__main__':
    main()