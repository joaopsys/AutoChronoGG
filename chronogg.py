#!/usr/bin/env python3
import contextlib
import logging
import time

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


@contextlib.contextmanager
def setup_logging():
    logger = logging.getLogger()
    try:
        if os.environ["DEBUG"]:
            logger.setLevel(logging.DEBUG)
    except KeyError:
        logger.setLevel(logging.INFO)
    try:
        # __enter__

        log_filename = 'AutoChronoGG_{}.log'.format(time.strftime("%Y%m%d-%H%M%S"))
        f_handler = logging.FileHandler(filename=log_filename, encoding='utf-8', mode='w')
        s_handler = logging.StreamHandler(stream=sys.stdout)
        dt_fmt = '%Y-%m-%d %H:%M:%S'
        fmt = logging.Formatter(
            '%(asctime)s %(levelname)-5.5s [%(name)s] [%(funcName)s()] %(message)s <line %(lineno)d>',
            dt_fmt,
            style='%')
        for handler in [f_handler, s_handler]:
            handler.setFormatter(fmt)
            logger.addHandler(handler)

        yield
    finally:
        # __exit__
        handlers = logger.handlers[:]
        for hdlr in handlers:
            hdlr.close()
            logger.removeHandler(hdlr)


def get_web_page(url, headers, cookies):
    try:
        logging.info(f'Fetching {url}')
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
        logging.info(f"Error processing webpage: {e}")
        if e.code == ALREADY_CLICKED_CODE:
            return ALREADY_CLICKED_CODE
        if e.code == UNAUTHORIZED:
            return UNAUTHORIZED
        return None


def save_cookie(cookie):
    # https://stackoverflow.com/questions/25432139/python-cross-platform-hidden-file
    # Just Windows things
    if os.name == 'nt':
        ret = ctypes.windll.kernel32.SetFileAttributesW(COOKIE_FILE_NAME, 0)

    with open(COOKIE_FILE_NAME, 'w') as f:
        f.write(cookie)

    if os.name == 'nt':
        ret = ctypes.windll.kernel32.SetFileAttributesW(COOKIE_FILE_NAME, 2)


def get_cookie_from_file():
    try:
        with open(COOKIE_FILE_NAME, 'r') as f:
            return f.read()
    except:
        return ''


def get_config_from_file():
    try:
        with open(CONFIG_FILE_NAME, 'r') as f:
            return json.load(f)
    except:
        return False


def config_exists():
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
        config = get_config_from_file()
        if config_exists():
            if not config:
                logging.info(f'An error occurred while trying to load the config from file.'
                             f' Check the JSON syntax in {CONFIG_FILE_NAME}.')
                return
        if len(sys.argv) < 2:
            gg_cookie = get_cookie_from_file()
            if not gg_cookie or len(gg_cookie) < 1:
                logging.info('<<<AutoChronoGG>>>')
                logging.info('Usage: ./chronogg.py <Authorization Token>')
                logging.info('Please read the README.md and follow the instructions on '
                             'how to extract your authorization token.')
                return
        else:
            gg_cookie = sys.argv[1]

        results = get_web_page(POST_URL, GLOBAL_HEADERS, gg_cookie)
        if not results:
            logging.info('An unknown error occurred while fetching results. Terminating...')
            return
        elif results == ALREADY_CLICKED_CODE:
            logging.info('An error occurred while fetching results: Coin already clicked. Terminating...')
            save_cookie(gg_cookie)
            return
        elif results == UNAUTHORIZED:
            logging.info('An error occurred while fetching results: Expired/invalid authorization token.'
                         ' Terminating...')
            if config and config['email']['enabled']:
                recipients = []
                for email in config['email']['to']:
                    recipients.append(email['name'] + ' <' + email['address'] + '>')
                frm = {
                    'name': config['email']['from']['name'],
                    'address': config['email']['from']['address']
                }
                try:
                    send_mail(to=recipients, subject='AutoChronoGG: Invalid token',
                              message='An error occurred while fetching results: Expired/invalid authorization token.'
                                      ' Terminating...',
                              frm=frm, host=config['email']['server'])
                except:
                    logging.info('An error occurred while sending an e-mail alert.'
                                 ' Please check your configuration file or your mail server.')
            return
        logging.info('Done.')
        save_cookie(gg_cookie)
    except KeyboardInterrupt:
        logging.info("Interrupted.")


if __name__ == '__main__':
    with setup_logging():
        main()
