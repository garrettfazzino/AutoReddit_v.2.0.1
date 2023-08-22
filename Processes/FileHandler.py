import pandas as pd
from datetime import datetime
import os
import shutil

"Creates directories / data files, and destroys all unneeded files when finished."

# Initializing info from database
def csv2dict(index=int):
    """Takes the most recent database entry and creates a dictionary from the info pulled

index:
    int, deciphers which scrape you want to access in decsending order (1 most recent, increase to go farther back)

Returns: dictionary of desired reddit scrape"""

    database_path="Data/AutoRedditDB.csv"
    df = pd.read_csv(database_path)

    if index > len(df):
        index = len(df)
    desired_index = len(df)-index
    most_recent_scrape = df.loc[desired_index]
    info_dict = most_recent_scrape.to_dict()

    print("\nInfo Dictionary created\n")
    return info_dict

# Creates directories in accordance to post ID
def directory_maker(info_dict):
    """Creates a new directory from the 'Id' of the reddit post.
Set to desktop location for now, can be implemented as a input for 
new location later. 

info_dict: 
    dictionairy of reddit info from 'csv2dict' function

Returns: downloads_path and final_renders directory paths"""
    Id = 'Id'
    downloads_path = f"{str(datetime.today().date())}_{info_dict[Id]}_autoreddit_downloads"
    final_renders_folder = os.path.join(downloads_path, f"{info_dict[Id]}_f_{datetime.today().date()}")

    # Another way to express "if this directory doesnt already exist"
    if not os.path.exists(downloads_path):
        os.mkdir(downloads_path)
        print(f"\nDownloads folder created.\n")
    
    if not os.path.exists(final_renders_folder):
        os.mkdir(final_renders_folder)
        print(f"\nFinal renders folder created.\n")

    return downloads_path, final_renders_folder

# Delete all downlaoded files
def file_delete(downloads_path=str):
    """Deletes all leftover files from local directories
    
downloads_path:
    path to the downloads folder"""

    try:
        shutil.rmtree(downloads_path)
        print("\nAll audio / video files removed from local disk. Refer to GCS and Dropbox for final cuts.\n")

    except Exception as e:
        print(e)

    return True

