# AutoReddit v2.0.1
Autonomously create encapsulating videos of reddit posts in vertical format for upload to TikTok, Reels, Snapchat, etc. You never have to worry about having content again, with an autonomous bot that makes you videos in both a woman's and man's character, named 'Ari' and 'Alex' respectively. 

# Environment Setup
In order to set your environment up to run the code here, first install all requirements:

```shell
pip3 install -r requirements.txt
```

Rename `example.env` to `.env` and edit the variables appropriately.
```
GCP_API_KEY= PATH/TO/JSON/FILE/ON/DISK
REDDIT_API_CLIENT= String of Reddit API Client ID
REDDIT_API_SECRET= String of Reddit API Client Password
SENDER_EMAIL= Personal Email to send notifications from
EMAIL_PASSWORD= Personal Password to email account for emailing
RECIPIENT_EMAIL= Recipient Email to accept notifications
DROPBOX_KEY= API Key from Dropbox
DROPBOX_SECRET= API Secret from Dropbox
DROPBOX_OAUTH_REFRESH= OAuth refresh token from Dropbox
```

# How does it work?
AutoReddit is built to operate on disk, or with the built in Docker File, it can be tasked to docker or a VM to run. This app is heavily integrated with Google Cloud Platform, using many API's such as storage, text-to-speech, and speech-to-text to accomplish all of the processes needed. Just insert all environment variables, then begin the program. Popular reddit posts are automatcially aggregated, filtered, applied to a video background, and placed into a dropbox folder after being cut into 59s long cuts. From there, you can do with the videos as you wish.

## Python Version
To use this software, you must have Python 3.8 or later installed. Earlier versions of Python will not compile.