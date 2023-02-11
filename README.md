# piGpt
interface with GPT on a raspi. GPT will write it's own code on the filesystem and execute to do various things.
<BR>
It has a connection to the internet.
<BR>
It can write it's own code and execute it.
<BR>
What can we make it do?
<BR>
![dog example](example1.jpg)

## correcting syntax errors
I manually got selenium working myself by installing the latest packages.<BR>
Once GPT generated some python code using selenium I soon found out that it was using deprecated functions.<BR>
At first I thought: darn, I'll have to figure out some older version of selenium to install.<BR>
But why would I do that when I can just instruct GPT what's changed?<BR>
```
The selenium python module has been udpated. here are the following changes:
- find_element_by_id("element_id") has been replaced with find_element(By.ID, "element_id")
```
I also noticed that sometimes it generated code missing import statements and with some plain text before the code.<BR>
```
Any additional text that isn't python code should be a python comment.
Always start the python code with a comment.
Make sure to import all necessary python modules.
```

## accessing the internet
Asking it to access the internet ran into issues.<BR>
Http 403 is returned from some sites that can detect bots.<BR>
```
Be sure to set yourself as User-Agent in any http requests.
```
Notice that I can be vague about this. It knows how to write this code.<BR>
Sometimes GPT likes to use 'example' URLs.<BR>
```
Use only real URLs.
```
Some sites run things like jQuery to update the page. This is a dumb approach but works.
I specifically mentioned the time module because if I didn't it used a selenium delay which didn't work.
```
Before reading any elements be sure to wait 2 seconds using the python time module.
```

## hints to GPT
GPT is very good at coming up with a solution, but if you give it a hint on how to do a particular thing
it will use that approach.
```
The best way to do this is to run "cat /etc/os-release" and then search for VERSION_CODENAME.
```

## webpage control
I have another raspi controlling a fireplace in my house.<BR>
It has a simple web interface and I can describe in plain text what GPT should do when it writes code.<BR>
```
If I ask anything about a fireplace here are some notes:
- To control a fireplace visit http://192.168.50.31:5555/ and click the button called triggerButton.
- The text in the button indicates if the fireplace is on or off. 
- Read the text of the button to determine the state of the fireplace and decide if to click the button or not.
- "Off" means the fireplace is currently off.
- "On" means the fireplace is currently on.
- Always respond with a print statement of the action that took place.
```
So I can ask GPT to 'turn on the fireplace' and it will <BR>
- generate the corresponding python code<BR>
- app.py will run the code and convert any output to speech and play it.<BR>
This results in something like this:
```
You said: turn on the fireplace
===GPT CODE===
# Import necessary modules
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

# Setup driver
options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

# Visit the webpage
driver.get("http://192.168.50.31:5555/")

# Wait for page to load
time.sleep(2)

# Check the text of the button
element = driver.find_element(By.ID, "triggerButton")
if element.text == "Off":
    # Fireplace is off, so turn it on
    element.click()
    print("Turning on the fireplace")
else:
    print("Fireplace is already on")
======
STDOUT
Turning on the fireplace
STDERR
===GPT RESPONSE===
Turning on the fireplace
======
```

## direction on methods
Once I notice that it's capable of writing code using a particular website, subsequent <BR>
requests can contain directions on how it should go about doing the job.
```
what's the current stock price for microsoft
```
versus
```
what's the current stock price for microsoft, use marketwatch.com
```

## auto installation of python modules
This prompt addition achieved the desired result first try.
First run of code will fail, then it'll see the error, write/run python code to install modules, then you can make your request again and it works.<BR>
Tip: to test you can speak "use the <XXXX> python module to ....."
```
If you see ModuleNotFoundError, then write python code to install the necessary modules.
```