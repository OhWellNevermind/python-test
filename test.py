import shutil
import string
import subprocess
import os
from os import listdir
from os.path import isfile, join

import random

import easyocr
import cv2

import tkinter.messagebox
from tkinter.ttk import Progressbar

import customtkinter
from tkinter import filedialog
from tkinter import *
import threading

from PIL import Image
from natsort import natsorted

from mutagen.mp3 import MP3

from moviepy.editor import *
from moviepy.decorators import *
from moviepy.video.fx import *
from moviepy.video.compositing.transitions import *
from moviepy.video.fx.all import crop

import numpy

import math

customtkinter.set_appearance_mode('dark')
customtkinter.set_default_color_theme('blue')

root = customtkinter.CTk()
root.resizable(False, False)
root.geometry('600x560')

tab_view = customtkinter.CTkTabview(root)
tab_view.pack()

tab_view.add('Generate Voice')
tab_view.add('Clear Text')
tab_view.add('Increase Image Size')
tab_view.add('Generate Video')

tab_view.set('Generate Voice')

generate_voice = tab_view.tab('Generate Voice')
increase_img_size = tab_view.tab('Increase Image Size')
clear_text = tab_view.tab('Clear Text')
generate_video = tab_view.tab('Generate Video')

root.title("Manhwa Helper")

# Generate Voice

script_location = None
audios_location = None

voices = {
    'Guy': 'en-US-GuyNeural',
}

label = customtkinter.CTkLabel(
    master=generate_voice, text="Generate Voice", font=("Roboto", 24, 'bold'))
label.pack(pady=15, padx=10)


def script_upload():
    global script_location
    script_location = filedialog.askopenfilename(
        title='Upload Script', filetypes=(('Text Files', '*.txt'),), initialdir='./')

    file_entry.configure(state=NORMAL)
    file_entry.delete(0, END)
    file_entry.insert(0, script_location)
    file_entry.configure(state=DISABLED)


def set_location():
    global audios_location
    audios_location = filedialog.askdirectory(initialdir='./')

    audios_entry.configure(state=NORMAL)
    audios_entry.delete(0, END)
    audios_entry.insert(0, audios_location)
    audios_entry.configure(state=DISABLED)


def voice_generation():
    script = open(script_location, 'r', encoding='utf-8')
    script_text = script.read()

    paragraphs = script_text.split('\n')
    print(paragraphs)

    script = []

    for line in paragraphs:
        if line.strip():
            script.append(line.strip())

    audio_files_raw = 'audio_files_raw'
    raw_video = '_raw'
    processed_video = '_processed'

    if not os.path.exists(audio_files_raw):
        os.makedirs(audio_files_raw)

    for i, phrase in enumerate(script):
        video_index = i + 1
        voice_file = f'{audio_files_raw}/{video_index}{raw_video}'

        cmd = f'edge-tts --voice {voices[voice_menu.get()]} --text "{phrase}" --write-media {voice_file}.mp3'
        subprocess.run(cmd, shell=True)

        processed_file = f'{audio_files_raw}/{video_index}{processed_video}'

        cmd = f'ffmpeg -y -i "{voice_file}.mp3" -vn -ar 44100 -ac 2 -b:a 192k {processed_file}.mp3'
        subprocess.run(cmd, shell=True)

        done_voice = f'{audios_location}/{video_index}'

        cmd = f'ffmpeg -y -i "{processed_file}.mp3" -af "silenceremove=1:start_duration=1:start_threshold=-90dB:detection=peak,aformat=dblp,areverse,silenceremove=start_periods=1:start_duration=1:start_threshold=-90dB:detection=peak,aformat=dblp,areverse" {done_voice}.mp3'
        subprocess.run(cmd, shell=True)

        progressValue = round(((i + 1) / len(script)) * 100, 1)

        progressbar.configure(value=progressValue)
        progress.configure(text=f'{progressValue}%')

        if progressValue == 100:
            tkinter.messagebox.showinfo(
                title='Done', message='Voice was generated')

    for fname in os.listdir('./audio_files_raw'):
        if '_processed' in fname:
            continue
        else:
            os.remove(os.path.join('./audio_files_raw', fname))


file_entry = customtkinter.CTkEntry(
    master=generate_voice, width=270, font=("Roboto", 15))
