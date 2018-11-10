# AutoChronoGG
A Python script to automatically get the daily coins on Chrono.gg

**Requirements:**

Python 3 is required to run this script.

**Format:**

The format is pretty straightforward, the program only needs your Authorization Token in order to have access to your Chrono.gg session.

    Usage: ./chronogg.py "<Authorization Token (starts with JWT, first execution only)>"

In order to obtain your Authorization Token, you must follow these steps:
* Head to https://chrono.gg/ and login
* Right-click anywhere -> Inspect Element -> Go to the network tab -> Filter by XHR
* Keep the network tab open and refresh the page
* Some requests will appear, **click "account"** and copy the **Authorization** header under "Request Headers". It should start with "JWT", followed by a train of characters. **Make sure you copy all of it!**

**You only need to do this once because AutoChronoGG will remember your authorization token (if valid).**

**Optional: Additional features - E-mail on expired/invalid token**

* Copy `.config.example` to `.config`
* Enable by setting `email.enabled` to `true` in `.config`.

**Optional: Crontab**

This script is meant to be run once per day, so here goes a crontab example for the lazy:

    0 17 * * * root cd /usr/local/bin/ && ./chronogg.py
