import Processes.RedditScraper as RedditScraper
import Processes.VideoEditor as VideoEditor
import Processes.CloudStorage as CloudStorage
import Processes.Emailer as Emailer
import Processes.FileHandler as FileHandler
import Processes.Text2Speech as Text2Speech
import time
import logging
import google.cloud.logging
import os

# Comprehensive video creation function
def video_generator(info_dict, name):

    try:
        downloads_path, final_renders_folder = FileHandler.directory_maker(
            info_dict)
        t2r, t4s = Text2Speech.textbody_reader(info_dict)
        audiopath, headers_list = Text2Speech.t2s(downloads_path=downloads_path,
                                                  t2r=t2r,
                                                  t4s=t4s,
                                                  info_dict=info_dict,
                                                  name=name
                                                  )
        uri, duration = CloudStorage.upload_audio(audiopath, info_dict)
        sub_list = Text2Speech.speech_to_text(audio_uri=uri, duration=duration)
        bgvideopath = CloudStorage.gcs_video_downloader(downloads_path, duration, name)
        ccr_video_path = VideoEditor.cut_crop_resize(downloads_path, bgvideopath, duration)
        speech_bubble = VideoEditor.speech_bubble_object(audiopath, duration, ccr_video_path)
        compiled_path = VideoEditor.video_compiler(title=VideoEditor.title_obj_gen(info_dict['Subreddit'], name),
                                                   heading=VideoEditor.header_obj_gen(headers_list, name),
                                                   subtitles=VideoEditor.sub_obj_gen(sub_list, name),
                                                   sb_video=speech_bubble,
                                                   audiopath=audiopath,
                                                   # bgaudiopath = bgaudiopath,
                                                   downloads_path=downloads_path,
                                                   info_dict=info_dict,
                                                   name=name
                                                   )
        VideoEditor.video_chopper(compiled_video_path=compiled_path,
                                  downloads_path=downloads_path,
                                  final_renders_path=final_renders_folder,
                                  duration=duration
                                  )
        gcs_folder = CloudStorage.upload_to_gcs(
            final_renders_folder, info_dict)
        CloudStorage.db_update(info_dict)
        CloudStorage.dropbox_upload(final_renders_folder, info_dict, name)
        Emailer.notify_email(gcs_folder=gcs_folder)
        FileHandler.file_delete(downloads_path)
        print("\nVideo Creation Process Complete.\n")
        return True

    except Exception as e:
        downloads_path, final_renders_folder = FileHandler.directory_maker(
            info_dict)
        FileHandler.file_delete(downloads_path)
        print(f"\nException occurred: {e}\n")
        print("\nVideo Creation Failed, moving to next iteration.\n")
        return False


# Final main function
def main():

    characters = ["ari", "alex"]
    iteration_count = 1
    error_count = 0
    operation = True
    while operation == True:
        for name in characters:
            try:
                info_dict = RedditScraper.reddit_scraper(name)
                video_generator(info_dict, name)
                sleep_time_minutes = 90
                for n in range(sleep_time_minutes):
                    print(f"Sleeping for the next {sleep_time_minutes} minute(s)...")
                    logging.info(f"Sleeping for the next {sleep_time_minutes} minute(s)...")
                    time.sleep(60)
                    iteration_count += 1
                    sleep_time_minutes -= 1

            except Exception as e:
                print(e)
                logging.info(e)
                error_count += 1
                Emailer.error_email(e, iteration_count, error_count)
                if error_count == 10:
                    operation = False
                continue


    return


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if int(os.environ.get("PRODUCTION", 0)) == 1:
        logging_client = google.cloud.logging.client()
        logging_client.setup_logging()
    while True:
        logging.info("AutoReddit Started")
        main()
        logging.info("AutoReddit Killed")
