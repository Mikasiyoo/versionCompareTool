import webbrowser

import requests
import json
from bottle import template

class generateContentHtml(object):
    def getallcompareMetaList(self,compareMetaList,components):
        for component in components:
            if not component in compareMetaList.keys():
                compareMetaList[component] = 'N/A'
        return compareMetaList

    def generatemessage_html(self,branchx,branchy,components):
        filename = 'compareMetaList-from-' + branchx + '-to-' + branchy + '.json'
        with open(filename, 'r') as f:
            compareMetaList = json.load(f)
        compareMetaList = self.getallcompareMetaList(compareMetaList,components)
        message_html = """
            <html>
            <head><h2>Release Content Report ({{items[1]}})</h2></head>
            <body>
            <br>
            <br>
            <table cellpadding="10" style="border-style: solid;border-width: 3px;">
            <th style="font-size:18px;"><b>Catalog</b></th>
            %for component, detail in items[0].items():
                <tr>
                    <td style="font-size:16px;" ><a href='#{{component}}'>{{component}}</a>
                    %if detail == 'N/A':
                        - No commit is included
                    %else:
                        %if len(detail) == 1:
                            - {{len(detail)}} commit is included
                        %else:
                            - {{len(detail)}} commits are included
                        %end
                    %end
                    </td>
                </tr>
            %end
            </table >
            <br>

            %for component, detail in items[0].items():
                <h3> <a href="{{component}}" id="{{component}}" jumpthis="{{component}}" ></a>{{component}} </h3>
                %if detail == 'N/A':
                    <ul><li>N/A</li></ul>
                %else:
                <ol>
                    %for id, val in detail.items():
                    <li>
                        <table cellspacing="10px" style="table-layout:fixed;" >
                            <tr >
                                <td style="width: 100px;"><a href='https://code.citrite.net/projects/XD/repos/appmanagement/commits/{{id}}'>{{val['displayId']}}</a></td>
                                <td class="breakline">{{val['message']}}</td>
                                <td style="width: 100px;">{{val['author']}}</td>
                                <td style="width: 100px;"> {{val['date']}}<td>
                            </tr>
    
                            %if val['issue'] != 'N/A':
                                <tr >
                                    <td style="width: 100px;"><a href='https://issues.citrite.net/browse/{{list(val['issue'].keys())[0]}}'><b>{{list(val['issue'].keys())[0]}}</b></a> </td>
                                    <td class="breakline">{{list(val['issue'].values())[0]}}</td>
                                </tr>
                            %end
                        </table>
                        </li><hr>
                    %end
                    </ol>
                %end  
            %end
            <style>
                td.breakline{width:900px;word-break:break-all;word-wrap:break-word;}
                tr.jiraheight{height:60px;}
            </style>
            </body>
            </html>
            """
        message_html = template(message_html, items=[compareMetaList,branchx])
        return message_html


