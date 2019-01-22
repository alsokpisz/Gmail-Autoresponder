# Gmail-Autoresponder
Created over the Fall 2018 semester for a small storage facility company in Round Rock. 
Their software suite was frustrating them because they could not send a personalized email to tenants with their facility management software. 
I created a command-line solution which used Python and the GMail API to parse important details from the facility software registration receipt 
and create a personalized email to the new tenant. 
Windows Task Scheduler ran this program every minute.

To run this program, you would need to:
Install the latest version of python and pip
https://developers.google.com/gmail/api/quickstart/python
* Download Client Config.json file
* Download the Google oauth2 with pip
* Set up the sample code locally
* Run the sample code  locally
Remember to delete token.js whenever recreating anything
Go to GCP and doublecheck credential settings.
pip install beautifulsoup4
pip install python-dateutil
pip install lxml
And create a file called 'privatefunc.py' which handles client sensitive information.
