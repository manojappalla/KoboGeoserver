import os
import requests
import xml.etree.ElementTree as ET
from qgis.core import *
from qgis.utils import *
import json
from PyQt5.QtCore import *
from auth import Auth

class Import:

    def __init__(self, kobo_url, kobo_username, kobo_password):
        self.kobo_url = kobo_url
        self.kobo_username = kobo_username
        self.kobo_password = kobo_password

    def getAuth(self):
        auth = requests.auth.HTTPDigestAuth(self.kobo_username,self.kobo_password)
        return auth

    def getValue(self,key, newValue = None):
        print("searching in setting parameter",key)
        for row in range (0,self.rowCount()):
            print(" parameter is",self.item(row,0).text())
            if self.item(row,0).text() == key:
                if newValue:
                    self.item(row, 1).setText(str(newValue))
                    print("setting new value",newValue)
                    self.setup() #store to settings
                value=self.item(row,1).text().strip()
                if value:
                    if key=='url':
                        if not value.endswith('/'):
                            value=value+'/'
                    return value

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

    def qtype(odktype):
        if odktype == 'binary':
            return QVariant.String, {'DocumentViewer': 2, 'DocumentViewerHeight': 0, 'DocumentViewerWidth': 0,
                                     'FileWidget': True, 'FileWidgetButton': True, 'FileWidgetFilter': '',
                                     'PropertyCollection': {'name': None, 'properties': {}, 'type': 'collection'},
                                     'RelativeStorage': 0, 'StorageMode': 0}
        elif odktype == 'string':
            return QVariant.String, {}
        elif odktype[:3] == 'sel':
            return QVariant.String, {}
        elif odktype[:3] == 'int':
            return QVariant.Int, {}
        elif odktype[:3] == 'dat':
            return QVariant.Date, {}
        elif odktype[:3] == 'ima':
            return QVariant.String, {'DocumentViewer': 2, 'DocumentViewerHeight': 0, 'DocumentViewerWidth': 0,
                                     'FileWidget': True, 'FileWidgetButton': True, 'FileWidgetFilter': '',
                                     'PropertyCollection': {'name': None, 'properties': {}, 'type': 'collection'},
                                     'RelativeStorage': 0, 'StorageMode': 0}
        elif odktype == 'Hidden':
            return 'Hidden'
        else:
            return (QVariant.String), {}

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
            url=turl+'api/v2/assets'
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













"""
*************************************************************************************************
                                TESTING
*************************************************************************************************
"""
url = input("Enter url: ")
username = input("Enter username: ")
password = input("Enter password: ")

data = Import(url, username, password)

try:
    print(data.getFormList())
except:
    print("Invalid credentials entered")