file_entry.configure(state=DISABLED)
file_entry.pack(pady=10)

upload_script = customtkinter.CTkButton(
    master=generate_voice, text='Upload Script', font=("Roboto", 15), command=script_upload)
upload_script.pack(pady=10)

audios_entry = customtkinter.CTkEntry(
    master=generate_voice, width=270, font=("Roboto", 15))
audios_entry.configure(state=DISABLED)
audios_entry.pack(pady=10)

audio_location = customtkinter.CTkButton(
    master=generate_voice, text='Set Location', font=("Roboto", 15), command=set_location)
audio_location.pack()

voice_label = customtkinter.CTkLabel(
    master=generate_voice, text="Select Voice", font=("Roboto", 15, 'bold'))
voice_label.pack(pady=10)

voice_menu = customtkinter.CTkComboBox(
    master=generate_voice, width=270, values=list(voices.keys()))
voice_menu.pack(pady=10)


def start():
    if not script_location or not audios_location:
        tkinter.messagebox.showerror(
            title='Error', message='Please set script location and save directory')
        return

    thread = threading.Thread(target=voice_generation)
    thread.start()
    # start_btn.configure(state=DISABLED)


start_btn = customtkinter.CTkButton(master=generate_voice, text='Start', font=(
    "Roboto", 20, 'bold'), width=220, height=40, command=start)
start_btn.pack(pady=25)

progressbar = Progressbar(master=generate_voice, length=300, value=0)
progressbar.pack(pady=8, padx=8)

progress = customtkinter.CTkLabel(
    master=generate_voice, text='0%', font=("Roboto", 16, 'bold'))
progress.pack(pady=5)

# Increase Image Size

images_location = None
image_size = 1.25


def get_images_location():
    global images_location
    images_location = filedialog.askdirectory(initialdir='./')
    print(images_location)
    image_entry.configure(state=NORMAL)
    image_entry.delete(0, END)
    image_entry.insert(0, images_location)
    image_entry.configure(state=DISABLED)


def increase_size():
    for i, image in enumerate((os.listdir(images_location))):
        img_path = os.path.join(images_location, image)
        img = Image.open(img_path)

        width, height = img.size
        new_width, new_height = int(
            width * image_size), int(height * image_size)

        resized_img = img.resize((new_width, new_height))
        resized_img.save(img_path)

        progressValue = round(
            ((i + 1) / len(os.listdir(images_location))) * 100, 1)

        images_progressbar.configure(value=progressValue)
        images_progress.configure(text=f'{progressValue}%')

        if progressValue == 100:
            tkinter.messagebox.showinfo(
                title='Done', message='Images size was increased')


size_label = customtkinter.CTkLabel(
    master=increase_img_size, text="Increase Image Size", font=("Roboto", 24, 'bold'))
size_label.pack(pady=15, padx=10)

image_entry = customtkinter.CTkEntry(
    master=increase_img_size, width=270, font=("Roboto", 15))
image_entry.configure(state=DISABLED)
image_entry.pack(pady=10)

image_location = customtkinter.CTkButton(
    master=increase_img_size, text='Set Location', font=("Roboto", 15), command=get_images_location)
image_location.pack(pady=10)


def images_start():
    if not images_location:
        tkinter.messagebox.showerror(
            title='Error', message='Please set images location')
        return

    thread = threading.Thread(target=increase_size)
    thread.start()
    images_start_btn.configure(state=DISABLED)


def set_size(value):
    global image_size
    image_size = round(value, 2)
    size_slider_label.configure(text=f'Size: {image_size}x')


size_slider_label = customtkinter.CTkLabel(
    master=increase_img_size, text="Size: 1.25x", font=("Roboto", 15, 'bold'))
size_slider_label.pack(pady=6)

size_slider = customtkinter.CTkSlider(
    master=increase_img_size, from_=1, to=1.5, number_of_steps=10, command=set_size)
size_slider.pack()
size_slider.set(1.25)

images_start_btn = customtkinter.CTkButton(master=increase_img_size, text='Start', font=(
    "Roboto", 20, 'bold'), width=220, height=40, command=images_start)
images_start_btn.pack(pady=25)

images_progressbar = Progressbar(master=increase_img_size, length=300, value=0)
images_progressbar.pack(pady=8, padx=8)

