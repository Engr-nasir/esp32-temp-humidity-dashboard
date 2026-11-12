# Copy this file to config.py and change the values.
# config.py is listed in .gitignore, so it will NOT be uploaded to GitHub.

USERNAME = "admin"                               # dashboard login name
PASSWORD = "change-me"                           # dashboard password
DEVICE_KEY = "change-this-device-key"            # must match DEVICE_KEY in secrets.h
SECRET_KEY = "change-this-to-a-long-random-text" # used by Flask to sign login sessions
CSV_FILE = "readings.csv"                        # every reading is saved here
