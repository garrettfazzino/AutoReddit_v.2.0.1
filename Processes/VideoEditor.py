from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip, ImageClip, VideoClip
from moviepy.video.tools.subtitles import SubtitlesClip
import os
from datetime import datetime
from pydub import AudioSegment
from scipy.io import wavfile
from PIL import Image, ImageDraw
import numpy as np
from random import choice

"""Creates 1 min videos using the data scraped from the RedditScraper.py file."""

# Creates r/subreddit object
def title_obj_gen(title, name):
    """Creates r/subreddit style titles for the videos

title:
    The name of the subreddit the post came from

Returns: title object for moviepy compiler"""

    font = ''
    if name == 'ari':
        font = "Media/Glossy Sheen Shine.ttf"
    if name == 'alex':
        font = "Media/ChangaOne-Regular.ttf"

    # .set_position((.2,.2), relative=True)
    title_object = TextClip(txt=f"r/{title}",
                            font=font,
                            fontsize=100,
                            color='WhiteSmoke',
                            # bg_color='gray30',
                            stroke_color='black',
                            stroke_width=2.0,
                            )

    return title_object

# Creates textbody subtitles object
def sub_obj_gen(subtitles_list=list, name=str):
    """Creates textbody subtitles for the videos

subtitles_list:
    List returned by the speech_to_text function

Returns: subtitles object for moviepy compiler"""

    font = ''
    if name == 'ari':
        font = "Media/Glossy Sheen Shine.ttf"
    if name == 'alex':
        font = "Media/ChangaOne-Regular.ttf"

    def generator(txt): return TextClip(txt,
                                        font=font,
                                        fontsize=150,
                                        stroke_color='black',
                                        stroke_width=2.0,
                                        # bg_color='gray30',
                                        color='WhiteSmoke')

    # .set_position((.2,.3), relative=True)
    subtitle_object = SubtitlesClip(subtitles_list, generator)

    return subtitle_object

# Creates u/redditor heading object
def header_obj_gen(headers_list, name):
    """Creates u/redditor style header(s) for the videos

headers_list:
    List returned by the t2s function

Returns: headers object for moviepy compiler"""

    font = ''
    if name == 'ari':
        font = "Media/Glossy Sheen Shine.ttf"
    if name == 'alex':
        font = "Media/ChangaOne-Regular.ttf"

    def generator(txt): return TextClip(txt,
                                        font=font,
                                        fontsize=80,
                                        stroke_color='WhiteSmoke',
                                        stroke_width=1.0,
                                        color='black',
                                        # bg_color='gray30'
                                        )

    # .set_position((.7,.2), relative=True)
    header_object = SubtitlesClip(headers_list, generator)

    return header_object

# CCR, creates correct cut from screen and resizes to 1080p x 1920p
def cut_crop_resize(downloads_path, videopath, time):
    """Funnction that takes the input video then crops it to the alotted time, the image/resizes for proper screen ratio
dir_path: 
    path returned from 'directorymaker' function
filename:
    str, filename returned from the 'bgvideo_downloader' function
time: 
    int, returned from the concatenation of audio function (yet to be created)

Returns: pathname to final video output"""

    print("\nCCR beginning now.\n")
    output_filename = f"ccr_{videopath[-1:-10]}.mp4"
    ccr_video_path = os.path.join(downloads_path, output_filename)

    # Correctly takes a 1080p background video cuts it to time length, then crops and resizes it to proper dimensions for upload
    os.system(
        f"""ffmpeg -t {time} -i {videopath} -vf "crop=607.5:1080:655:0,scale=1080:-1" {ccr_video_path}""")

    print("\nCCR complete.\n")
    return ccr_video_path

# Creates Ari's speech bubble
def speech_bubble_object(audiopath=str, duration=float, ccr_path=str):
    """Creates the make_frame function to support Ari's speech bubble

audiopath:
    local path to final audio
duration:
    length of audio in float format
ccr_path:
    local path to ccr video

Returns VideoClip object for moviepy compiler"""

    video = VideoFileClip(ccr_path)
    w, h = video.size

    def audio_ratio(audiopath, duration):
        print("\nAnalyzing audio now.\n")
        # Opening audio through scipy / pydub
        f = wavfile.read(audiopath)
        # Creating needed variables
        numsamples = len(f[1])
        samplerate = numsamples/duration
        fps = 60
        sample_per_frame = [abs(x) for x in f[1][0::int(samplerate/fps)]]
        normalized_per_frame = [(x/(max(sample_per_frame)))
                                for x in sample_per_frame]
        size_per_frame = []
        for x in normalized_per_frame:
            if x >= .75:
                size_per_frame.append(1)
            elif .5 <= x < .75:
                size_per_frame.append(.75)
            elif .1 <= x < .5:
                size_per_frame.append(.5)
            else:
                size_per_frame.append(0)

        return size_per_frame

    size_per_frame = audio_ratio(audiopath=audiopath,
                                 duration=duration)

    # Using make_frame function to create each frame which will be added to the final video for speech bubble
    print("\nCreating speech bubble frames.\n")

    colors_list = ['pink', 'green', 'purple',
                   'blue', 'orange', 'red', 'yellow']
    outline_color = choice(colors_list)

    def make_frame(t):
        index = int(t*60)
        ratio = size_per_frame[index]
        r = int(162+(ratio*16))
        x = w/2
        y = h/2
        leftUpPoint = (x-r, y-r)
        rightDownPoint = (x+r, y+r)
        twoPointList = [leftUpPoint, rightDownPoint]
        frame = Image.fromarray(video.get_frame(t))
        draw = ImageDraw.Draw(frame)
        draw.ellipse(twoPointList, fill='black',
                     outline=outline_color, width=9)
        # outline=(0,80,100,40)
        finalframe = np.array(frame)

        return finalframe

    print("\nYour character can now speak!\n")
    return VideoClip(make_frame, duration=duration)

