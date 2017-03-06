# Imports
import ConfigParser
import json
import logging.config
import os
import re
import requests
import rumps
import warnings
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Main constants
APP_NAME = 'Telkom'
# example data:
# {value: 76, label: 'Remaining integrated data', formatted: '30.5 GB' + ' (' +76 + '%)'},
# {value: 23, label: 'Fixed data usage', formatted: '9.5 GB' + ' (' +23 + '%)'},
REGEX = 'value:.*?(\d+).*?label:.*?\'(.*?)\'.*?formatted:.*?\'(.*?)\''
REGEX = REGEX + '.*?' + REGEX
REFRESH_MENU = 'Refresh'
REFRESH_INTERVAL = 10*60
REMAINDER_KEY = 'remainder'
USAGE_KEY = 'usage'
USAGE_SUBSTRING = 'usage'
TOGGLE_MENU = 'Toggle'
TOGGLE_TEMPLATE = 'Show {}'
UPDATING_MESSAGE = 'Updating...'
ERROR_MESSAGE = 'Error'
CONF_DEFAULT_SECTION = 'default'
CONF_USERNAME = 'username'
CONF_PASSWORD = 'password'
CONF_TOGGLE = 'toggle'

# Path constants
CONF_TEMPLATE_PATH = '{0}/conf/{1}'
APP_CONF = 'telkom.conf'
LOGGER_CONF = 'logger.conf'
ICONS_TEMPLATE_PATH = '{0}/icons/{1}'
APP_ICON = 'telkom_24x24.png'
REFRESH_ICON = 'refresh_24x24.png'

# Telkom constants
LOGIN_URL = 'https://secure.telkomsa.net/titracker/servlet/LoginServlet'
HTTP_HEADERS = {'User-Agent': 'Mozilla/5.0'}
USERNAME_HTML_ID = 'ID_Field'
PASSWORD_HTML_ID = 'PW_field'

def get_page(username, password):
    """
    Get a web page as plain text HTML. 

    :return: HTML data
    """
    login_payload = {USERNAME_HTML_ID: username, PASSWORD_HTML_ID: password}
    session = requests.Session()
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=InsecureRequestWarning)
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

def parse_info(script):
    """
    Parse the remaining data from the given script tag.

    :return: Dictionary with usage and remainder containing tuples of (label, data_string, data_percentage_string)
    """
    match = re.search(REGEX, script, flags=re.MULTILINE|re.DOTALL)
    # we don't know which group is the usage and which the remainder
    if USAGE_SUBSTRING in match.groups()[4]:
        usage = match.groups()[3:6]
        remainder = match.groups()[0:3]
        usage = match.groups()[3:6]
    else:
        usage = match.groups()[0:3]
        remainder = match.groups()[3:6]
    info = {
        REMAINDER_KEY: (remainder[1], remainder[2], remainder[0]),
        USAGE_KEY: (usage[1], usage[2], usage[0])
    }
    return info

def reload_info():
    """
    Reload usage info.
    """
    global app, logger, username, password, toggle
    try:
        old_title = app.title
        app.title = UPDATING_MESSAGE
        html = get_page(username, password)
        data = extract_data(html)
        info = parse_info(data)
        logger.info(info[REMAINDER_KEY][0] + ': ' +  info[REMAINDER_KEY][1] + ' (' + info[REMAINDER_KEY][2] + '%)')
        logger.info(info[USAGE_KEY][0] + ': ' +  info[USAGE_KEY][1] + ' (' + info[USAGE_KEY][2] + '%)')
        app.title = '{0} ({1}%)'.format(info[toggle][1], info[toggle][2])
    except Exception, e:
        logger.exception(e)
        app.title = ERROR_MESSAGE

def toggle():
    """
    Toggle between usage and remainder.
    """
    global app, toggle, logger
    logger.info(app.menu[TOGGLE_MENU])
    logger.info(toggle)
    app.menu[TOGGLE_MENU].title = TOGGLE_TEMPLATE.format('foo')

#@rumps.clicked(REFRESH_MENU)
def refresh_callback(_):
    """
    Refresh menu item's click action.
    """
    global logger
    logger.info(REFRESH_MENU)
    reload_info()

#@rumps.clicked(TOGGLE_MENU)
def toggle_callback(_):
    """
    Toggle menu item's click action.
    """
    global logger
    logger.info(TOGGLE_MENU)
    toggle()

@rumps.timer(REFRESH_INTERVAL)
def reload_info_callback(sender):
    """
    Timer callback for reloading usage info.
    """
    refresh_callback(None)

def get_logger(conf_path):
    """
    Initialise the logger from a config file.

    :return: Logger instance
    """
    logging.config.fileConfig(conf_path)
    logger = logging.getLogger()
    return logger

def main():
    """
    Main application.
    """
    global app, app_path, username, password, toggle, info
    logger.info('Reading config')
    config_parser = ConfigParser.SafeConfigParser()
    with open(CONF_TEMPLATE_PATH.format(app_path, APP_CONF)) as config_file:
        config_parser.readfp(config_file)
        username = config_parser.get(CONF_DEFAULT_SECTION, CONF_USERNAME)
        password = config_parser.get(CONF_DEFAULT_SECTION, CONF_PASSWORD)
        toggle = config_parser.get(CONF_DEFAULT_SECTION, CONF_TOGGLE)
    logger.info('Username: ' + username)
    logger.info('Toggle: ' + toggle)
    refresh_menu = rumps.MenuItem(REFRESH_MENU, 
                                  callback=refresh_callback,
                                  icon=ICONS_TEMPLATE_PATH.format(app_path, REFRESH_ICON), 
                                  dimensions=(16, 16))
    toggle_menu = rumps.MenuItem(TOGGLE_MENU, 
                                 callback=toggle_callback)
    app = rumps.App(APP_NAME,
                    icon=ICONS_TEMPLATE_PATH.format(app_path, APP_ICON),
                    menu=(refresh_menu, toggle_menu, None))
    logger.info('Running')
    app.title = APP_NAME
    # app.menu = [
    #     rumps.MenuItem(REFRESH_MENU, callback=refresh_callback),
    #     rumps.MenuItem(TOGGLE_MENU, callback=toggle_callback)
    # ]
    app.run()

if __name__ == "__main__":
    """
    Bootstrap.
    """
    app_path = os.path.dirname(os.path.abspath(__file__))
    logger_conf = CONF_TEMPLATE_PATH.format(app_path, LOGGER_CONF)
    logger = get_logger(logger_conf)
    info = {}
    username = None
    password = None
    try:
        main()
    except Exception, e:
        logger.exception(e)
