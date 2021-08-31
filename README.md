# MeetDocs-Using-Symbl
MeetDocs allows employees to easily review meetings by transcribing the recordings, organizing the content, and adding insights in a user-friendly interface and emailing them the details extracted


## MeetDocs Flow
Employee pastes meeting link, enter symbl app id, app secret, sender email & password, receiver email.

Symbl POST Video URL Async API is called for processing video.

After the job is completed, the following information is extracted:
Conversation info, Transcription (messages), Topics, Action items and Follow-ups.

A mail is send containing Transcription (messages) saved in pdf. Topics, Action items and Follow-ups are also sended in the mail.

## Steps to run the project
Install the packages present in requirements.txt

Run the Project using: python backend.py