images_progress = customtkinter.CTkLabel(
    master=increase_img_size, text='0%', font=("Roboto", 16, 'bold'))
images_progress.pack(pady=5)

# Clear Text

confidence = 0.15
clear_images_location = None


def import_images():
    global clear_images_location
    clear_images_location = filedialog.askdirectory()

    clear_entry.configure(state=NORMAL)
    clear_entry.delete(0, END)
    clear_entry.insert(0, clear_images_location)
    clear_entry.configure(state=DISABLED)


def set_confidence(value):
    global confidence
    confidence = round(value, 2)
    clear_slider_label.configure(text=f'Confidence: {confidence}')


def get_images_path(image):
    return clear_images_location + '/' + image


def delete_text():
    images = natsorted(
        list(map(get_images_path, os.listdir(clear_images_location))))

    language = language_menu.get()

    if language == "Korean":
        language = "ko"
    elif language == "Japanese":
        language = "ja"
    elif language == "English":
        language = "en"
    elif language == "Russian":
        language = "ru"

    for index, image in enumerate(images):
        # Copies image and remove non-unicode characters
        if not image.isascii():
            name = ''.join(c for c in image if c in string.printable)

            if os.path.splitext(os.path.basename(name))[1] == '':
                basename = ""
                ext = os.path.splitext(os.path.basename(name))[0]
            else:
                basename = os.path.splitext(os.path.basename(name))[0]
                ext = os.path.splitext(os.path.basename(name))[1]

            name = os.path.join(os.path.dirname(
                image), basename + str(index) + ext)
            shutil.copy(image, name)
            image = name

        # OCR
        reader = easyocr.Reader([language])
        result = reader.readtext(image, batch_size=16)

        # Read the image
        img_rect = cv2.imread(image)
        img_temp = cv2.imread(image)
        h, w, c = img_temp.shape

        # Fill temp image with black
        img_temp = cv2.rectangle(img_temp, [0, 0], [w, h], (0, 0, 0), -1)
        img_inpaint = cv2.imread(image)

        raw_list = []
        rects = []

        # For each detected text
        for r in result:

            # If the OCR text is above the CONFIDENCE
            if r[2] >= confidence:
                # Add text to raw list
                raw_list.append(r[1])

                # Save the tuple of top right and bottom left of where the text is
                # Bottom Left = r[0][0]
                # Bottom Right = r[0][1]
                # Top Right = r[0][2]
                # Top Left = r[0][3]
                bottom_left = tuple(int(x) for x in tuple(r[0][0]))
                top_right = tuple(int(x) for x in tuple(r[0][2]))

                # Add rectangles to a list
                rects.append((top_right, bottom_left))

                # Draw a rectangle around the text
                img_rect = cv2.rectangle(
                    img_rect, bottom_left, top_right, (0, 255, 0), 3)

                # Fill text with white rectangle
                img_temp = cv2.rectangle(
                    img_temp, bottom_left, top_right, (255, 255, 255), -1)

                # Convert temp image to black and white for mask
                mask = cv2.cvtColor(img_temp, cv2.COLOR_BGR2GRAY)

                # "Content-Fill" using mask (INPAINT_NS vs INPAINT_TELEA)
                img_inpaint = cv2.inpaint(
                    img_inpaint, mask, 3, cv2.INPAINT_TELEA)

                # Draw a rectangle around the text
                preview_rect = cv2.rectangle(
                    img_rect, bottom_left, top_right, (0, 255, 0), 3)

                # Draw confidence level on detected text
                cv2.putText(preview_rect, str(round(r[2], 2)), bottom_left, cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (0, 0, 0), 1, 1)

        export_path = clear_images_location + ' processed/'

        if not os.path.exists(export_path):
            os.makedirs(export_path)

        cv2.imwrite(export_path + image.split('/')[-1], img_inpaint)

        progressValue = round(
            ((index + 1) / len(os.listdir(clear_images_location))) * 100, 1)

        clear_progressbar.configure(value=progressValue)
        clear_progress.configure(text=f'{progressValue}%')

        if progressValue == 100:
            tkinter.messagebox.showinfo(
                title='Done', message='Text was deleted')


def clear_start():
    if not clear_images_location:
        tkinter.messagebox.showerror(
            title='Error', message='Please set images location')
        return

    thread = threading.Thread(target=delete_text)
    thread.start()
    clear_start_btn.configure(state=DISABLED)

