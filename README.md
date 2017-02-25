# Telkom-ADSL-Data-Usage
Tiny macOS tray app for indicating Telkom ADSL data usage.

# Dependencies
* Python 2.7 or newer
* [Xcode Command-Line Tools](https://developer.apple.com/xcode/)
* [rumps: Ridiculously Uncomplicated Mac OS X Python Statusbar apps](https://github.com/jaredks/rumps)
* [requests](http://docs.python-requests.org/en/master/)

# Installation
* Download the latest version
* Copy it to your Applications folder
* Edit the application config in the app bundle;
** `~/Applications/Telkom ADSL Usage.app/Contents/Resources/conf/telkom.conf`
* Run the app
* Right click on it in the doc and select the setting to start it at login

# Troubleshooting
Check the log in the app bundle.

# Development
* Install py2app
* Run `./make.sh`

# Credits
Thank you to [dryicons](http://dryicons.com/) for the [Coquette Icon Set](http://dryicons.com/free-icons/preview/coquette-icons-set/). 
