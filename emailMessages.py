# version 2lines
import json
import sys
import smtplib
import webbrowser
from collections import defaultdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bottle import template


class SendMessageEmail(object):
    def __init__(self):
        self.mail_sender = "qinshu.liu@citrix.com"
        self.mail_receiver = "qinshu.liu@citrix.com"  # ,yanyan.zhu@citrix.com,lei.wang1@citrix.com
        self.host = 'smtp.citrix.com'
        self.port = 25
        self.server = self.start_server()

    def start_server(self):
        server = smtplib.SMTP(self.host, self.port)
        server.ehlo()
        server.starttls()
        server.ehlo()
        print("---------------Email Server Ready---------------")
        return server

    def generate_message(self, subject, message_html):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.mail_sender
        msg['To'] = self.mail_receiver
        msg.attach(message_html)
        return msg

    def generate_message_html(self, compareMetaList, branchx):
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
                            <td><a href='#{{component}}'>{{component}}</a>
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
                        <h3><a href="{{component}}" name="{{component}}" jumpthis="{{component}}" ></a>{{component}} </h3>
                        %if detail == 'N/A':
                            <ul><li>N/A</li></ul>
                        %else:
                            %count =1
                            %for id, val in detail.items():

                                        <div style="line-height:30px;"> &nbsp&nbsp&nbsp&nbsp{{count}}.<a href='https://code.citrite.net/projects/XD/repos/appmanagement/commits/{{id}}'>
                                         &nbsp&nbsp{{val['displayId']}}</a>   &nbsp - &nbsp   {{val['author']}} &nbsp&nbsp  {{val['date']}}</div>
                                        <br /><div  class="breakline"> &nbsp&nbsp&nbsp&nbsp{{val['message']}}</div>

                              <hr>  
                              %count +=1
                            %end


                        %end  
                    %end

        <br>
		<br>
		<br>
		<p class="ending">Thanks,</p>
		<p class="ending">Release Content Management Service</p>
		 <style>

		    p {font-family:Arial,Helvetica,sans-serif;}
		    p.ending {style="font-size:14px;"}
            a { text-decoration:none;} 
            td {font-size:16px; font-family:Arial,Helvetica,sans-serif;}
            .breakline{max-width:800px; max-height:700px; word-break:break-all;word-wrap:break-word;}
        </style>

        </body>
        </html>
        """
        message_html = template(message_html, items=[compareMetaList, branchx])
        return message_html

    def send_email(self, compareMetaList, branchx):
        print("***********************Start to Send Email***********************")
        subject = "Release Content Report ({})".format(branchx)
        message_html = self.generate_message_html(compareMetaList, branchx)
        message_html = MIMEText(message_html, _subtype='html', _charset='utf-8')
        message = self.generate_message(subject, message_html)
        try:
            self.server.send_message(message)
            print("*******************Email Sent Successfully*******************")
        except (smtplib.SMTPAuthenticationError, smtplib.SMTPServerDisconnected):
            print("***************Authentication Expired, Waiting for Starting new Server****************")
            self.server = self.start_server()
            self.server.send_message(message)
            print("*******************Email Sent Successfully*******************")
        except:
            print("Unable to send the email. Error: {}".format(sys.exc_info()[0]))



