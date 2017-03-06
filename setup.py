"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

import py2app
from setuptools import setup

APP = ['telkom.py']
DATA_FILES =  [('icons', ['icons/app_128x128.icns',
                          'icons/telkom_24x24.png',
                          'icons/refresh_24x24.png']),
               ('conf', ['conf/telkom.conf',
                         'conf/logger.conf']),
               ('', ['README.md',
                     'LICENSE'])]
OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'LSUIElement': True,
    },
    'packages': ['rumps'], 
    'iconfile': 'icons/app_128x128.icns'
}

setup(
    app=APP,
    name='Telkom ADSL Data Usage',
    version='1.1.0',
    description='Status Item app to monitor Telkom ADSL data usage.',
    author='Pieter Rautenbach',
    url='http://www.whatsthatlight.com/',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
