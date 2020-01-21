from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


# If modifying these scopes, delete the file token.pickle.
SCOPES = 'https://www.googleapis.com/auth/calendar'


class Listener():

    # This is straight from the google calendar api tutorial
    # Starts a service
    def __init__(self, phrase, sub, tz):
        self.phrase = phrase
        self.sub = sub
        self.tz = tz
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

        self.service = build('calendar', 'v3', credentials=creds)

    # Send the alert to google calendar
    def alert(self):
        start = list(str(datetime.datetime.now() + datetime.timedelta(0, 60, 0)))
        start[10] = 'T'
        start = start[:19]
        start = ''.join(start)

        end = list(str(datetime.datetime.now() + datetime.timedelta(0, 1860, 0)))
        end[10] = 'T'
        end = end[:19]
        end = ''.join(end)

        event_body = {
            'summary': 'Phrase "' + self.phrase + '" FOUND in reddit.com/r/' + self.sub,
            'decription': 'Maybe I should put link to the reddit post here',
            'start': {
                'dateTime': start,
                'timeZone': self.tz,
            },
            'end': {
                'dateTime': end,
                'timeZone': self.tz,
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 1},
                    {'method': 'popup', 'minutes': 1},
                ],
            }
        }

        event = self.service.events().insert(calendarId='primary', body=event_body).execute()
        print('Event created: %s' % (event.get('htmlLink')))

    # Start the listener itself
    #def start(self):
        # Loop here, looking for keyword in reddit post




def main():

    l = Listener("hmm", "FrugalMaleFashion", "America/Chicago")
    l.alert()

if __name__ == '__main__':
    main()