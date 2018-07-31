#python3

import requests
import time
import json
import os
from pprint import pprint
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

#setup using instructions in README
my_admin = 'admin.user@domain.com'
service_account = 'myservice@projectname.iam.gserviceaccount.com'
json_file_name = 'myJSONkey.json'


#ReadExternalFile
def readFile(path):
    fileinfo = ""
    with open(path) as f:
        fileinfo = f.read()
    return fileinfo

#ServiceCredentials
def servicecreds(scope):
    SERVICE_ACCOUNT_EMAIL = service_account
    SERVICE_ACCOUNT_JSON_FILE_PATH = dir_path = os.path.dirname(os.path.realpath(__file__)) + "/" + json_file_name
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
    SERVICE_ACCOUNT_JSON_FILE_PATH, scopes=scope)
    mycreds = credentials.create_delegated(my_admin)
    return mycreds

#Gmail&GCal Requires the end-user to be impersonated
def impersonateservicecreds(enduser, scope):
    SERVICE_ACCOUNT_EMAIL = service_account
    SERVICE_ACCOUNT_JSON_FILE_PATH = dir_path = os.path.dirname(os.path.realpath(__file__)) + "/" + json_file_name
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
    SERVICE_ACCOUNT_JSON_FILE_PATH, scopes=scope)
    #impersonates end-user
    mycreds = credentials.create_delegated(enduser)
    return mycreds

#Users

def createUser(userEmail, orgUnit, firstname, lastname, department, password, changePasswordAtNextLogin=True):
    container = {}
    container['primaryEmail'] = userEmail
    container['orgUnitPath'] = "/" + orgUnit
    container['name'] = {"familyName": lastname, "givenName": firstname}
    container['organizations'] = [{'department': department}]
    container['changePasswordAtNextLogin'] = changePasswordAtNextLogin
    container['password'] = password
    userservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.user'))
    try:
        results = userservice.users().insert(body=container).execute()
        return results
    except:
        return "Error"

def suspensionUser(userEmail, suspended=True):
    container = {}
    container['suspended'] = suspended
    userservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.user'))
    try:
        results = userservice.users().patch(userKey = userEmail, body = container).execute()
        return results
    except:
        return "Error"

def getUser(userEmail, info):
    container = []
    userservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.user'))
    try:
        results = userservice.users().get(userKey=userEmail).execute()
        return results[info]
    except:
        return "Error"

def getUserAll(userEmail):
    container = []
    userservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.user'))
    try:
        results = userservice.users().get(userKey=userEmail, projection="full").execute()
        return results
    except:
        return "Error"

def getUser2FA(userEmail):
    container = []
    userservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.user'))
    try:
        results = userservice.users().get(userKey=userEmail).execute()
        return results['isEnrolledIn2Sv']
    except:
        return "Error"

def setPassword(userEmail, password):
    container = {}
    container['changePasswordAtNextLogin'] = False
    container['password'] = password
    userservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.user'))
    try:
        results = userservice.users().patch(userKey = userEmail, body = container).execute()
        return results
    except:
        return "Error"

def forcePasswordChangeNextLogin(userEmail):
    container = {}
    container['changePasswordAtNextLogin'] = True
    userservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.user'))
    try:
        results = userservice.users().patch(userKey = userEmail, body = container).execute()
        return results
    except:
        return "Error"

#email

def unshareProfileInGAL(userEmail):
    container = {}
    container['includeInGlobalAddressList'] = False
    userservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.user'))
    try:
        results = userservice.users().patch(userKey = userEmail, body = container).execute()
        return results
    except:
        return "Error"

def shareProfileInGAL(userEmail):
    container = {}
    container['includeInGlobalAddressList'] = True
    userservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.user'))
    try:
        results = userservice.users().patch(userKey = userEmail, body = container).execute()
        return results
    except:
        return "Error"

def getUserAlias(userEmail):
    container = []
    userservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.user'))
    try:
        results = userservice.users().aliases().list(userKey=userEmail ).execute()
        for item in results['aliases']:
            container.append(item['alias'])
        return container
    except:
        return "Error"

def setUserAlias(userEmail, aliasEmail):
    container = {'alias':aliasEmail}
    userservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.user'))
    try:
        results = userservice.users().aliases().insert(userKey = userEmail, body = container).execute()
        return results
    except:
        return "Error"

def getVacation(userEmail):
    container = {}
    emailservice = build('gmail', 'v1', credentials=impersonateservicecreds(userEmail,'https://www.googleapis.com/auth/gmail.modify'))
    #try:
    results = emailservice.users().settings().getVacation(userId=userEmail).execute()
    container['response'] = results.get('responseBodyHtml')
    container['subject'] = results.get('responseSubject')
    container['VacationOn'] = results.get('enableAutoReply')
    return container
    #except:
    #   return "Error"

