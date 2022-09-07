#!/usr/bin/python3

from lxml import etree as ET
from configparser import ConfigParser
from urllib import error, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from PIL import Image
from inky.auto import auto
import random
import os
import sys


installLocation = "/home/pi/PosterPi/"

#Constants
s= Service('/usr/bin/chromedriver')
config = ConfigParser()
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US;en;q=0.5',
    'Host': 'anidb.net',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0'
}


def _get_plexToken():
    """Fetch the API key from your configuration file.
    Expects a configuration file named "config.ini" with structure:

        [Plex]
        plexToken=YOUR-PLEX-TOKEN-KEY

    """

    config.read(f"{installLocation}config.ini")
    return config["Plex"]["plexToken"]
plex_token = _get_plexToken ()

def _get_plexUrl():
    """Fetch the API key from your configuration file.
    Expects a configuration file named "config.ini" with structure:

        [Plex]
        plexUrl=YOUR-PLEX-SERVER-URL:PORT

    """
    config.read(f"{installLocation}config.ini")
    return config["Plex"]["plexServerUrl"]
plex_server = _get_plexUrl()

def _get_plexAccount():
    """Fetch the API key from your configuration file.
    Expects a configuration file named "config.ini" with structure:

        [Plex]
        plexAccount=YOUR-PLEX-ACCOUNT-NAME

    """

    config.read(f"{installLocation}config.ini")
    return config["Plex Account"]["account"]
plex_account = _get_plexAccount ()

def _get_plexPlayHistory():
    """Fetch the API key from your configuration file.
    Expects a configuration file named "config.ini" with structure:

        [Plex Play History]
        history=YOUR-PLEX-POSTER-URL-FROM-LAST-SESSION


    """

    config.read(f"{installLocation}config.ini")
    return config["Plex Play History"]["history"]

plex_history = _get_plexPlayHistory ()

def _get_artPath():
    """Fetch the API key from your configuration file.
    Expects a configuration file named "config.ini" with structure:

        [Art]
        folderPath=/your/art/folder/path/

    """

    config.read(f"{installLocation}config.ini")
    return config["Art"]["folderpath"]
artFolder = _get_artPath ()

def _get_queryUrl():
#Builds the URL to query Plex Server.

    urlQuery = (
        f"{plex_server}/status/sessions?X-Plex-Token={plex_token}"
 )

    return urlQuery

queryPlexURL = _get_queryUrl()
print(queryPlexURL) # <-Test the Plex Query URL construction works

#Opens and reads the XML file provided by Plex Query
#with open (dataPlexAPI) as XML_File:

try:
    responsePlex = request.urlopen(queryPlexURL)
except error.HTTPError as http_error:
    if http_error.code == 401:  # 401 - Unauthorized
        sys.exit("Access denied. Check your token.")
    elif http_error.code == 404:  # 404 - Not Found
        sys.exit("Can't find plex data.")
    else:
        sys.exit(f"Something went wrong... ({http_error.code})")

plexRead = ET.parse(responsePlex)
root= plexRead.getroot()
#print(ET.tostring(root, encoding='utf8').decode('utf8')) #<- Test xml conversion
ET.tostring(root, encoding='utf8').decode('utf8')


nowPlayingType = plexRead.xpath('/MediaContainer/Video/@librarySectionTitle')
nowPlayingAccount = plexRead.xpath("/MediaContainer/Video/User/@title")

#print(nowPlayingType) # <-Test that nowPlayingType works
#Check for the current type of content playing
if nowPlayingType == ['Movies']:
    nowPlayingDetails=plexRead.xpath('/MediaContainer/Video/@thumb')
    print(nowPlayingDetails)
    poster = nowPlayingDetails[0]
elif nowPlayingType == ['TV Shows']:
    nowPlayingDetails = plexRead.xpath('/MediaContainer/Video/@grandparentThumb')
    print(nowPlayingDetails)
    poster = nowPlayingDetails[0]
elif nowPlayingType == ['3D']:
    nowPlayingDetails=plexRead.xpath('/MediaContainer/Video/@thumb')
    print(nowPlayingDetails)
    poster = nowPlayingDetails[0]
else:
    poster = ""

print(poster)

if poster != "":

    #Builds the URL to get the poster from the Plex Server.

    plexPosterURL = (f"{plex_server}{poster}/status/sessions?X-Plex-Token={plex_token}")

    print("Plex Poster Art located at:")
    print(plexPosterURL)
    #Checks if what you are watching has changed since the last time the script ran
    if plexPosterURL != plex_history:
        print('Updating Playing History')
        config["Plex Play History"] = {
            "history": plexPosterURL,
        }
        #Write the above sections to config.ini file
        with open(f"{installLocation}config.ini", 'w') as conf:
            config.write(conf)

        #Saves the poster of whatever is playing on plex locally.
        request.urlretrieve(plexPosterURL, f"{installLocation}nowWatchingPoster.jpg")
        print("Now playing image saved locally")
        # Take Screenshot of PlexPoster.html
        print("Taking screenshot of the poster")
        options = Options()
        options.add_argument( "--headless" )
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        width = 448
        height = 600
        driver = webdriver.Chrome(options=options, service=s)
        driver.set_window_size(width, height)
        driver.get('file:///home/pi/PosterPi/PlexPoster.html') #Installed Directory
        driver.save_screenshot(f"{installLocation}Poster.png")
        driver.quit()
        #Display Completed Image "Poster.png" and puts the "Now Showing" banner and a border on the Plex Poster
        print("Sending screenshot to the display")
        inky = auto(ask_user=True, verbose=True)
        saturation = 1
        image = Image.open(f"{installLocation}Poster.png")
        resizedRotatedImage = image.rotate(90, expand=1).resize(inky.resolution)
        inky.set_image(resizedRotatedImage, saturation=saturation)
        inky.show()
        sys.exit
    else:
        #Exits if nothing changes
        print('No Changes to Playing History. Exiting.')
        sys.exit
else:
    plexPosterURL = poster
    print("No recognised media type playing on Plex")
    if plexPosterURL != plex_history:
        print('Updating Playing History')
        config["Plex Play History"] = {
            "history": "plexPosterURL",
        }
        #Write the above sections to config.ini file
        with open(f"{installLocation}config.ini", 'w')  as conf:
            config.write(conf)

            # folder path for image showing when Plex is at rest
        dir_path = artFolder

        # list to store files
        directoryContents = []

        # Iterate directory
        for path in os.listdir(dir_path):
        # check if current path is a file
            if os.path.isfile(os.path.join(dir_path, path)):
                directoryContents.append(path)

            #Pick random image
        selectedImage=random.choice(directoryContents)
        print(selectedImage) #<- Prints what image was selected
        #Reconstructs image path
        #displayedImage=Image.open(f"{dir_path}\{selectedImage}").show()

        #displayedImage #<- Test
        #Display the at rest image on the Inky Screen
        inky = auto(ask_user=True, verbose=True)
        saturation = 1
        image = Image.open((f"{dir_path}{selectedImage}"))
        resizedRotatedImage = image.rotate(90, expand=1).resize(inky.resolution)

        inky.set_image(resizedRotatedImage, saturation=saturation)
        inky.show()
        sys.exit
    else:
        #Exits if nothing changes
        print('No Changes to Playing History. Exiting.')
        sys.exit