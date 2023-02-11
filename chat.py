#!/usr/bin/env python

import os
import subprocess # to run stuff and get output
import time
import dotenv # to put OPENAPI key in .env file
dotenv.load_dotenv()
import openai
import speech_recognition as sr
from pydub import AudioSegment
import sounddevice # gets rid of those annoying ALSA errors

from gtts import gTTS # text to speech
from io import BytesIO # to pipe voice to object rather than file

from pydub import AudioSegment # using pydub rather than pygame prevent all those ALSA undderruns
from pydub.playback import play

# helping GPT a little by installing some stuff
# selenium, chromium-browser, pyvirtualdisplay


# determine device_index for webcam mic
# Input Device id  1  -  USB Device 0x46d:0x821: Audio (hw:3,0)
# sr.Microphone(device_index=1)
import pyaudio
p = pyaudio.PyAudio()
info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')

for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print ("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))


class Speech():
    @classmethod
    def speak(cls, text):
        if text == "":
            print("nothing to say")
            return
        mp3_file_object = BytesIO()
        tts = gTTS(text, lang='en')
        tts.write_to_fp(mp3_file_object)

        mp3_file_object.seek(0)
        play(AudioSegment.from_file(mp3_file_object, format="mp3"))

openai.api_key = os.getenv('OPENAI_API_KEY')
model_engine = "text-davinci-003"
prompt = """
We're going to have a conversation about anything.
"""

# Generate a response
def ask(prompt):
    print("contacting GPT...")
    try:
        completion = openai.Completion.create(
            engine=model_engine,
            prompt=prompt,
            max_tokens=1024,
            top_p=1,
            temperature=0.7,
            frequency_penalty=0,
            presence_penalty=0,
            request_timeout = 30
        )
        return completion.choices[0].text
    except Exception as e:        
        print("openai error", e)
        return "print(\"openai is down\")"

r = sr.Recognizer()
Speech.speak("say something")
speech = sr.Microphone(device_index=1)
while 1:
    # get some input
    with speech as source:
        print("say something!…")
        audio = r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        print("converting speech to text...")
        recog = r.recognize_google(audio, language = 'en-US')
        print("You said: " + recog)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        continue
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
        continue

    # to maintain conext, just keep appending to prompt with "/n" delimiters ?
    prompt += recog + "\n"
    response = ask(prompt)
    Speech.speak(response)

