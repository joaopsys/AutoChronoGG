#!/usr/bin/env python3
__author__ = 'jota'

from io import BytesIO
import gzip
import urllib.request
import urllib.parse
import urllib.error
import sys
import os
import ctypes
import json
import smtplib
from email.message import EmailMessage

MAIN_URL = 'https://chrono.gg'
POST_URL = 'https://api.chrono.gg/quest/spin'
ALREADY_CLICKED_CODE = 420
UNAUTHORIZED = 401
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
GLOBAL_HEADERS = {'User-Agent': USER_AGENT, 'Pragma': 'no-cache', 'Origin': MAIN_URL, 'Accept-Encoding': 'gzip, deflate, br', 'Accept': 'application/json', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'Referer': MAIN_URL}
COOKIE_FILE_NAME = ".chronogg"
CONFIG_FILE_NAME = ".config"

def getWebPage(url, headers, cookies):
    try:
        print('Fetching '+url)
        request = urllib.request.Request(url, None, headers)
        request.add_header('Authorization', cookies)
        response = urllib.request.urlopen(request)
        if response.info().get('Content-Encoding') == 'gzip':
            buf = BytesIO(response.read())
            f = gzip.GzipFile(fileobj=buf)
            r = f.read()
        else:
            r = response.read()
        return r
    except urllib.error.HTTPError as e:
        print("Error processing webpage: "+str(e))
        if (e.code == ALREADY_CLICKED_CODE):
            return ALREADY_CLICKED_CODE
        if (e.code == UNAUTHORIZED):
            return UNAUTHORIZED
        return None

def saveCookie(cookie):
    ## https://stackoverflow.com/questions/25432139/python-cross-platform-hidden-file
    ## Just Windows things
    if os.name == 'nt':
        ret = ctypes.windll.kernel32.SetFileAttributesW(COOKIE_FILE_NAME, 0)

    with open(COOKIE_FILE_NAME, 'w') as f:
        f.write(cookie)

    if os.name == 'nt':
        ret = ctypes.windll.kernel32.SetFileAttributesW(COOKIE_FILE_NAME, 2)

def getCookieFromfile():
    try:
        with open(COOKIE_FILE_NAME, 'r') as f:
            return f.read()
    except:
        return ''

def getConfigFromFile():
    try:
        with open(CONFIG_FILE_NAME, 'r') as f:
            return json.load(f)
    except:
        return False

def send_mail(to_email, subject, message, config):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = config['email']['from']['name'] + ' <' + config['email']['from']['address'] + '>'
    msg['To'] = ', '.join(to_email)
    msg.set_content(message)
    server = smtplib.SMTP(config['email']['server'])
    server.send_message(msg)
    server.quit()

def main():
    try:
        config = getConfigFromFile()
        if not config:
            print('An error occurred while trying to load config the file.')
            print('Copy .config.example to .config')
            return
        if (len(sys.argv) < 2):
            ggCookie = getCookieFromfile()
            if (not ggCookie or len(ggCookie) < 1):
                print('<<<AutoChronoGG>>>')
                print('Usage: ./chronogg.py <Cookie>')
                print('Please insert your cookie. Press CTRL+SHIFT+J on the website (CTRL+SHIFT+K on Firefox) and type document.cookie. Then paste the whole string as an argument.')
                print('You only need need to do this once because AutoChronoGG will remember your cookie (if valid).')
                return
        else:
            ggCookie = sys.argv[1]

        results = getWebPage(POST_URL, GLOBAL_HEADERS, ggCookie)
        recipients = []
        if (not results):
            print('An error occurred while fetching results (probably expired/invalid cookie). Terminating...')
            return
        elif (results == ALREADY_CLICKED_CODE):
            print('An error occurred while fetching results: Coin already clicked. Terminating...')
            saveCookie(ggCookie)
            return
        elif (results == UNAUTHORIZED):
            print('An error occurred while fetching results: UNAUTHORIZED. Terminating...')
            for email in config['email']['to']:
                recipients.append(email['name'] + ' <' + email['address'] + '>')
            if config['email']['enabled']:
                send_mail(to_email=recipients, subject='AutoChronoGG: Invalid cookie', message='An error occurred while fetching results: UNAUTHORIZED. Terminating...', config=config)
            return
        print ('Done.')
        saveCookie(ggCookie)
    except KeyboardInterrupt:
        print("Interrupted.")

if __name__ == '__main__':
    main()
