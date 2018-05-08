import requests
import base64
import time
import json
from collections import defaultdict
from datetime import datetime
from emailMessages import SendMessageEmail

#generate basic auth
def  make_base_auth(user,password):
    tok = user + ':' + password
    bytestok = tok.encode(encoding="utf-8")
    hash = base64.b64encode(bytestok).decode("utf-8")
    return "Basic " + hash

#load version compare infomation
def loadVersionCompareInfo(branchx,branchy,auth):
    DDC_url = "https://code.citrite.net/rest/api/1.0/projects/XD/repos/appmanagement/compare/commits"
    querystring = {"from":"refs/heads/"+branchx,"to":"refs/heads/"+branchy,"limit":"9000"}
    response = requests.request("GET", DDC_url, headers=headers, params=querystring)
    return response.json()

#load commit infomation
def loadcommitInfo(id):
    commit_url = "https://code.citrite.net/rest/api/1.0/projects/XD/repos/appmanagement/commits/"+id
    querystring = {"limit": "9000"}
    response = requests.request("GET", commit_url, headers=headers, params=querystring)
    return response.json()

#load commit diff infomation ,get component info
def loadcommitDiffInfo(id):
    commitDiff_url = "https://code.citrite.net/rest/api/1.0/projects/XD/repos/appmanagement/commits/" + id+"/diff"
    querystring = {"limit": "9000"}
    response = requests.request("GET", commitDiff_url, headers=headers, params=querystring)
    return response.json()

def loadIssueSummary(jirakey):
    jira_url="https://issues.citrite.net/rest/api/2/issue/"+jirakey
    querystring = {"limit": "9000"}
    response = requests.request("GET", jira_url, headers=headers, params=querystring)
    return response.json()

def loadBranches():
    branch_url = "https://code.citrite.net/rest/api/1.0/projects/XD/repos/appmanagement/branches"
    querystring = {"limit": "9000"}
    response = requests.request("GET", branch_url, headers=headers, params=querystring)
    return response.json()

def getLatestBranch():
    branches = loadBranches()
    branchvalue = branches['values']
    ans = []  #all the release branches
    for branch in branchvalue:
        branchId = branch['displayId']
        if 'release-cloud' in branchId and branchId.index('release-cloud') == 0 and len(branchId)<=16:
            ans.append(branchId)
    return ans[:2]


def loadcommitofComponent(commitofComponent,id):
    commitDiff = loadcommitDiffInfo(id)
    length = len(commitDiff['diffs'])
    if length != 0:  # if diffs is not empty, empty is 'grey merge'
        commitDiffdiffs = commitDiff['diffs']
        commitofComponent[id] = getComponent(commitDiffdiffs)
    return commitofComponent

def getComponent(commitDiffdiffs):
    componentList = []
    for i in commitDiffdiffs:
        if i['source'] != None and i['source']['components'][0] not in componentList:
                componentList.append(i['source']['components'][0])
        if i['destination'] != None and i['destination']['components'][0] not in componentList:
                componentList.append(i['destination']['components'][0])
    return componentList


def collectByComponent(dict,components): #{components：[id]}
    newdict = defaultdict()
    for i in components:
        newdict[i] = []
    for id, componentList in dict.items():
        for component in componentList:
            if component in components:
                newdict[component].append(id)
    return newdict

def timeStamptotime(timestamp):  #return local time
    time_local = time.localtime(timestamp/1000)
    dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    return dt

def timestamp_to_utc_strtime(timestamp): #return UTC time
    utc_str_time = datetime.utcfromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
    return utc_str_time

#jiraSummaryDict:load jiarkey to its summary message(value)
def getjiraSummaryDict(commitDataDict):
    jiraSummaryDict = defaultdict()
    for id in commitDataDict.keys():
        if commitDataDict[id]['issue'] != None:
            #print(id)
            jirakeyList = commitDataDict[id]['issue']  # jirakeyList is a list , one commit may be linked with several issues
            for jirakey in jirakeyList:
                if jirakey not in jiraSummaryDict.keys():
                    jiraSummary = loadIssueSummary(jirakey)
                    jiraSummaryDict[jirakey] = jiraSummary['fields']['summary']
        #print(id)
    return jiraSummaryDict

