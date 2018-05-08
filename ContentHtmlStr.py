import json

import requests

def changeSpecialChar(str):
    if '&' in str:
        str=str.replace('&', '&amp;')
    if '<' in str :
        str=str.replace('<', '&lt;')
    return str

def getallcompareMetaList(compareMetaList, components):
    for component in components:
        if not component in compareMetaList.keys():
            compareMetaList[component] = 'N/A'
    return compareMetaList

def generateContentHtmlStr(branchx,branchy,components):
    filename = 'compareMetaList-from-' + branchx + '-to-' + branchy + '.json'
    with open(filename, 'r') as f:
        compareMetaList = json.load(f)
    compareMetaList = getallcompareMetaList(compareMetaList, components)
    message_html = "<h2>Release Content Report ({})</h2><br></br><br></br><table cellpadding='10' style='border-style: solid;border-width: 3px;'><th style='font-size:18px;'><b>Catalog</b></th>".format(branchx)
    for component, detail in compareMetaList.items():
        message_html +="<tr><td style='font-size:16px;'> <a href ='#{}'> {} </a>".format(component,component)
        if detail == 'N/A':
            message_html +="- No commit is included"
        else:
            if len(detail) == 1:
                message_html += "- {} commit is included".format(len(detail))
            else:
                message_html += "- {} commits are included".format(len(detail))
        message_html += "</td></tr>"
    message_html += "</table><br></br>"

    for component, detail in compareMetaList.items():
        message_html += "<h3><a href='{}' id='{}'></a>{}</h3>".format(component,component,component)
        if detail == 'N/A':
            message_html += "<ul><li>N/A</li></ul>"

        else:
            message_html += "<ol>"
            for id, val in detail.items():
                message_html += '<li><table width= "100%" cellspacing="10px"  style="table-layout:fixed;"><tr>' \
                                '<td class="outer"><a href="https://code.citrite.net/projects/XD/repos/appmanagement/commits/{}">{}</a></td>' \
                                '<td width="600px" class="breakline">{}</td>' \
                                '<td class="outer">{}</td>' \
                                '<td class="outer">{}</td>' \
                                '</tr>'.format(id,val['displayId'],changeSpecialChar(val['message']),val['author'],val['date'])
                if val['issue'] != 'N/A':
                    message_html += '<tr>' \
                                    '<td class="outer"><a href="https://issues.citrite.net/browse/{}"><b>{}</b></a></td>' \
                                    '<td width="600px" class="breakline">{}</td></tr>'.format(list(val['issue'].keys())[0],list(val['issue'].keys())[0],changeSpecialChar(list(val['issue'].values())[0]))
                message_html += '</table></li><hr />'
            message_html += '</ol>'

    message_html += '<style>td.outer{border:void;}' \
                    'td.breakline{width:600px;word-break:break-all;word-wrap:break-word;}' \
                    'tr.jiraheight{height:60px;}</style>'

    return message_html

def set_page_json(json_content):
    headers = {
        'Content-Type': 'application/json',
    }
    response = requests.put("https://info.citrite.net/rest/api/content/1295236079", headers=headers, data=json.dumps(json_content),
                 auth=('qinshul', 'SStt700523;'))
    response.encoding = "utf8"
    return(response.text)

components = ['Brokering','Operations','Infrastructure',
              'GroupPolicy','Provisioning','Studio','Upm']
branchx='release-cloud60'
branchy='release-cloud59'
contentHTML = generateContentHtmlStr(branchx,branchy,components)

print(contentHTML)
json_content ={'body':
                   {'storage':
                        {'representation': 'storage',
                         'value': contentHTML }
                    },
                'title': u'Release Content Management Service test',
                'version': {'number': 28},
                'key': u'INFO',
                'type': u'page',
                'id': u'1295236079'}


print(set_page_json(json_content))






