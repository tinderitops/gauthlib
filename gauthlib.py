#python3

import requests
import time
import json
import os
import pandas
from pprint import pprint
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.errors import HttpError

#setup using instructions in README
my_admin = 'admin.user@domain.com'
service_account = 'myservice@projectname.iam.gserviceaccount.com'
json_file_name = 'myJSONkey.json'
SERVICE_ACCOUNT_JSON_FILE_PATH = dir_path = os.path.dirname(os.path.realpath(__file__)) + "/" + json_file_name


#ReadExternalFile
def readFile(path):
    fileinfo = ""
    with open(path) as f:
        fileinfo = f.read()
    return fileinfo

#ServiceCredentials
def servicecreds(scope):
    SERVICE_ACCOUNT_EMAIL = service_account
    credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_JSON_FILE_PATH, scopes=scope)
    #possible to use from json dict instead using:
    #credentials = ServiceAccountCredentials.from_json_keyfile_dict(authorization, scopes=scope)
    mycreds = credentials.create_delegated(my_admin)
    return mycreds

#Gmail&GCal Requires the end-user to be impersonated
def impersonateservicecreds(enduser, scope):
    SERVICE_ACCOUNT_EMAIL = service_account
    credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_JSON_FILE_PATH, scopes=scope)
    #possible to use from json dict instead using:
    #credentials = ServiceAccountCredentials.from_json_keyfile_dict(authorization, scopes=scope)
    #impersonates end-user
    mycreds = credentials.create_delegated(enduser)
    return mycreds

#Users

def doesUserExist(user):
    userexistcontainer = False
    userservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.user.readonly'))
    try:
        results = userservice.users().get(userKey=user).execute()
        if results is not None:
            userexistcontainer = True
        return userexistcontainer
    except:
        return userexistcontainer

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
        return ("Created " + results['name']['givenName'] + " " + results['name']['familyName'] + "'s email (" + results['primaryEmail'] + ")")

    except HttpError as error:
        # see if the error contains the message 'Entity already exists'
        # which is the message it responds with when the email already exists
        if "Entity already exists" in str(error):
            print("User already exists! Going to attempt to unsuspend and add to global address list.")
            # unsuspend user account
            suspensionUser(userEmail=userEmail, suspended=False)
            # reshare email in global address list
            shareProfileInGAL(userEmail=userEmail)
            # update user (email) with proper fields with content in the container object
            results = userservice.users().patch(userKey = userEmail, body = container).execute()
            return ("Unsuspended and added " + userEmail+ " to the global address list.")
        else:
            # an exception occurred that we didn't expect, return it to caller.
            raise Exception(error)
    except Exception as e:
        raise Exception(e)

def listAllSuspendedUsers(customer="my_customer"):
    usercontainer = []
    userservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.user'))
    request = userservice.users().list(customer=customer)
    #try:
    while request is not None:
        results = request.execute()
        for item in results['users']:
            if item['suspended'] == True:
                usercontainer.append(item['primaryEmail'])
        request = userservice.users().list_next(request,results)
    return usercontainer

def listAllActiveUsers(customer="my_customer"):
    usercontainer = []
    userservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.user'))
    request = userservice.users().list(customer=customer)
    #try:
    while request is not None:
        results = request.execute()
        for item in results['users']:
            if item['suspended'] == False:
                usercontainer.append(item['primaryEmail'])
        request = userservice.users().list_next(request,results)
    return usercontainer
    #except:
    #    return "Error"

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

def getUserVerificationCodes(userEmail):
    container = []
    userservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.user.security'))
    try:
        results = userservice.verificationCodes().list(userKey=userEmail).execute()
        return results['items']
    except:
        return "Error"

def generateUserVerificationCodes(userEmail):
    container = {}
    userservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.user.security'))
    try:
        results = userservice.verificationCodes().generate(userKey = userEmail).execute()
        return "Success"
    except:
        return "Error"

def invalidateUserVerificationCodes(userEmail):
    container = {}
    userservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.user.security'))
    try:
        results = userservice.verificationCodes().invalidate(userKey = userEmail).execute()
        return "Success"
    except:
        return "Error"

#Email

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
    try:
        results = emailservice.users().settings().getVacation(userId=userEmail).execute()
        container['response'] = results.get('responseBodyHtml')
        container['subject'] = results.get('responseSubject')
        container['VacationOn'] = results.get('enableAutoReply')
        return container
    except:
        return "Error"

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
    try:
        results = emailservice.users().settings().forwardingAddresses().create(userId=userEmail, body=container).execute()
        return results
    except:
        return "Error"

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