def setVacation(userEmail, responseSubject, responseBodyHtml):
    container = {}
    container = {'responseSubject':responseSubject, 'responseBodyHtml':responseBodyHtml, 'enableAutoReply':True}
    emailservice = build('gmail', 'v1', credentials=impersonateservicecreds(userEmail,'https://www.googleapis.com/auth/gmail.settings.basic'))
    try:
        results = emailservice.users().settings().updateVacation(userId=userEmail, body=container).execute()
        return results
    except:
        return "Error"

def setVacationOff(userEmail):
    container = {}
    container = {'enableAutoReply':False}
    emailservice = build('gmail', 'v1', credentials=impersonateservicecreds(userEmail,'https://www.googleapis.com/auth/gmail.settings.basic'))
    try:
        results = emailservice.users().settings().updateVacation(userId=userEmail, body=container).execute()
        return results
    except:
        return "Error"

def setSignature(userEmail, signatureHTML):
    container = {}
    container = {'signature':signatureHTML}
    emailservice = build('gmail', 'v1', credentials=impersonateservicecreds(userEmail,'https://www.googleapis.com/auth/gmail.settings.basic'))
    try:
        results = emailservice.users().settings().sendAs().patch(userId=userEmail, sendAsEmail=userEmail, body=container).execute()
        return results
    except:
        return "Error"

def setSignatureFromFile(userEmail, signatureHTMLPath):
    signatureHTML = readFile(signatureHTMLPath)
    container = {'signature':signatureHTML}
    emailservice = build('gmail', 'v1', credentials=impersonateservicecreds(userEmail,'https://www.googleapis.com/auth/gmail.settings.basic'))
    try:
        results = emailservice.users().settings().sendAs().patch(userId=userEmail, sendAsEmail=userEmail, body=container).execute()
        return results
    except:
        return "Error"

def getGmailSignature(userEmail):
    container = {}
    emailservice = build('gmail', 'v1', credentials=impersonateservicecreds(userEmail,'https://www.googleapis.com/auth/gmail.settings.basic'))
    try:
        results = emailservice.users().settings().sendAs().get(userId=userEmail, sendAsEmail=userEmail).execute()
        container = results['signature']
        return container
    except:
        return "Error"

def addForwardingAddress(userEmail, forwardingEmail):
    container = {'forwardingEmail':forwardingEmail}
    emailservice = build('gmail', 'v1', credentials=impersonateservicecreds(userEmail,'https://www.googleapis.com/auth/gmail.settings.sharing'))
    #try:
    results = emailservice.users().settings().forwardingAddresses().create(userId=userEmail, body=container).execute()
    return results
    #except:
    #    return "Error"

def getAutoForwarding(userEmail):
    container = {}
    emailservice = build('gmail', 'v1', credentials=impersonateservicecreds(userEmail,'https://www.googleapis.com/auth/gmail.settings.basic'))
    try:
        results = emailservice.users().settings().getAutoForwarding(userId=userEmail).execute()
        container['enabled'] = results.get('enabled')
        container['forwardingEmail'] = results.get('emailAddress')
        return container
    except:
        return "Error"

#needs fixing to add the forwarding addres prior to turning on forwarding.
def setAutoForwarding(userEmail, forwardingEmail):
    addForwardingAddress(userEmail,forwardingEmail)
    container = {'enabled':True, 'emailAddress':forwardingEmail, 'disposition':'leaveInInbox'}
    emailservice = build('gmail', 'v1', credentials=impersonateservicecreds(userEmail,'https://www.googleapis.com/auth/gmail.settings.sharing'))
    #try:
    results = emailservice.users().settings().updateAutoForwarding(userId=userEmail, body=container).execute()
    return results
    #except:
    #    return "Error"

def removeAutoForwarding(userEmail):
    container = {'enabled':False}
    emailservice = build('gmail', 'v1', credentials=impersonateservicecreds(userEmail,'https://www.googleapis.com/auth/gmail.settings.sharing'))
    try:
        results = emailservice.users().settings().updateAutoForwarding(userId=userEmail, body=container).execute()
        return results
    except:
        return "Error"

#Authorized Keys

def listASPS(userEmail):
    ASPScodeIds = []
    aspsservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.user.security'))
    try:
        results = aspsservice.asps().list(userKey=userEmail).execute()
        for items in results['items']:
            ASPScodeIds.append(items['codeId'])
        return ASPScodeIds
    except:
        return "Error"

def deleteASPS(userEmail, codeID):
    container = []
    aspsservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.user.security'))
    try:
        results = aspsservice.asps().delete(userKey=userEmail, codeId=codeID).execute()
        return results
    except:
        return "Error"


