import os
import requests
from qgis.core import *
from qgis.utils import *
import json
from PyQt5.QtCore import QSettings
# import auth

class Import:

    def __init__(self, kobo_url, kobo_username, kobo_password):
        self.kobo_url = kobo_url
        self.kobo_username = kobo_username
        self.kobo_password = kobo_password


    def getproxiesConf(self):

        """
        This function is used to configure all the proxy settings.
        :return:
        """
        s = QSettings()  # getting proxy from qgis options settings
        proxyEnabled = s.value("proxy/proxyEnabled", "")
        proxyType = s.value("proxy/proxyType", "")
        proxyHost = s.value("proxy/proxyHost", "")
        proxyPort = s.value("proxy/proxyPort", "")
        proxyUser = s.value("proxy/proxyUser", "")
        proxyPassword = s.value("proxy/proxyPassword", "")
        if proxyEnabled == "true" and proxyType == 'HttpProxy':  # test if there are proxy settings
            proxyDict = {
                "http": "http://%s:%s@%s:%s" % (proxyUser, proxyPassword, proxyHost, proxyPort),
                "https": "http://%s:%s@%s:%s" % (proxyUser, proxyPassword, proxyHost, proxyPort)
            }
            return proxyDict
        else:
            return None


    def getFormList(self):

        """
        This function will return the dictionary of all the forms present in the kobotoolbox
        :return:
        """

        user = self.kobo_username
        password = self.kobo_password
        turl = self.kobo_url
        proxies = self.getproxiesConf()

        if turl:
            url=turl+'/assets'
        else:
            print("Enter correct url.")
            return None, None

        para={'format':'json'}
        keyDict={}
        questions = []

        try:
            response = requests.get(url, proxies=proxies, auth=(user, password), params=para)
            forms = response.json()
            for form in forms['results']:
                if form['asset_type'] == 'survey' and form['deployment__active'] == True:
                    keyDict[form['name']] = form['uid']
            return keyDict, response
        except:
            # self.iface.messageBar().pushCritical(self.tag, self.tr("Invalid url username or password"))
            print("Invalid username or password")
            return None, None


url = input("Enter url: ")
username = input("Enter username: ")
password = input("Enter password: ")

data = Import(url, username, password)

try:
    print(data.getFormList())
except:
    print("Invalid credentials entered")