# Compiles audio, video, and text bodies into final output
def video_compiler(title, subtitles, sb_video, audiopath, downloads_path, info_dict, name, heading=None):
    """Concatenates bgvideo, with texts and audio

title:
    TextClip object from textclip_generator
subtitles: 
    SubtitlesClip object, contains subtitles for display
sb_video: 
    path to the speech_bubble_object
audiopath: 
    str, path to fully processed audio
downloads_path:
    path to downloads folder
info_dict: 
    info_dict from csv2dict function
name:
    name of the character chosen for the current iteration
heading: 
    TextClip object, cotainins headers

Returns: final video path"""

    facepath = ''
    if name == 'ari':
        facepath = "Media/ari_circle.png"
    if name == 'alex':
        facepath = "Media/alex_circle.png"
    print("\nVideo compiling beginning now.\n")
    duration = sb_video.duration
    face = ImageClip(facepath, duration=duration)
    title = title.set_duration(duration)
    result = CompositeVideoClip([sb_video,
                                title.set_position(
                                    ('center', .29), relative=True),
                                heading.set_position(
                                    ('center', .36), relative=True),
                                subtitles.set_position(
                                    ('center', .61), relative=True),
                                face.set_position(('center', 'center'))
                                 ])

    # USE THESE IN CASE OF 'audio=' not working correctly
    voiceaudio = AudioFileClip(audiopath)
    # bgaudio = AudioFileClip(bgaudiopath)
    # lowerbgaudio = bgaudio.fx(volumex, .3)
    final = result.set_audio(voiceaudio)
    output_path = f"{downloads_path}/{info_dict['Id']}_finalvideo_{datetime.now().date()}.mp4"

    final.write_videofile(
        filename=output_path,
        fps=60,
        # audio=lowerbgaudio,
        remove_temp=True,
        codec="libx264",
        audio_codec="aac"
    )

    print("\nVideo has been fully compiled\n")
    return output_path

# Chops final blended video into 1min sections
def video_chopper(compiled_video_path, downloads_path, final_renders_path, duration, bgaudio_path=None, cut_time=60):
    """Cuts the final compiled video path into 60s long segments for posting

compiled_video_path:
    path produced by video_compiler function
downloads_path:
    path to downloads folder
final_renders_path:
    path to final renders folder
duration:
    duration in float format
bgaudio_path:
    path to background audio (instrumental)
cut_time:
    length of desired cuts, automatically set to 60s"""

    print("\nGet down, GET TO THE CHOPPPAAAAHHH\n")
    if bgaudio_path:  # CURRENTLY NOT WORKING
        merge_path = os.path.join(
            os.getcwd(), downloads_path, "bgaudio_merged.mp4")
        os.system(
            f"""ffmpeg -i {compiled_video_path} -i {bgaudio_path} -filter_complex [0:a] volume=0.4 [music] [1:a] amix=inputs=2:duration=longest [audio_out] -map 0:v -map [audio_out] {merge_path}""")

        start = 0
        for x in range(int((duration//cut_time)+1)):
            output_path = os.path.join(
                os.getcwd(), downloads_path, "final_renders" f"fincut{x}.mp4")
            if duration > cut_time:
                os.system(
                    f"ffmpeg -ss 00:0{x}:00.00 -i {merge_path} -t 00:01:00.00 {output_path}")
                start += 60
            else:
                final_cut = duration - start
                os.system(
                    f"ffmpeg -ss 00:0{x}:00.00 -i {merge_path} -t 00:00:{final_cut} {output_path}")

        print("\nVideo have been chopped.\n")
        return

    else:
        start = 0
        for x in range(int((duration//cut_time)+1)):
            output_path = os.path.join(
                os.getcwd(), final_renders_path, f"fincut{x}.mp4")
            if duration > cut_time:
                os.system(
                    f"ffmpeg -ss 00:0{x}:00.00 -i {compiled_video_path} -t 00:01:00.00 {output_path}")
                start += 60
            else:
                final_cut = duration - start
                os.system(
                    f"ffmpeg -ss 00:0{x}:00.00 -i {compiled_video_path} -t 00:00:{final_cut} {output_path}")

        print("\nVideo have been chopped.\n")
        return