def getcompareMetaList(components,componentofCommit,commitDataDict,jiraSummaryDict):
    compareMetaList = defaultdict(dict) # the final conclude object
    for component in components:
        for id in componentofCommit[component]:
            try:
                compareMetaList[component][id] = commitDataDict[id]
                keyList = commitDataDict[id]['issue']  # issue is a list
                if keyList != None and keyList != 'N/A':
                    compareMetaList[component][id]['issue'] = defaultdict(dict)
                    for key in keyList:
                        compareMetaList[component][id]['issue'][key] = jiraSummaryDict[key]
                else:
                    compareMetaList[component][id]['issue'] = 'N/A'  ##here, first define issue is 'N/A'
            except Exception  as e:
                print(str(e))
                print(id)
                print(componentofCommit[component][id])
    return compareMetaList

def generatecompareMetaListJson(branchx,branchy,compareMetaList):
    filename = 'compareMetaList-from-'+branchx+'-to-'+branchy+'.json'
    with open(filename, "w") as f:
        json.dump(compareMetaList, f, indent=4)
        print('load json file success.')

#define when some components do not have commits
def getallcompareMetaList(compareMetaList,components):
    for component in components:
        if not component in compareMetaList.keys():
            compareMetaList[component] = 'N/A'
    return compareMetaList

def getconfigInfo():
    with open('user.json', 'r') as f:
        fb=json.load(f)
    return fb

#get component to jira dict
def getcomponentTojira(branchx,branchy,components):
    filename = 'compareMetaList-from-' + branchx + '-to-' + branchy + '.json'
    with open(filename, 'r') as f:
        compareMetaList = json.load(f)
    componentTojira = defaultdict(list)
    for component in compareMetaList.keys():
        for id in compareMetaList[component].keys():
            issue = compareMetaList[component][id]['issue']
            if issue != 'N/A' and issue not in componentTojira[component]:
                componentTojira[component].append(issue)
    for component in components:
        if not component in componentTojira.keys():
            componentTojira[component] = 'N/A'
    return [componentTojira,branchx]

def work():
    sleeptime = 24 * 3600  # run every 24h
    while True :
        print('start',time.strftime("%H:%M:%S"))

        latestBranch = getLatestBranch()
        branchx = latestBranch[0]  # from
        branchy = latestBranch[1]  # to
        print('compare from %s to %s.'%(branchx,branchy))
        commitDataDict = defaultdict(dict)  # id to its displayId, author, message, issue, date
        VersionCompareInfo = loadVersionCompareInfo(branchx,branchy,auth) # raw campare infomation
        commitofComponent = defaultdict()  # id to component

    #load commitdatadict and commitofComponent
        for commits in VersionCompareInfo['values']:
            if True :#'Merg' not in commits['message']
                id = commits['id']    #eg id='67367463687' is string
                commitDetail = loadcommitInfo(id)
                commitDataDict[id]['displayId'] = commitDetail['displayId']
                commitDataDict[id]['message'] = commitDetail['message']
                commitDataDict[id]['date'] = timestamp_to_utc_strtime(commitDetail["committerTimestamp"]) #eg:1524173017000

                if 'displayName' in commitDetail['author'].keys() :
                    commitDataDict[id]['author'] = commitDetail['author']['displayName']
                else:
                    commitDataDict[id]['author'] = commitDetail['author']['name']

                if 'properties' in commitDetail.keys() and 'jira-key' in commitDetail["properties"].keys():
                    commitDataDict[id]['issue'] = commitDetail["properties"]['jira-key']
                else:
                    commitDataDict[id]['issue'] = None
                print(id)
                commitofComponent = loadcommitofComponent(commitofComponent,id)
        print('commitDataDict done')

        componentofCommit = collectByComponent(commitofComponent,components)#key is component, value is commit id
        print('componentofCommit done')
        jiraSummaryDict = getjiraSummaryDict(commitDataDict)
        print('jiraSummaryDict done')
        compareMetaList = getcompareMetaList(components,componentofCommit,commitDataDict,jiraSummaryDict)
        print(compareMetaList)
        generatecompareMetaListJson(branchx,branchy,compareMetaList) # write compareMetaList to a json file

        #send emails
        compareMetaList = getallcompareMetaList(compareMetaList, components)
        mail = SendMessageEmail()
        mail.send_email(compareMetaList, branchx)

        #sleep
        time.sleep(sleeptime)


fb = getconfigInfo()
user=fb['user']
password=fb['password']
PostmanToken=fb['PostmanToken']
auth = make_base_auth(user,password)

headers = {
            'Authorization': auth,
            'Cache-Control': "no-cache",
            'Postman-Token': PostmanToken
            }

components = ['Brokering','Operations','Infrastructure',
              'GroupPolicy','Provisioning','Studio','Upm'] #component should be shown


if __name__ == '__main__':
    print("versionComparebot online")
    try:
        work()
    except Exception as e:
        print("Exception Occurred..", str(e))
        #emailMessages.report_email_error(sys.exc_info(), "error")