from google.cloud import speech_v1 as speech
import google.cloud.texttospeech as tts
import os
from pydub import AudioSegment
import codecs


# env variables for G-Cloud functions
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "Data/autoreddit-377319-e4460975370b.json"

# Parses information into proper formats and creates T2S audio files / .txt files with file/text info


def textbody_reader(info_dict):
    """Takes textbodies from the scrape desired and parses them into a list for the T2S, and dictionary for subtitles

info_dict: 
    dict, returned from csv2dict function

Returns:
    text_to_read: lst, used for the T2S function to create audio
    text_for_subtitles: dict, used in subtitle / text_overlay generators to create displayable text"""

    # Names variables from info_dict
    textbody = info_dict['TextBody']
    print(f"\n{textbody}\n")
    texttype = info_dict['TextType']
    title = info_dict['Title']
    author = f"u/{info_dict['Author']}"
    print(f"Text type is:      {texttype}")

    # Begins the iterative process of filtering through textbody of each post to create the text_to_read list
    space = "."
    text_to_read = [space, title, space]
    text_for_subtitles = {}

    if texttype == 'Comment':
        text_for_subtitles[author] = title
        text_list = textbody.split("$newcomment$")[1:]
        for x in [x.split("$commentstart$") for x in text_list]:
            text_to_read.append(x[1])
            text_to_read.append(space)
            text_for_subtitles[x[0]] = x[1]

    elif texttype == 'Story':
        text_for_subtitles[author] = textbody
        for paragraph in textbody.split("\n"):
            if paragraph == "\n":
                text_to_read.append(space)
            else:
                text_to_read.append(paragraph)

    else:
        raise NameError

    print("\nText has been read in and morphed into readable bodies for Ari\n")
    return text_to_read, text_for_subtitles

# Converts textbodies to audio files


def t2s(downloads_path, t2r, t4s, info_dict, name):
    """Takes the info dic and creates T2S audio file from parsed comment or story bodies

downloads_path: 
    path to the downloads folder
t2r:
    text to read, textbody from the textbody_reader function
t4s:
    text for subtitles, textbody from the textbody_reader function
info_dict:
    dict, returned by csv2dict function
voice_name:
    Ari's voice from the google cloud text to speech options list

Returns:
    final_audio_path: str, pathname to the final audio rendering
    txtfile_path: str, pathname to the .txt file with all ffmpeg readable names in it"""

    voice_name = ""
    if name == "ari":
        voice_name = "en-US-Wavenet-F"
    if name == "alex":
        voice_name = "en-US-Wavenet-I"

    print("\nText to speech beginning now\n")
    language_code = "-".join(voice_name.split("-")[:2])
    voice_params = tts.VoiceSelectionParams(
        language_code=language_code, name=voice_name
    )
    audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)
    client = tts.TextToSpeechClient()

    # Setting any needed variables from the info_dict
    id = info_dict['Id']
    txtfile_path = os.path.join(
        os.getcwd(), downloads_path, f"{id}-audio-files.txt")

    # Using t4s to create headers list
    headers = list(t4s.keys())
    headers_list = []
    start = 0.0
    count = 0

    # Using the text_to_read list to create either T2S audio files or silence where necessary
    for i, string in enumerate(t2r):

        if string == '.':
            filename = os.path.join(
                os.getcwd(), downloads_path, f'{i}_silence_{id}.wav')
            os.system(
                f"ffmpeg -f lavfi -i anullsrc=channel_layout=mono:sample_rate=24000 -t 0.35 -acodec pcm_s16le {filename}")
            start += .1

        else:
            text_input = tts.SynthesisInput(text=string.replace("\n", ""))
            response = client.synthesize_speech(
                input=text_input, voice=voice_params, audio_config=audio_config, timeout=120.00
            )
            filename = os.path.join(
                os.getcwd(), downloads_path, f'{i}_t2s_{id}.wav')
            with open(filename, "wb") as out:
                out.write(response.audio_content)
                print(f'Generated speech saved to "{filename}"')
            duration = AudioSegment.from_file(filename).duration_seconds
            end = start + duration + .25
            if len(headers) > 1:
                headers_list.append(((start, end), headers[count]))
            else:
                headers_list.append(((start, end), headers[0]))
            count += 1
            start = end

        with codecs.open(txtfile_path, 'a', encoding="utf-8") as f:
            f.write(f"""file '{filename}'\n""")

    # Using the .txt file to concat all audio files into one and put it into final renders folder
    final_audio_path = os.path.join(
        os.getcwd(), downloads_path, f"{id}_t2s.wav")
    os.system(
        f"ffmpeg -f concat -safe 0 -i {txtfile_path} -c copy {final_audio_path}")

    print("\nFinal audio has been processed and concatenated.\n")
    return final_audio_path, headers_list

# Formulates subtitiles list


def speech_to_text(audio_uri, duration):
    """Analyzes audio file in GCP to create subtitles list for the final video

audio_uri:
    uri from GCP to the final audio to be analyzed
duration:
    duration of audio in float format

Returns:
    subtitles list for the subtitles_generator function"""

    print("\nAnalyzing audio for subtitles now.\n")
    client = speech.SpeechClient()
    config = {
        "language_code": "en-US",
        "enable_word_time_offsets": True,
        "enable_automatic_punctuation": True
    }

    if duration < 60:
        response = client.recognize(config=config, audio=audio_uri)

    else:
        response = client.long_running_recognize(
            config=config, audio=audio_uri).result()

    subs_list = []
    for result in response.results:
        for alternative in result.alternatives:
            for word in alternative.words:
                if not word.start_time:
                    start = 0
                else:
                    start = word.start_time.total_seconds()
                end = word.end_time.total_seconds()
                t = word.word
                subs_list.append(((float(start), float(end)), t))

    print("\nAudio analyzation complete.\n")
    return subs_list