# Make video


voices_location = None
video_images_location = None


def get_voices_location():
    global voices_location
    voices_location = filedialog.askdirectory(initialdir='./')
    print(voices_location)
    video_audios_entry.configure(state=NORMAL)
    video_audios_entry.delete(0, END)
    video_audios_entry.insert(0, voices_location)
    video_audios_entry.configure(state=DISABLED)


def get_video_images_location():
    global video_images_location
    video_images_location = filedialog.askdirectory(initialdir='./')
    print(video_images_location)
    video_image_entry.configure(state=NORMAL)
    video_image_entry.delete(0, END)
    video_image_entry.insert(0, video_images_location)
    video_image_entry.configure(state=DISABLED)


def get_random_animation(clip):
    random_num = random.randint(0, 7)
    # random_num = 7
    print(random_num)
    if (random_num == 0):
        clip = clip.set_position(lambda t: (t * 20 + 10, -(t * 20) + 10))
        clip.fps = 30
        return clip
    elif (random_num == 1):
        clip = zoom_in_effect(clip, zoom_ratio=0.04)
        return clip
    elif (random_num == 2):
        clip = clip.set_position(lambda t: (-(t * 20) + 10, -(t * 20) + 10))
        clip.fps = 30
        return clip
    elif (random_num == 3):
        clip = zoom_out_effect(clip, zoom_ratio=0.04)
        return clip
    elif (random_num == 4):
        clip = clip.set_position(lambda t: (t * 20 + 20, t * 20 + 20))
        clip.fps = 30
        return clip
    elif (random_num == 5):
        clip = clip.set_position(lambda t: (t * 30 + 10, 'center'))
        clip.fps = 30
        return clip
    elif (random_num == 6):
        clip = clip.set_position(lambda t: (-(t * 30) + 10, 'center'))
        clip.fps = 30
        return clip
    elif (random_num == 7):
        clip = clip.set_position(lambda t: (-(t * 20) + 10, t * 20 + 10))
        clip.fps = 30
        return clip


def zoom_in_effect(clip, zoom_ratio=0.04):
    def effect(get_frame, t):
        img = Image.fromarray(get_frame(t))
        base_size = img.size

        new_size = [
            math.ceil(img.size[0] * (1 + (zoom_ratio * t))),
            math.ceil(img.size[1] * (1 + (zoom_ratio * t)))
        ]

        # The new dimensions must be even.
        new_size[0] = new_size[0] + (new_size[0] % 2)
        new_size[1] = new_size[1] + (new_size[1] % 2)

        img = img.resize(new_size, Image.LANCZOS)

        x = math.ceil((new_size[0] - base_size[0]) / 2)
        y = math.ceil((new_size[1] - base_size[1]) / 2)

        img = img.crop([
            x, y, new_size[0] - x, new_size[1] - y
        ]).resize(base_size, Image.LANCZOS)

        result = numpy.array(img)
        img.close()

        return result

    return clip.fl(effect)


def zoom_out_effect(clip, zoom_ratio=0.01):
    def effect(get_frame, t):
        img = Image.fromarray(get_frame(t))
        base_size = img.size

        new_size = [
            math.ceil(img.size[0] * (1 - (zoom_ratio * t))),
            math.ceil(img.size[1] * (1 - (zoom_ratio * t)))
        ]

        # The new dimensions must be even.
        new_size[0] = new_size[0] + (new_size[0] % 2)
        new_size[1] = new_size[1] + (new_size[1] % 2)

        img = img.resize(new_size, Image.LANCZOS)

        x = math.ceil((new_size[0] - base_size[0]) / 2)
        y = math.ceil((new_size[1] - base_size[1]) / 2)

        img = img.crop([
            x, y, new_size[0] - x, new_size[1] - y
        ]).resize(base_size, Image.LANCZOS)

        result = numpy.array(img)
        img.close()

        return result

    return clip.fl(effect)


