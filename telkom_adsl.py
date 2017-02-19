# Imports
import json
import re
import requests
from bs4 import BeautifulSoup

# Constants
LOGIN_URL = "https://secure.telkomsa.net/titracker/servlet/LoginServlet"
HTTP_HEADERS = {'User-Agent': 'Mozilla/5.0'}
USERNAME_HTML_ID = 'ID_Field'
PASSWORD_HTML_ID = 'PW_field'
# example data:
# {value: 76, label: 'Remaining integrated data', formatted: '30.5 GB' + ' (' +76 + '%)'},
# {value: 23, label: 'Fixed data usage', formatted: '9.5 GB' + ' (' +23 + '%)'},
REGEX = 'value:.*?(\d+).*?label:.*?\'(.*?)\'.*?formatted:.*?\'(.*?)\''
REGEX = REGEX + '.*?' + REGEX
USAGE_SUBSTRING = 'usage'

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
    """
    match = re.search(REGEX, data.text, flags=re.MULTILINE|re.DOTALL)
    # we don't know which group is the usage and which the remainder
    if USAGE_SUBSTRING in match.groups()[4]:
        usage = match.groups()[3:6]
        remainder = match.groups()[0:3]
    else:
        usage = match.groups()[0:3]
        remainder = match.groups()[3:6]
    return remainder

def main():
    """
    Main application.
    """
    #global logger, app, info
    username = 'rautenbach2015@telkomsa.net'
    password = 'Rvewzs@9'
    html = get_page(username, password)
    data = extract_data(html)
    remainder = parse_remainder(data)
    print(remainder[1] + ': ' +  remainder[2] + ' (' + remainder[0] + '%)')

if __name__ == "__main__":
    """
    Bootstrap.
    """
    #p = os.path.dirname(os.path.abspath(__file__))
    #l = "{0}/conf/logger.conf".format(p)
    #logger = get_logger(l)
    #info = {}
    #try:
    main()
    #except Exception, e:
    #    pass
    #    #logger.exception(e)
