# Imports
import json
import logging.config
import os
import re
import requests
import rumps
from bs4 import BeautifulSoup

# Constants
LOGIN_URL = 'https://secure.telkomsa.net/titracker/servlet/LoginServlet'
HTTP_HEADERS = {'User-Agent': 'Mozilla/5.0'}
USERNAME_HTML_ID = 'ID_Field'
PASSWORD_HTML_ID = 'PW_field'
# example data:
# {value: 76, label: 'Remaining integrated data', formatted: '30.5 GB' + ' (' +76 + '%)'},
# {value: 23, label: 'Fixed data usage', formatted: '9.5 GB' + ' (' +23 + '%)'},
REGEX = 'value:.*?(\d+).*?label:.*?\'(.*?)\'.*?formatted:.*?\'(.*?)\''
REGEX = REGEX + '.*?' + REGEX
USAGE_SUBSTRING = 'usage'
REFRESH_MENU = 'Refresh'
APP_NAME = 'Telkom'
REMAINDER_KEY = 'remainder'
UPDATING_MESSAGE = 'Updating...'
ERROR_MESSAGE = 'Error'

def get_page(username, password):
    """
    Get a web page as plain text HTML. 

    :return: HTML data
    """
    login_payload = {USERNAME_HTML_ID: username, PASSWORD_HTML_ID: password}
    session = requests.Session()
    response = session.post(LOGIN_URL, headers=HTTP_HEADERS, data=login_payload, verify=False)
    return response.text

def extract_data(html):
    """
    Extract the script that contains the usage data.

    :return: The script element as a string
    """
    soup = BeautifulSoup(html, 'html.parser')
    scripts = []
    for script in soup.findAll('script'):
        scripts.append(script)
    return scripts[7].text

def parse_remainder(script):
    """
    Parse the remaining data from the given script tag.

    :return: Tuple of (remain_label, data_string, data_percentage_string)
    """
    match = re.search(REGEX, script, flags=re.MULTILINE|re.DOTALL)
    # we don't know which group is the usage and which the remainder
    if USAGE_SUBSTRING in match.groups()[4]:
        usage = match.groups()[3:6]
        remainder = match.groups()[0:3]
    else:
        usage = match.groups()[0:3]
        remainder = match.groups()[3:6]
    return (remainder[1], remainder[2], remainder[0])

def reload_info():
    """
    """
    global app, logger
    try:
        old_title = app.title
        app.title = UPDATING_MESSAGE

        username = 'foo'
        password = 'bar'
        html = get_page(username, password)
        data = extract_data(html)
        remainder = parse_remainder(data)
        info = {
            REMAINDER_KEY: remainder
        }
        logger.info(remainder[0] + ': ' +  remainder[1] + ' (' + remainder[2] + '%)')
        app.title = '{0} ({1}%)'.format(info[REMAINDER_KEY][1], info[REMAINDER_KEY][2])
    except Exception, e:
        logger.exception(e)
        app.title = ERROR_MESSAGE

@rumps.clicked(REFRESH_MENU)
def refresh_callback(_):
    """
    Refresh menu item's click action.
    """
    global logger
    logger.info(REFRESH_MENU)
    reload_info()

@rumps.timer(1*60)
def reload_info_callback(sender):
    """
    Timer callback for reloading usage info.
    """
    refresh_callback(None)

def get_logger(conf_path):
    """
    Initialise the logger from a config file.
    """
    logging.config.fileConfig(conf_path)
    logger = logging.getLogger()
    return logger

def main():
    """
    Main application.
    """
    global app, app_path, info
    refresh = rumps.MenuItem(REFRESH_MENU, 
                             icon='{0}/icons/refresh_24x24.png'.format(app_path), 
                             dimensions=(16, 16))
    app = rumps.App(APP_NAME,
                    icon='{0}/icons/telkom_24x24.png'.format(app_path),
                    menu=(refresh, None))
    app.run()

if __name__ == "__main__":
    """
    Bootstrap.
    """
    app_path = os.path.dirname(os.path.abspath(__file__))
    logger_conf = '{0}/conf/logger.conf'.format(app_path)
    logger = get_logger(logger_conf)
    info = {}
    try:
        main()
    except Exception, e:
        logger.exception(e)
