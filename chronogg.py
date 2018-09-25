#!/usr/bin/env python3
__author__ = 'jota'

import ctypes
import gzip
import json
import os
import smtplib
import sys
import urllib.error
import urllib.parse
import urllib.request
from email.message import EmailMessage
from io import BytesIO

MAIN_URL = 'https://chrono.gg'
POST_URL = 'https://api.chrono.gg/quest/spin'
ALREADY_CLICKED_CODE = 420
UNAUTHORIZED = 401
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
GLOBAL_HEADERS = {'User-Agent': USER_AGENT, 'Pragma': 'no-cache', 'Origin': MAIN_URL,
                  'Accept-Encoding': 'gzip, deflate, br', 'Accept': 'application/json', 'Cache-Control': 'no-cache',
                  'Connection': 'keep-alive', 'Referer': MAIN_URL}
COOKIE_FILE_NAME = ".chronogg"
CONFIG_FILE_NAME = ".config"

try:
    from local_vars import proxy_password, proxy_login, proxyurl
    if proxy_login and proxy_password and proxyurl:
        proxy = 'http://{}:{}@{}'.format(proxy_login, proxy_password, proxyurl)
    elif proxy_login and proxyurl:
        proxy = 'http://{}@{}'.format(proxy_login, proxyurl)
    else:
        proxy = 'http://{}'.format(proxyurl)
    os.environ['HTTP_PROXY'] = proxy
    os.environ['HTTPS_PROXY'] = proxy
except ImportError:
    os.environ['HTTP_PROXY'] = ''
    os.environ['HTTPS_PROXY'] = ''

def getWebPage(url, headers, cookies):
    try:
        print('Fetching ' + url)
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
        print("Error processing webpage: " + str(e))
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


def configExists():
    return os.path.exists(CONFIG_FILE_NAME)


def send_mail(to, subject, message, frm, host):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = frm['name'] + ' <' + frm['address'] + '>'
    msg['To'] = ', '.join(to)
    msg.set_content(message)
    server = smtplib.SMTP(host)
    server.send_message(msg)
    server.quit()


def main():
    try:
        config = getConfigFromFile()
        if configExists():
            if not config:
                print(
                    'An error occurred while trying to load the config from file. Check the JSON syntax in ' + CONFIG_FILE_NAME)
                return
        if (len(sys.argv) < 2):
            ggCookie = getCookieFromfile()
            if (not ggCookie or len(ggCookie) < 1):
                print('<<<AutoChronoGG>>>')
                print('Usage: ./chronogg.py <Authorization Token>')
                print(
                    'Please read the README.md and follow the instructions on how to extract your authorization token.')
                return
        else:
            ggCookie = sys.argv[1]

        results = getWebPage(POST_URL, GLOBAL_HEADERS, ggCookie)
        if (not results):
            print('An unknown error occurred while fetching results. Terminating...')
            return
        elif (results == ALREADY_CLICKED_CODE):
            print('An error occurred while fetching results: Coin already clicked. Terminating...')
            saveCookie(ggCookie)
            return
        elif (results == UNAUTHORIZED):
            print('An error occurred while fetching results: Expired/invalid authorization token. Terminating...')
            if config and config['email']['enabled']:
                recipients = []
                for email in config['email']['to']:
                    recipients.append(email['name'] + ' <' + email['address'] + '>')
                frm = {}
                frm['name'] = config['email']['from']['name']
                frm['address'] = config['email']['from']['address']
                try:
                    send_mail(to=recipients, subject='AutoChronoGG: Invalid token',
                              message='An error occurred while fetching results: Expired/invalid authorization token. Terminating...',
                              frm=frm, host=config['email']['server'])
                except:
                    print(
                        'An error occurred while sending an e-mail alert. Please check your configuration file or your mail server.')
            return
        print('Done.')
        saveCookie(ggCookie)
    except KeyboardInterrupt:
        print("Interrupted.")


if __name__ == '__main__':
    main()
