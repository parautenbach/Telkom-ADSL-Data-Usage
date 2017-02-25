# Imports
import json
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

def get_page(username, password):
    """
    """
    login_payload = {USERNAME_HTML_ID: username, PASSWORD_HTML_ID: password}
    session = requests.Session()
    response = session.post(LOGIN_URL, headers=HTTP_HEADERS, data=login_payload, verify=False)
    return response.text

def extract_data(html):
    """
    """
    soup = BeautifulSoup(html, 'html.parser')
    scripts = []
    for script in soup.findAll('script'):
        scripts.append(script)
    return scripts[7]

def parse_remainder(data):
    """

    :return: Tuple of (remain_label, data_string, data_percentage_string)
    """
    match = re.search(REGEX, data.text, flags=re.MULTILINE|re.DOTALL)
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
    global app
    old_title = app.title
    app.title = 'Updating...'

    username = 'foo'
    password = 'bar'
    html = get_page(username, password)
    data = extract_data(html)
    remainder = parse_remainder(data)
    info = {
        REMAINDER_KEY: remainder
    }
    print(remainder[0] + ': ' +  remainder[1] + ' (' + remainder[2] + '%)')
    app.title = '{0} ({1}%)'.format(info[REMAINDER_KEY][1], info[REMAINDER_KEY][2])

@rumps.clicked(REFRESH_MENU)
def refresh_callback(_):
    print(REFRESH_MENU)
    #global info
    try:
    #    last_update = info['last_update']
    #    info['last_update'] = None
        reload_info()
    except Exception, e:
        print(e)
    #    info['last_update'] = last_update

@rumps.timer(1*60)
def reload_info_callback(sender):
    """
    Timer callback for reloading all info.
    """
    # We don't use any locking, as we assume that the interval between runs will be less
    # than the time to retrieve the data
    #thread = threading.Thread(target=reload_info)
    #thread.daemon = True
    #thread.start()
    refresh_callback(None)

def main():
    """
    Main application.
    """
    #global logger, app, info
    global app, info
    #timer = rumps.Timer(reload_info_callback, 5)
    #summary = rumps.MenuItem('Summary')#, 
                             #icon='{0}/icons/summary_24x24.png'.format(p), 
                             #dimensions=(16, 16))
    refresh = rumps.MenuItem(REFRESH_MENU)#, 
                             #icon='{0}/icons/refresh_24x24.png'.format(p), 
                             #dimensions=(16, 16))
    app = rumps.App(APP_NAME,
                    #icon='{0}/icons/app_24x24.png'.format(p),
                    menu=(refresh, None))
    app.run()

if __name__ == "__main__":
    """
    Bootstrap.
    """
    #p = os.path.dirname(os.path.abspath(__file__))
    #l = "{0}/conf/logger.conf".format(p)
    #logger = get_logger(l)
    info = {}
    #try:
    main()
    #except Exception, e:
    #    pass
    #    #logger.exception(e)