def setAutoForwarding(userEmail, forwardingEmail):
    addForwardingAddress(userEmail,forwardingEmail)
    container = {'enabled':True, 'emailAddress':forwardingEmail, 'disposition':'leaveInInbox'}
    emailservice = build('gmail', 'v1', credentials=impersonateservicecreds(userEmail,'https://www.googleapis.com/auth/gmail.settings.sharing'))
    try:
        results = emailservice.users().settings().updateAutoForwarding(userId=userEmail, body=container).execute()
        return results
    except:
        return "Error"

def removeAutoForwarding(userEmail):
    container = {'enabled':False}
    emailservice = build('gmail', 'v1', credentials=impersonateservicecreds(userEmail,'https://www.googleapis.com/auth/gmail.settings.sharing'))
    try:
        results = emailservice.users().settings().updateAutoForwarding(userId=userEmail, body=container).execute()
        return results
    except:
        return "Error"

def createDelegatedEmail(userEmail,delegateTo):
    container = {'delegateEmail': delegateTo}
    emailservice = build('gmail', 'v1', credentials=impersonateservicecreds(userEmail,'https://www.googleapis.com/auth/gmail.settings.sharing'))
    try:
        results = emailservice.users().settings().delegates().create(userId=userEmail,body=container).execute()
        return results
    except:
        return "Error"

def removeDelegatedEmail(delegatedTo,delegatedFrom):
    emailservice = build('gmail', 'v1', credentials=impersonateservicecreds(delegatedFrom,'https://www.googleapis.com/auth/gmail.settings.sharing'))
    try:
        results = emailservice.users().settings().delegates().delete(delegateEmail=delegatedTo,userId=delegatedFrom).execute()
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

def infoASPS(userEmail, codeID):
    container = []
    aspsservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.user.security'))
    try:
        results = aspsservice.asps().get(codeId=codeID,userkey=userEmail).execute()
        return results
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

def doesGroupExist(groupIDer):
    groupexistcontainer = False
    groupservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.group.readonly'))
    try:
        results = groupservice.groups().get(groupKey=groupIDer).execute()
        if results is not None:
            groupexistcontainer = True
        return groupexistcontainer
    except:
        return groupexistcontainer


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
        return ["No Groups"]

#ChromeDevices
def listChromeDevices(customerID='my_customer',pageToken=None,orderBy="status", orgUnitPath="",projection="FULL"):
    chromecontainer = []
    chromeservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.device.chromeos.readonly'))
    request = chromeservice.chromeosdevices().list(customerId=customerID,pageToken=pageToken,orderBy=orderBy,orgUnitPath=orgUnitPath,projection=projection)
    try:
        while request is not None:
            results = request.execute()
            print(results)
            for item in results['chromeosdevices']:
                chromecontainer.append(item)
            request = chromeservice.chromeosdevices().list_next(request,results)
        return chromecontainer
    except:
        return "Error"

def getChromeDevice(deviceID,customerID='my_customer', projection="FULL"):
    chromeservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.device.chromeos.readonly'))
    try:
        results = chromeservice.chromeosdevices().get(customerId=customerID,deviceId=deviceID,projection=projection)
        return results
    except:
        return "Error"

def actionChromeDevice(deviceID,action,customerID='my_customer',deprovision_reason="same_model_replacement"):
    chromeactioncontainer = {}
    chromeservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.device.chromeos'))
    if action == 'deprovision':
        chromeactioncontainer = {'action':action,'deprovisionReason':deprovision_reason}
    else:
        chromeactioncontainer = {'action':action}
    try:
        results = chromeservice.chromeosdevices().action(customerId=customerID,deviceId=deviceID,body=chromeactioncontainer).execute()
        return results
    except:
        return "Error"

def moveChromeDeviceOU(orgUnitMoveTo,deviceIDs,customerID='my_customer'):
    deviceIDsContainer = {'deviceIds':deviceIDs}
    chromeservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.device.chromeos'))
    try:
        results = chromeservice.chromeosdevices().moveDevicesToOu(customerId=customerID,orgUnitPath=orgUnitMoveTo,body=deviceIDsContainer)
        return results
    except:
        return "Error"




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

def makeEventYearlyRecurring(calendarID,eventID):
    container = {'recurrence':['RRULE:FREQ=YEARLY']}
    calservice = build('calendar', 'v3', credentials=servicecreds('https://www.googleapis.com/auth/calendar'))
    try:
        results = calservice.events().patch(calendarId=calendarID,eventId=eventID, body=container).execute()
        return results
    except:
        return "Error"


