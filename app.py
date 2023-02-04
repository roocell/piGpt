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
import pygame # for playing sound


pygame.init()
pygame.mixer.init(buffer=4096) #prevent underrun errors
class Speech():
    @classmethod
    def speak(cls, text):
        mp3_file_object = BytesIO()
        tts = gTTS(text, lang='en')
        tts.write_to_fp(mp3_file_object)
        pygame.mixer.music.load(mp3_file_object, 'mp3')
        pygame.mixer.music.play()
        # wait until done
        # while pygame.mixer.get_busy() == True:
        #     time.sleep(1)

openai.api_key = os.getenv('OPENAI_API_KEY')
model_engine = "text-davinci-003"
prompt = """
you have a python interface to a linux machine. you are able to write python code and execute it on this machine. 
I will ask you questions. your responses will always be in python code. if you have anything to say that is not python code
make sure it's displayed as a python comment.
my first task of you is to tell me what version of piOs is running. The best way to do this is to run "cat /etc/os-release"
and then search for VERSION_CODENAME.
"""

# Generate a response
def ask(prompt):
    completion = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=255,
        top_p=1,
        temperature=0.7,
        frequency_penalty=0,
        presence_penalty=0
    )
    return completion.choices[0].text

# to maintain conext, just keep appending to prompt with "/n" delimiters

response = ask(prompt)
print("===GPT CODE===")
print(response)
print("======")
# execute reponse
file = "gpt_start.py"
f = open(file, "w")
f.write(response)
f.close()
#os.system("python " + file)
p = subprocess.run(["python", file], capture_output=True, text=True)
print("STDOUT")
print(p.stdout)
print("STDERR")
print(p.stderr)

resp =  p.stdout
if "Traceback" in p.stderr:
    resp = "error running the code"
print("===GPT RESPONSE===")
print(resp)
print("======")
Speech.speak(resp)

time.sleep(30)

exit()
r = sr.Recognizer()
speech = sr.Microphone(device_index=2)
while 1:
    # get some input
    with speech as source:
        print("say something!…")
        audio = r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        recog = r.recognize_google(audio, language = 'en-US')
        print("You said: " + recog)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        continue
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
        continue

    response = ask(recog)[0:254]

    print("the response from GPT was ", response)