def create_video():
    clips = []

    voices = natsorted(list(['./audio_files_raw/{}'.format(f) for f in listdir(
        './audio_files_raw') if isfile(join('./audio_files_raw', f))]))
    images = natsorted(list(['./images/{}'.format(f)
                       for f in listdir('./images') if isfile(join('./images', f))]))

    i = True
    for img, voice in zip(images, voices):
        audio = AudioFileClip(voice)
        audio_length = audio.duration - 0.5
        clip = ImageClip(img, duration=audio_length, ismask=False)
        clip.size = (1920, 1080)
        clip = clip.on_color(color=(0, 0, 0), col_opacity=1)
        clip = clip.set_audio(audio)
        if not i:
            clip = get_random_animation(clip)
        i = False
        bg = ColorClip(size=(1920, 1080),
                       duration=audio_length, color=(0, 0, 0))
        video = VideoClip(bg.make_frame, duration=audio_length)
        video_with_img = CompositeVideoClip([video, clip])

        clips.append(video_with_img)
        bg.close()

    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile("./Final.mp4", fps=30)


video_images_label = customtkinter.CTkLabel(
    master=generate_video, text="Select Images Path", font=("Roboto", 15, 'bold'))
video_images_label.pack(pady=10)

video_image_entry = customtkinter.CTkEntry(
    master=generate_video, width=270, font=("Roboto", 15))
video_image_entry.configure(state=DISABLED)
video_image_entry.pack(pady=10)

video_image_location = customtkinter.CTkButton(
    master=generate_video, text='Set Location', font=("Roboto", 15), command=get_video_images_location)
video_image_location.pack(pady=10)

video_voice_label = customtkinter.CTkLabel(
    master=generate_video, text="Select Voices Path", font=("Roboto", 15, 'bold'))
video_voice_label.pack(pady=10)

video_audios_entry = customtkinter.CTkEntry(
    master=generate_video, width=270, font=("Roboto", 15))
video_audios_entry.configure(state=DISABLED)
video_audios_entry.pack(pady=10)

video_audio_location = customtkinter.CTkButton(
    master=generate_video, text='Set Location', font=("Roboto", 15), command=get_voices_location)
video_audio_location.pack()


def video_start():
    if not video_images_location or not voices_location:
        tkinter.messagebox.showerror(
            title='Error', message='Please set images and video location location')
        return

    thread = threading.Thread(target=create_video)
    thread.start()


video_start_btn = customtkinter.CTkButton(master=generate_video, text='Start', font=(
    "Roboto", 20, 'bold'), width=220, height=40, command=video_start)
video_start_btn.pack(pady=25)


video_progressbar = Progressbar(master=generate_video, length=300, value=0)
video_progressbar.pack(pady=8, padx=8)

video_progress = customtkinter.CTkLabel(
    master=generate_video, text='0%', font=("Roboto", 16, 'bold'))
video_progress.pack(pady=5)

# Others

clear_label = customtkinter.CTkLabel(
    master=clear_text, text="Clear Text", font=("Roboto", 24, 'bold'))
clear_label.pack(pady=15, padx=10)

clear_entry = customtkinter.CTkEntry(
    master=clear_text, width=270, font=("Roboto", 15))
clear_entry.configure(state=DISABLED)
clear_entry.pack(pady=10)

clear_location = customtkinter.CTkButton(
    master=clear_text, text='Import Images', font=("Roboto", 15), command=import_images)
clear_location.pack(pady=10)

language_label = customtkinter.CTkLabel(
    master=clear_text, text="Select Language", font=("Roboto", 15, 'bold'))
language_label.pack(pady=10)

language_menu = customtkinter.CTkComboBox(master=clear_text, width=270, values=[
                                          "English", "Japanese", "Korean", "Russian"])
language_menu.pack(pady=10)

clear_slider_label = customtkinter.CTkLabel(
    master=clear_text, text="Confidence: 0.15", font=("Roboto", 15, 'bold'))
clear_slider_label.pack(pady=10)

clear_slider = customtkinter.CTkSlider(
    master=clear_text, from_=0, to=1, number_of_steps=100, command=set_confidence)
clear_slider.pack()

clear_start_btn = customtkinter.CTkButton(master=clear_text, text='Start', font=(
    "Roboto", 20, 'bold'), width=220, height=40, command=clear_start)
clear_start_btn.pack(pady=25)

clear_progressbar = Progressbar(master=clear_text, length=300, value=0)
clear_progressbar.pack(pady=8, padx=8)

clear_progress = customtkinter.CTkLabel(
    master=clear_text, text='0%', font=("Roboto", 16, 'bold'))
clear_progress.pack(pady=5)

root.mainloop()
