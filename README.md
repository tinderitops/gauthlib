GAuthLib

Python3

Created by https://github.com/robolague/ and https://github.com/edwinruizr

A python function library for accessing Google APIs (Admin SDK, Mail, and Calendar)

Download this repo and from the directory:
```
pip3 install -r requirements.txt
```

To set your passwords up, edit gauthlib and replace:
```
my_admin = 'admin.user@domain.com' with your own admin user.
```

Project Setup:
```
https://console.cloud.google.com/projectcreate
```

Name the project anything you want, then go to:

https://console.cloud.google.com/apis/library?

Enable Gmail API and Admin SDK, Calendar API, Drive API, Sheets API

To enable a service account(required):

https://console.cloud.google.com/iam-admin/serviceaccounts/project

Service account user role for the service account. Get the service account name (will end in iam.gserviceaccount.com)

edit gauthlib and replace:
```
service_account = 'myservice@projectname.iam.gserviceaccount.com'
```

For the service account, download the JSON key and place it in the same directory as this file. Get the name of the key and edit gauthlib and replace:
```
json_file_name = 'myJSONkey.json'
```

Be sure to enable Site-Wide Delegation for the service account user.
Open the JSON file and retrieve the 'client_id' and make a note of it.

Go to https://admin.google.com/ManageOauthClients

For your client_id, authorize the following scopes (or any subset you will need for the function(s) you want to use):
```
https://www.googleapis.com/auth/admin.directory.user,
https://www.googleapis.com/auth/admin.directory.group,
https://www.googleapis.com/auth/admin.directory.group.member,
https://www.googleapis.com/auth/admin.directory.device.mobile,
https://www.googleapis.com/auth/admin.directory.userschema,
https://www.googleapis.com/auth/gmail.settings.basic,
https://www.googleapis.com/auth/gmail.settings.sharing,
https://www.googleapis.com/auth/admin.directory.user.security,
https://mail.google.com/,
https://www.googleapis.com/auth/calendar,
https://www.googleapis.com/auth/gmail.modify,
https://www.googleapis.com/auth/gmail.settings.basic,
https://www.googleapis.com/auth/gmail.settings.sharing,
https://www.googleapis.com/auth/spreadsheets.readonly,
https://www.googleapis.com/auth/drive,
https://www.googleapis.com/auth/drive.file,
https://www.googleapis.com/auth/drive.readonly,
https://www.googleapis.com/auth/spreadsheets,
https://www.googleapis.com/auth/spreadsheets.readonly,
https://www.googleapis.com/auth/admin.datatransfer,
https://www.googleapis.com/auth/admin.datatransfer.readonly
```


API References:

https://developers.google.com/admin-sdk/directory/v1/reference/

https://developers.google.com/gmail/api/v1/reference/

https://developers.google.com/calendar/v3/reference/

https://developers.google.com/admin-sdk/data-transfer

https://developers.google.com/sheets/api/reference/rest/

https://developers.google.com/drive/api/v3/reference/
