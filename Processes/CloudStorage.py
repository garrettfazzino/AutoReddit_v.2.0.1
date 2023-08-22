from google.cloud import storage
import os
from random import choice
from datetime import datetime
import dropbox
from pydub import AudioSegment
import pandas as pd
from dotenv import load_dotenv

"Handles all downloads / uploads to GCP Storage and Dropbox"

# Loads all .env variables
load_dotenv()

# env variables for G-Cloud functions
GCP_API_KEY = os.getenv('GCP_API_KEY')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GCP_API_KEY
config = {
    "language_code": "en-US",
    "enable_word_time_offsets": True,
    "enable_automatic_punctuation": True
}

# General DB Update


def db_update(info_dict, path="Data/AutoRedditDB.csv"):
    """Accesses the previous database and appends new info from scrapes

info: 
    list of info from desired scrape
path: 
    path to the current database"""

    try:
        old_df = pd.read_csv(path, index_col=0)
        apppendable = pd.DataFrame(info_dict, index=[0])
        new_df = pd.concat([old_df, apppendable], ignore_index=True)
        new_df.to_csv(path, mode='w')
        print("\nData appended to local database successfully.\n")

    except:
        apppendable.to_csv(f"{info_dict['Id']}_info_dict.csv")
        print("\nIncomplete information, please review appendable.\n")

    try:
        storage_client = storage.Client()
        bucket = storage_client.get_bucket('autoreddit-database')
        blob = bucket.get_blob("AutoRedditDB.csv")
        blob.upload_from_filename(path)
        print("\nDatabase uploaded to GCP successfully.\n")

    except Exception as e:
        print(f"\nData has not been uploaded to GCP due to exception: {e} \n")

    return True

# Uploads t2s audio to GCP for s2t analyzer


def upload_audio(audiopath, info_dict):
    """Uploads the final audio file from t2s into GCP for analyzation by s2t

audiopath:
    path to final audio on local disk
info_dict:
    dictionary returned by csv2dict function

Returns:
    uri: uri to GCP audio file
    duration: duration of audio in seconds (float format)"""

    print("\nUploading audio file to GCP storage.\n")
    duration = AudioSegment.from_file(audiopath).duration_seconds
    id = info_dict['Id']
    storage_client = storage.Client()
    bucket = storage_client.get_bucket('audio_for_s2t')
    blob = bucket.blob(f"{id}_t2s.wav")
    blob.upload_from_filename(audiopath, num_retries=3)

    uri = dict(uri=f"gs://audio_for_s2t/{id}_t2s.wav")

    print(
        f"\nAudio uploaded to storage.\n\n\nDuration of audio is {duration}s.\n")
    return (uri, duration)

# Downloads bg video / audio from gcs


def gcs_video_downloader(downloads_path, duration, name):
    """Pulls a random bg_video from the desired bucket

downloads_path:
    path to downloads folder    
duration:
    time of current audio
prefix:
    denotes the folder within the bucket which holds desired bgvideos

Returns: path to the downloaded video to be sent to CCR
"""
    if name == "ari":
        prefix = "ari_bg_videos/"
    if name == "alex":
        prefix = "alex_bg_videos/"

    # Note: Client.list_blobs requires at least package version 1.17.0.
    storage_client = storage.Client()
    bucket = storage_client.get_bucket('bg_videos')
    blobs = bucket.list_blobs(prefix=prefix)

    print("\nChoosing video to download.\n")
    # Note: The call returns a response only when the iterator is consumed.
    blob_list = [x.name for x in blobs]
    blob_names = [x.split("/")[-1]
                  for x in blob_list if x.split("/")[-1] != '']
    folder_name = blob_list[0]
    video_time = 0
    if float(duration) > 180:
        video_time = 6
    elif float(duration) > 60:
        video_time = 3
    else:
        video_time = 1
    filter_lst = [x for x in blob_names if x[0] == str(video_time) and x != '']
    video = choice(filter_lst)
    uri = f"gs://{bucket.name}/{folder_name}{video}"
    output_path = os.path.join(
        downloads_path, f"{datetime.today().date()}-bgvideo.webm")

    print("\nDownloading chosen video from GCP.\n")
    with open(output_path, 'wb') as f:
        storage_client.download_blob_to_file(blob_or_uri=uri, file_obj=f)

    storage_client.close()          # Closes client

    print("\nVideo downloaded.\n")
    return output_path

# Uploading files to GCS


def upload_to_gcs(final_renders_path, info_dict):
    """Uploads final cuts to GCS storage

final_renders_path:
    path to final renders folder
info_dict:
    dictionary returend from csv2dict function

Returns:
    name for the GCP folder that the finals are saved under"""

    # Downloads the directory or files after -r to the bucket after gs://
    # os.system(f'gsutil cp -r {final_renders_path} gs://finals_for_upload')
    id = info_dict["Id"]

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "Data/autoreddit-377319-e4460975370b.json"
    storage_client = storage.Client()
    print("\nBeginning upload of final cuts to GCP.\n")

    # Upload final video files
    bucket = storage_client.get_bucket('finals_for_upload')
    split = final_renders_path.split("/")
    today = datetime.today()
    date_of_upload = today.date()
    time_of_upload = str(today.now().time())[:5]
    folder = f"{date_of_upload}_{time_of_upload}_{id}"
    files = os.listdir(final_renders_path)
    for file in files:
        path = os.path.join(os.getcwd(), final_renders_path, file)
        blob = bucket.blob(f"{folder}/{file}")
        blob.upload_from_filename(path)

    storage_client.close()

    print("\nFinal cuts upload to GCP complete.\n")
    return folder

# Uploading to dropbox


def dropbox_upload(final_renders_path, info_dict, name):
    """Uploads final cuts to Dropbox cloud storage

final_renders_path:
    path to final renders folder
info_dict:
    dictionary returend from csv2dict function"""

    post_id = info_dict['Id']
    
    # Create a Dropbox client
    dropbox_key = os.getenv('DROPBOX_KEY')
    dropbox_secret = os.getenv('DROPBOX_SECRET')
    dropbox_oauth_refresh = os.getenv('DROPBOX_OAUTH_REFRESH')
    dbx = dropbox.Dropbox(app_key=dropbox_key,
                          app_secret=dropbox_secret,
                          oauth2_refresh_token=dropbox_oauth_refresh)

    # Define the path of the new folder to create
    new_folder_path = f"/{name}_{datetime.now().date()}_{post_id}"

    # Create the new folder
    try:
        dbx.files_create_folder(new_folder_path)
        print(
            f"\nNew Dropbox folder '{new_folder_path}' created successfully!\n")
    except dropbox.exceptions.ApiError as e:
        print("\nError creating new folder:", e)

    # Define the path of the video file to upload
    try:
        finals = os.listdir(final_renders_path)
        for x in finals:
            file = os.path.join(final_renders_path, x)

            # Open the video file and read its contents
            with open(file, "rb") as f:
                file_contents = f.read()

            # Define the path of the new video file in Dropbox
            new_video_file_path = new_folder_path + f"/{x}"

            # Upload the video file to Dropbox
            dbx.files_upload(file_contents, new_video_file_path)
            print(f"Video file {x} uploaded successfully!")

    except dropbox.exceptions.ApiError as e:
        print("\nError uploading video file:", e)

    print("\nFinal cuts upload to Dropbox complete.\n")
    return True
