import os
import requests
import xml.etree.ElementTree as ET
from qgis.core import *
from qgis.utils import *
import json
from PyQt5.QtCore import *
from Auth import Auth


def qtype(odktype):
    if odktype == 'binary':
        return QVariant.String,{'DocumentViewer': 2, 'DocumentViewerHeight': 0, 'DocumentViewerWidth': 0, 'FileWidget': True, 'FileWidgetButton': True, 'FileWidgetFilter': '', 'PropertyCollection': {'name': None, 'properties': {}, 'type': 'collection'}, 'RelativeStorage': 0, 'StorageMode': 0}
    elif odktype=='string':
        return QVariant.String,{}
    elif odktype[:3] == 'sel' :
        return QVariant.String,{}
    elif odktype[:3] == 'int':
        return QVariant.Int, {}
    elif odktype[:3]=='dat':
        return QVariant.Date, {}
    elif odktype[:3]=='ima':
        return QVariant.String,{'DocumentViewer': 2, 'DocumentViewerHeight': 0, 'DocumentViewerWidth': 0, 'FileWidget': True, 'FileWidgetButton': True, 'FileWidgetFilter': '', 'PropertyCollection': {'name': None, 'properties': {}, 'type': 'collection'}, 'RelativeStorage': 0, 'StorageMode': 0}
    elif odktype == 'Hidden':
        return 'Hidden'
    else:
        return (QVariant.String),{}

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

    def getFormList(self):

        """
        This function will return the dictionary of all the forms present in the kobotoolbox in json format

        :return:
        dictionary containing name of the form as key and id as value
        Example: ({'test': 'aDHQqdStRmoRUwSZJb5P35', 'iirs_buildings': 'aumGeYCKpLmoK6jkcDgcUv'}, <Response [200]>)
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

    def importData(self,layer,selectedForm,doImportData=True):
        """
        This function accesses the XML response received from the get request using the following url
                        url = turl + '/assets/' + selectedForm
        The XML response returned is passed to the updateLayerXML() function.

        :param layer:
        :param selectedForm:
        :param doImportData:
        :return:
        No return value
        """

        #from kobo branchQH
        user=self.kobo_username
        password=self.kobo_password
        turl=self.kobo_url
        if turl:
            url=turl+'/assets/'+selectedForm
        else:
            print("URL is not entered.")
        para={'format':'xml'}
        requests.packages.urllib3.disable_warnings()
        try:
            response= requests.request('GET',url,proxies=self.getproxiesConf(),auth=(user,password),verify=False,params=para)
        except:
            print("Invalid url,username or password")
            return
        if response.status_code==200:
            xml=response.content

            self.layer_name,self.version, self.geoField,self.fields= self.updateLayerXML(layer,xml)
            layer.setName(self.layer_name)
            self.user=user
            self.password=password
            print("calling collect data")
            # self.collectData(layer,selectedForm,doImportData,self.layer_name,self.version,self.geoField)
        else:
            print("not able to connect to server")


    def updateLayerXML(self,layer,xml):
        geoField=''
        ns='{http://www.w3.org/2002/xforms}'
        nsh='{http://www.w3.org/1999/xhtml}'
        root= ET.fromstring(xml)
        #key= root[0][1][0][0].attrib['id']
        layer_name=root[0].find(nsh+'title').text
        instance=root[0][1].find(ns+'instance')
        fields={}
        #topElement=root[0][1][0][0].tag.split('}')[1]
        try:
            version=instance[0].attrib['version']
        except:
            version='null'
#        print('form name is '+ layer_name)
#        print (root[0][1].findall(ns+'bind'))
        for bind in root[0][1].findall(ns+'bind'):
            attrib=bind.attrib
            fieldName= attrib['nodeset'].split('/')[-1]
            try:
                fieldType=attrib['type']
            except:
                continue
            fields[fieldName]=fieldType
            # print('attrib type is',attrib['type'])
            qgstype,config = qtype(attrib['type'])
#            print ('first attribute'+ fieldName)
            inputs=root[1].findall('.//*[@ref]')
            if fieldType[:3]!='geo':
                #print('creating new field:'+ fieldName)
                isHidden= True
                if fieldName=='instanceID':
                    fieldName='ODKUUID'
                    fields[fieldName]=fieldType
                    isHidden= False
                for input in inputs:
                    if fieldName == input.attrib['ref'].split('/')[-1]:
                        isHidden= False
                        break
                if isHidden:
                    print('Reached Hidden')
                    config['type']='Hidden'
            else:
                geoField=fieldName
                # print('geometry field is =',fieldName)
                continue
            self.updateFields(layer,fieldName,qgstype,config)
        return layer_name,version,geoField,fields

    def updateFields(self, layer, text='ODKUUID', q_type=QVariant.String, config={}):
        flag = True
        for field in layer.fields():

            if field.name()[:10] == text[:10]:
                flag = False
                print("not writing fields")
        if flag:
            uuidField = QgsField(text, q_type)
            if q_type == QVariant.String:
                uuidField.setLength(300)
            layer.dataProvider().addAttributes([uuidField])
            layer.updateFields()
        fId = layer.dataProvider().fieldNameIndex(text)
        try:
            if config['type'] == 'Hidden':
                print('setting hidden widget')
                layer.setEditorWidgetSetup(fId, QgsEditorWidgetSetup("Hidden", config))
                return
        except Exception as e:
            # print(e)
            pass
        if config == {}:
            return
        print('now setting external resource widget')
        layer.setEditorWidgetSetup(fId, QgsEditorWidgetSetup("ExternalResource", config))
        print("done")







QgsApplication.setPrefixPath("/Applications/QGIS-LTR.app/Contents/Resources", True)
qgs = QgsApplication([], False)
qgs.initQgis()
url = input("Enter url: ")
username = input("Enter username: ")
password = input("Enter password: ")

"""
*************************************************************************************************
                                TESTING getFormList
*************************************************************************************************
"""
data = Import(url, username, password)

try:
    print(data.getFormList())
except:
    print("Invalid credentials entered")


"""
*************************************************************************************************
                                TESTING importData, updateLayerXML, updateFields
*************************************************************************************************
"""

# TODO: Create one empty shapefile and pass it as an argument to the importData function

layer = QgsVectorLayer("/Users/saimanojappalla/Desktop/PilotProject/KoboGeoserver/kobogeoserver-standalone/shapefile/new.shp", "testlayer_shp", "ogr")
selected_form = input("Please enter selected form: ")
data.importData(layer, selected_form)

