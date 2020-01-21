from __future__ import print_function
import datetime
import pickle
import os.path
import time
import praw
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


# If modifying these scopes, delete the file token.pickle.
SCOPES = 'https://www.googleapis.com/auth/calendar'


class Listener():

    # This is straight from the google calendar api tutorial
    # Starts a service
    def __init__(self, phrase, sub, tz, interval):
        self.phrase = phrase
        self.sub = sub
        self.tz = tz
        self.interval = interval
        creds = None

        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        #print(creds)
        #print(creds.valid)
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

    # Send an alert to google calendar
    def calendar_alert(self):
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
    def listen(self):
        reddit = praw.Reddit(client_id='',
                             client_secret='',
                             user_agent='')

        print(reddit.read_only)

        most_recent = ""
        while 1:
            print(str(datetime.datetime.now()))

            recent_set = False

            for submission in reddit.subreddit(self.sub).new(limit=10):

                if submission.title.lower() == most_recent:
                    break

                if self.phrase.lower() in submission.title.lower():
                    print("FOUND : ", submission.title)
                    self.calendar_alert()
                    break

                if not recent_set:
                    most_recent = submission.title.lower()
                    recent_set = True

            time.sleep(self.interval)


def main():

    l = Listener("Banana Republic", "FrugalMaleFashion", "America/Chicago", 10)
    l.listen()


if __name__ == '__main__':
    main()