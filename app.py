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
You have a python interface to a raspberry pi running piOS. you are able to write python code and execute it on this machine. 
I will tell you to do things. Your responses will always be in python code.
Any additional text that isn't python code should be a python comment.
Always start the python code with a comment.
Make sure to import all necessary python modules.

You are very good at parsing the code of webpages using python to figure out what to do on the webpage.
You do this by using the selenium module in python and chromium driver running on a headless raspberry pi.
Be sure to run headless by using the following
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
The selenium python module has been udpated. here are the following changes:
- find_element_by_id("element_id") has been replaced with find_element(By.ID, "element_id")
Before reading any elements be sure to wait 5 seconds using the python time module.

To control a fireplace visit http://192.168.50.31:5555/ and click the button called triggerButton.
The text in the button indicates if the fireplace is on or off. 
Read the text of the button to determine the state of the fireplace and decide if to click the button or not.
"Off" means the fireplace is currently off.
"On" means the fireplace is currently on.
Always respond with a print statement of the action that took place.

My first task of you is to tell me what version of piOs is running.
The best way to do this is to run "cat /etc/os-release" and then search for VERSION_CODENAME.

"""

# You can also write python code to run "pip" or "apt-get" to install anything you need to run the python script.


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


def gptRunCode(prompt):
    response = ask(prompt)
    print("===GPT CODE===")
    print(response)
    print("======")

    # we've asked GPT to always start the python code with a comment
    # let's start there
    i = response.index('#')
    response = response[i:]

    # execute reponse
    file = "code.py"
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

    # ModuleNotFoundError: No module named 'playsound'
    # should we install python modules?

    errors = [
        "Traceback",
        "SyntaxError",
        "IndentationError"
    ]
    if any(err in p.stderr for err in errors):
        resp = "error running the code"
    print("===GPT RESPONSE===")
    print(resp)
    print("======")
    return resp

resp = gptRunCode(prompt)
Speech.speak(resp)

r = sr.Recognizer()

speech = sr.Microphone(device_index=1)
while 1:
    # get some input
    with speech as source:
        print("say something!…")
        audio = r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        print("speech to text...")
        recog = r.recognize_google(audio, language = 'en-US')
        print("You said: " + recog)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        continue
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
        continue

    # to maintain conext, just keep appending to prompt with "/n" delimiters
    prompt += "\n" + recog
    print(prompt)
    resp = gptRunCode(prompt)
    Speech.speak(resp)