def listEvents(userEmail, calendarID='primary'):
    calevents = []
    calservice = build('calendar', 'v3', credentials=impersonateservicecreds(userEmail,'https://www.googleapis.com/auth/calendar'))
    request = calservice.events().list(calendarId=calendarID)
    try:
        while request is not None:
            results = request.execute()
            for item in results['items']:
                calevents.append(item)
            request = calservice.events().list_next(request,results)
        return calevents
    except:
        return "Error"

def listEventIDs(userEmail, calendarID='primary'):
    calevents = []
    calservice = build('calendar', 'v3', credentials=impersonateservicecreds(userEmail,'https://www.googleapis.com/auth/calendar'))
    request = calservice.events().list(calendarId=calendarID)
    try:
        while request is not None:
            results = request.execute()
            for item in results['items']:
                calevents.append(item['id'])
            request = calservice.events().list_next(request,results)
        return calevents
    except:
        return "Error"

def listAllCalendars(userEmail):
    container = {}
    calservice = build('calendar', 'v3', credentials=impersonateservicecreds(userEmail,'https://www.googleapis.com/auth/calendar'))
    try:
        results = calservice.calendarList().list().execute()
        for item in results['items']:
            container[item['summary']] = item['id']
        return container
    except:
        return "Error"

def listCalendarACL(calID, pageToken=None, showDeleted=False):
    container = []
    calservice = build('calendar', 'v3', credentials=servicecreds('https://www.googleapis.com/auth/calendar'))
    request = calservice.acl().list(calendarId=calID,pageToken=pageToken,showDeleted=showDeleted)
    try:
        while request is not None:
            results = request.execute()
            for item in results['items']:
                container.append(item)
            request = calservice.acl().list_next(request,results)
            return container
    except:
        return "Error"


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
    userservice = build('admin', 'directory_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.directory.user'))
    try:
        results = userservice.users().patch(userKey = userEmail, body = container).execute()
        return results
    except:
        return "Error"

#Google Drive
def listDriveFiles(userEmail):
    driveservice = build('drive', 'v3', credentials=impersonateservicecreds(userEmail,'https://www.googleapis.com/auth/drive.readonly'))
    try:
        files = driveservice.files().list().execute()
        return files
    except:
        return "Error"

def transferDriveFileOwner(userEmail, fileID, newOwner):
    container = {'role':'owner','type':'user','emailAddress':newOwner}
    driveservice = build('drive', 'v3', credentials=impersonateservicecreds(userEmail,'https://www.googleapis.com/auth/drive'))
    #try:
    results = driveservice.permissions().create(transferOwnership=True,fileId=fileID,body=container).execute()
    return results
    #except:
    #    return "Error"

def listTeamDrives(pageToken=None):
    drivecontainer = []
    driveservice = build('drive', 'v3', credentials=servicecreds('https://www.googleapis.com/auth/drive.readonly'))
    request = driveservice.teamdrives().list(useDomainAdminAccess=True,pageToken=pageToken)
    try:
        while request is not None:
            results = request.execute()
            for item in results['teamDrives']:
                drivecontainer.append(item)
            request = driveservice.teamdrives().list_next(request,results)
        return drivecontainer
    except:
        return "Error"

#Google Sheets
def getSheetValue(userEmail,sheet,key):
    sheetservice = build('sheets', 'v4', credentials=impersonateservicecreds(userEmail, 'https://www.googleapis.com/auth/spreadsheets.readonly'))
    try:
        sheetvalue = sheetservice.spreadsheets().values().get(spreadsheetId=sheet, range=key).execute()
        return sheetvalue['values']
    except:
        return "Error"



#Reports

def getSuspendReport():
    namecontainer = []
    datecontainer = []
    reportcontainer = {}
    reportservice = build('admin', 'reports_v1', credentials=servicecreds('https://www.googleapis.com/auth/admin.reports.audit.readonly'))
    results = reportservice.activities().list(userKey='all', applicationName='admin', eventName='SUSPEND_USER', maxResults=100).execute()
    for item in results['items']:
        for secondlevel in item['events']:
            for thirdlevel in secondlevel['parameters']:
                namecontainer.append(thirdlevel['value'])
        datecontainer.append(item['id']['time'])
    reportcontainer = dict(zip(namecontainer,datecontainer))
    suspendoutput = pandas.DataFrame.from_dict(reportcontainer,orient='index')
    suspendoutput.to_csv("suspendreport.csv")


def getLastLogin():
    names = []
    lastlogin = []
    activeusers = listAllActiveUsers()
    for user in activeusers:
        response = getUser(user, "lastLoginTime")
        if str(response) != "[]":
            names.append(user)
        lastlogin.append(response)
    else:
        pass
    output = dict(zip(names,lastlogin))
    lastlogin = pandas.DataFrame.from_dict(output,orient='index')
    lastlogin.to_csv("lastlogin.csv")