#Members/Groups
def getMembers(GroupIDer, pageToken=None, maxResults=200):
    container = {}
    membercontainer = []
    memberservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.group'))
    request = memberservice.members().list(groupKey=GroupIDer, pageToken=pageToken, maxResults=200)
    try:
        while request is not None:
            results = request.execute()
            for item in results['members']:
                membercontainer.append(item['email'])
            request = memberservice.members().list_next(request,results)
        container['members'] = membercontainer
        return container
    except:
        return "Error"

def addToGroup(groupKey, userEmail):
    container = {}
    container['email'] = userEmail
    memberservice = groupservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.group'))
    try:
        results = memberservice.members().insert(groupKey=groupKey, body=container).execute()
        return results
    except:
        return "Error"

def removeFromGroup(groupKey, userEmail):
    memberservice = groupservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.group'))
    try:
        results = memberservice.members().delete(groupKey=groupKey, memberKey=userEmail).execute()
        return results
    except:
        return "Error"


def getUserGroups(userEmail):
    container = []
    groupservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.group'))
    try:
        results = groupservice.groups().list(userKey=userEmail).execute()
        for item in results['groups']:
            container.append(item['email'])
        return container
    except:
        return "No User/Groups"


#Devices
def getDevicesFromMDM(QueryID):
    container = []
    mdmservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.device.mobile'))
    try:
        results = mdmservice.mobiledevices().list(customerId='my_customer', query=QueryID,
                orderBy='email').execute()
        for item in results['mobiledevices']:
            container.append(item['email'])
        return container
    except:
        return "Error"

#Schemas
def getSchemaList():
    container = []
    schemaservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.userschema'))
    try:
        results = schemaservice.schemas().list(customerId='my_customer').execute()
        for item in results['schemas']:
            container.append(item['schemaName'])
        return container
    except:
        return "Error"


def getSchemaRoles(userEmail, schema):
    container = []
    userservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.user'))
    try:
        results = userservice.users().get(userKey=userEmail, projection="custom", customFieldMask=schema).execute()
        for item in results['customSchemas'][schema]['role']:
            container.append(item['value'])
        return container
    except:
        return []


def addSchemaRole(userEmail,schema,role):
    rolelist =[{'value':role}]
    oldroles = getSchemaRoles(userEmail, schema)
    for item in oldroles:
        rolelist.append({'value':item})
    container = {'customSchemas':{schema:{'role':rolelist}}}
    userservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.user'))
    try:
        results = userservice.users().patch(userKey = userEmail, body = container).execute()
        #return results
    except:
        return "Error"



#Calendars

def listEvents(userEmail):
    calservice = build('calendar', 'v3', credentials=impersonateservicecreds(userEmail,'https://www.googleapis.com/auth/calendar'))
    results = calservice.events().list(calendarId='primary').execute()
    pprint(results)


def listAllCalendars(userEmail):
    container = {}
    calservice = build('calendar', 'v3', credentials=impersonateservicecreds(userEmail,'https://www.googleapis.com/auth/calendar'))
    results = calservice.calendarList().list().execute()
    for item in results['items']:
        container[item['summary']] = item['id']
    pprint(container)

#Address Updates

def getAddress(userEmail):
    container = []
    userservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.user'))
    try:
        results = userservice.users().get(userKey=userEmail).execute()
        for item in results['addresses']:
            container.append(item['formatted'])
        return container
    except:
        return []


def addAddress(userEmail,address):
    addresslist = [address]
    oldaddress = getAddress(userEmail)
    addresssubmit = []
    for item in oldaddress:
        addresslist.append(item)
    for item in addresslist:
        addresssubmit.append({'formatted': item, 'type':'home'})
    container = {'addresses':addresssubmit}
    userservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.user'))
    try:
        results = userservice.users().patch(userKey = userEmail, body = container).execute()
        return results
    except:
        return "Error"

def addAddressByList(userEmail, addresslist):
    addresssubmit = []
    for item in addresslist:
        addresssubmit.append({'formatted': item, 'type':'home'})
    container = {'addresses':addresssubmit}
    pprint(container)
    userservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.user'))
    try:
        results = userservice.users().patch(userKey = userEmail, body = container).execute()
        return results
    except:
        return "Error"

#Google Drive
def listDriveFiles(userEmail):
    driveservice = build('drive', 'v3', credentials=impersonateservicecreds(userEmail,'https://www.googleapis.com/auth/drive.readonly'))
    files = driveservice.files().list().execute()
    print(files)

#Google Sheets
def getSheetValue(userEmail,sheet,key):
    sheetservice = build('sheets', 'v4', credentials=impersonateservicecreds(userEmail, 'https://www.googleapis.com/auth/spreadsheets.readonly'))
    sheetvalue = sheetservice.spreadsheets().values().get(spreadsheetId=sheet, range=key).execute()
    print(sheetvalue['values'])

  
