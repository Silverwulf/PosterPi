# PosterPi
Downloads the Movie or TV show poster of whatever is playing on a given Plex server and displays it on an Inky Impression E-Ink screen.

Once the repo has been claimed rename config-sample.ini as "config.ini". Your config file should be formatted as follows:

[Plex]
plexserverurl = http://192.168.168.1:32400 # <- Insert the IP address and port of your Plex Server. 
plextoken = yourplextoken

[Plex Play History]
history = 

[Plex Account]
account = YourUsername

[Art]
folderpath = /Your/Downloaded/Art/Folder/ #<- This is where you want to insert the folder path for where the script will randomly choose artwork to be displayed when the Plex server is not playing anything. 

