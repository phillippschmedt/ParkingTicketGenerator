import datetime
import os
import shutil
import time
from os import listdir

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from chromedriver_py import binary_path # this will get you the path variable

login_username = "phillipp.schmedt@gmail.com"
login_password = "TZ66Bfm$Ky2fj5N%Z"
chromedriver = binary_path

tickets_dir = os.path.join(os.getcwd(), "tickets")
temp_dir = os.path.join(os.getcwd(), "temp")

## Downloads ticket and returns path to ticket
def create_ticket(visitdate, platenumber):

    # Return Ticket Path if ticket already exists. 
    ticket_path = generate_ticket_path(visitdate, platenumber)
    if os.path.isfile(ticket_path):
        return ticket_path

    # Remove temp directory and create new one
    shutil.rmtree(temp_dir, ignore_errors=True)
    os.mkdir(temp_dir)

    # Chromedriver Settings
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1200x600') # optional
      
    browser = webdriver.Chrome(executable_path=chromedriver, chrome_options=options)

    # Whenever we use wait, we will wait for max 15 seconds. Then throw exceptions
    wait = WebDriverWait(browser, 15)

    params = {'behavior': 'allow', 'downloadPath': temp_dir} 
    browser.execute_cdp_cmd('Page.setDownloadBehavior', params)
    
    # Login-Page
    browser.get('https://serviceportal.hamburg.de/HamburgGateway/Account/Login')

    # Login-Page: Enter Username
    browser.find_element_by_id('Username').send_keys(login_username) 

    # Login-Page: Enter Password
    browser.find_element_by_id('Password').send_keys(login_password)

    # Login-Page: Submit
    browser.find_element_by_name('LoginUsingUsernamePassword').click()

    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'user__select')))

    # Accept DSGVO
    browser.get('https://serviceportal.hamburg.de/HamburgGateway/FVS/FV/LBV/Bewohnerparken/Besucherparken')

    browser.find_element_by_name('Dsgvo.DsgvoAcceptance').click()
    browser.find_element_by_css_selector('button[type="submit"]').click()

    wait.until(EC.presence_of_element_located((By.ID, 'BesucherStartProcessButton')))

    # Besucherparken-Form
    browser.get('https://serviceportal.hamburg.de/HamburgGateway/FVS/FV/LBV/Bewohnerparken/Besucherparken?nep=1')

    browser.find_elements_by_name('Besucherparken.CitizenModel.Salutation')[1].click()

    browser.find_element_by_name('Besucherparken.CitizenModel.BirthDate').send_keys("26.11.1987")

    browser.find_element_by_name('Besucherparken.CitizenModel.Street').send_keys("Bornstraße")

    browser.find_element_by_name('Besucherparken.CitizenModel.StreetNumber').send_keys("26")

    browser.find_element_by_name('Besucherparken.CitizenModel.ZipCode').send_keys("20146")

    browser.find_element_by_name('Besucherparken.VehicleModel.CompleteRegistration').send_keys(platenumber)

    browser.find_element_by_name('Besucherparken.VisitModel.Begin').send_keys(visitdate.strftime("%d.%m.%Y"))

    browser.find_element_by_name('Besucherparken.BPEVMConsent.Consent').click()

    browser.find_element_by_css_selector('button[type="submit"]').click()

    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[type="submit"]')))

    # ConfirmationPage
    browser.find_element_by_css_selector('button[type="submit"]').click()

    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[type="submit"]')))

    # Download Ticket
    browser.get("https://serviceportal.hamburg.de/HamburgGateway/FVS/FV/LBV/Bewohnerparken/Besucherparken/GetParkausweis?nep=1")

    # Wait for file to finish download
    while len(os.listdir(temp_dir)) == 0:
        time.sleep(1)

    # Extract the path to the downloaded file
    temp_file_path = os.path.join(temp_dir, os.listdir(temp_dir)[0])
    
    # Move Downloaded file to tickets directory
    shutil.copyfile(temp_file_path, ticket_path)

    browser.quit()
    
    return os.path.join(temp_dir, os.listdir(temp_dir)[0])

# Returns the full path for a ticket
def generate_ticket_path(visitdate, platenumber):
    timestamp = str(int(time.mktime(visitdate.timetuple())))
    destination_file_name = "ticket-" + platenumber + "_" + timestamp + ".pdf"
    destination_file_path = os.path.join(tickets_dir, destination_file_name)
    return destination_file_path
