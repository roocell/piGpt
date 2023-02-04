import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By

# https://patrikmojzis.medium.com/how-to-run-selenium-using-python-on-raspberry-pi-d3fe058f011

# this give you chromedriver 104 which will work with the chrome-broswer (104) installed using apt-get
# https://github.com/electron/electron/releases/download/v21.4.1/chromedriver-v21.4.1-linux-armv7l.zip

#'chromedriver' executable needs to be in PATH

#Visit the page http://192.168.50.31:5555/ and click the button called triggerFireplace
options = webdriver.ChromeOptions()
options.add_argument('--headless')

### ONLY UNCOMMENT AND TRY USING THESE OPTIONS, IF YOU GET AN ERROR RUNNING THIS SCRIPT
# options.add_argument('--no-sandbox')
# options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(chrome_options=options)

# this was copied (almost) directly from a GPT output!
driver.get("http://192.168.50.31:5555/")
triggerFireplace_button = driver.find_element(By.ID, "triggerButton")
triggerFireplace_button.click()
