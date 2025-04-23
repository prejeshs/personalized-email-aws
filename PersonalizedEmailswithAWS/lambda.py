from datetime import date, datetime, timezone, timedelta
from newsapi import NewsApiClient
import boto3
from botocore.exceptions import ClientError
import json

class NewsMails:
    def __init__(self):
        client = boto3.resource('dynamodb', region_name="ap-south-1")
        self.table = client.Table('NewSubscribers')
        self.NewsApikey = '2b8bbd66c2e2403692a4e778e0697c21'
        self.ses_client = boto3.client('ses',region_name="ap-south-1")
    def GetAllDynamoDBRecord (self):
        try :
            response = self.table.scan()
            emaildata = response['Items']
            while 'LastEvaluatedKey' in response:
                response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                emaildata.extend(response['Items'])
        except ClientError as e:
            print(e.response['Error']['Message'])
            self.Email_Failed_Transaction("An exception occured while fetching DynamoDB records")
        else:
            print("Records found in DynamoDB, returning the records now"),
            return emaildata

    def GetAllNews (self , search, UserName, Email) :
        try :
            print("Getting news for the run")
            newsapi = NewsApiClient(api_key= self.NewsApikey)
            from_date = datetime.now(timezone.utc) + timedelta(days=-3)
            end_time = datetime.now(timezone.utc) + timedelta(days=0)
            all_articles = newsapi.get_everything(q=search,from_param=from_date,to=end_time,language='en',sort_by='relevancy')
            print(all_articles)
            if all_articles :
                print("News API returned the following")
                dt = date.today()
                iso_date = dt.isoformat()
                all_articles.update({"UserName": UserName, "Email":Email, "ISODate": iso_date, "SearchString": search})
            if all_articles['articles']:
                print("Response contains news, sorting now")
                all_articles['articles'].sort(key=lambda item:item['publishedAt'], reverse=True)
            else:
                print("Response does not contain any news, sending fail mail")
                self.Email_Failed_Transaction("Response does not contain any news, sending fail mail")
        except ClientError as e:
            print(e.response['Error']['Message'])
            self.Email_Failed_Transaction("An exception occured during the API call")
        else:
            print("News has been retrieved, returning now"),
            return all_articles

    def CreateUpdateEmailTemplate(self):
        try :
            print("Getting news for the run")
            Getresponse = self.ses_client.get_template( TemplateName='NewAPIResultsMail')
            if Getresponse['Template'] and Getresponse['ResponseMetadata']['HTTPStatusCode'] == 200 :
                print("Template already exists. Updating the template now")
                self.ses_client.update_template( 
                                Template={
                                        "TemplateName": "NewAPIResultsMail",
                                        "SubjectPart": "News On {{ SearchString }} for Date : {{ISODate}}",
                                        "HtmlPart": """<html>
                                                    <head>
                                                    <style>
                                                        table, td {
                                                        border: 1px solid black;
                                                        border-collapse: collapse;
                                                        }
                                                        
                                                        
                                                        th {
                                                        border: 1px solid black;
                                                        border-collapse: collapse;
                                                        font-weight: bold
                                                        }
                                                        
                                                        
                                                        td, th {
                                                        padding-left: 15px;
                                                        text-align: left;
                                                        }
                                                    </style>
                                                    </head>
                                                    <body>
                                                    <p style="font-family:'Futura Medium'">Hello {{ UserName }},</p>
                                                    <p style="font-family:'Futura Medium'">Below is the requested news on {{ SearchString }} for Date : {{ISODate}}:</p>
                                                    
                                                    <table style="width:100%">
                                                        <col style="width:50%">
                                                        <col style="width:50%">
                                                        <tr bgcolor="yellow">
                                                            <td>SourceId</td>
                                                            <td>SourceName</td>
                                                            <td>Author</td>
                                                            <td>Title</td>
                                                            <td>Description</td>
                                                            <td>Url</td>
                                                            <td>UrlToImage</td>
                                                            <td>PublishedAt</td>
                                                            <td>Content</td>
                                                        </tr>
                                                        {{#each articles}}
                                                        <tr>
                                                        <td>{{source.id}}</td>
                                                        <td>{{source.name}}</td>
                                                        <td>{{author}}</td>
                                                        <td>{{title}}</td>
                                                        <td>{{description}}</td>
                                                        <td>{{url}}</td>
                                                        <td>{{urlToImage}}</td>
                                                        <td>{{publishedAt}}</td>
                                                        <td>{{content}}</td>
                                                        </tr>
                                                        {{/each}}
                                                    </table>

                                                    <p style="font-family:'Futura Medium'">Please check with p64517412@gmail.com for any queries on the email.</p>
                                                    
                                                    <p style="font-family:'Futura Medium'">Best Regards,</p>
                                                    <p style="font-family:'Futura Medium'">Team PS</p>
                                                    </body>
                                                    </html>
                                                    """,
                                        "TextPart": """
                                                    Hello {{ UserName }},
                                                    
                                                    Below is the requested news on {{ SearchString }} for Date : {{ISODate}}:  
                                                            
                                                        {{#each articles}}
                                                        {{source.id}}
                                                        {{source.name}}
                                                        {{author}}
                                                        {{title}}
                                                        {{description}}
                                                        {{url}}
                                                        {{urlToImage}}
                                                        {{publishedAt}}
                                                        {{content}}
                                                        {{/each}}

                                                    Please check with p64517412@gmail.com for any queries on the email.
                                                    
                                                    Best Regards,
                                                    Team PS
                                                    """
                                    }
                                )
            print("SES template is updated successfully")
            return True
        except ClientError as e:
            print("SES template does not exist. Creating now")
            self.ses_client.create_template(
                                Template={ 
                                        "TemplateName": "NewAPIResultsMail",
                                        "SubjectPart": "News On {{ SearchString }} for Date : {{ISODate}}",
                                        "HtmlPart": """<html>
                                                    <head>
                                                        <style>
                                                            table, td {
                                                            border: 1px solid black;
                                                            border-collapse: collapse;
                                                            }
                                                            
                                                            
                                                            th {
                                                            border: 1px solid black;
                                                            border-collapse: collapse;
                                                            font-weight: bold
                                                            }
                                                            td, th {
                                                            padding-left: 15px;
                                                            text-align: left;
                                                            }
                                                        </style>
                                                    </head>
                                                    <body>
                                                    <p style="font-family:'Futura Medium'">Hello {{ UserName }},</p>
                                                    <p style="font-family:'Futura Medium'">Below is the requested news on {{ SearchString }} for Date : {{ISODate}}:</p>
                                                    
                                                    <table style="width:100%">
                                                        <col style="width:50%">
                                                        <col style="width:50%">
                                                        <tr bgcolor="yellow">
                                                            <td>SourceId</td>
                                                            <td>SourceName</td>
                                                            <td>Author</td>
                                                            <td>Title</td>
                                                            <td>Description</td>
                                                            <td>Url</td>
                                                            <td>UrlToImage</td>
                                                            <td>PublishedAt</td>
                                                            <td>Content</td>
                                                        </tr>
                                                        {{#each articles}}
                                                        <tr>
                                                        <td>{{source.id}}</td>
                                                        <td>{{source.name}}</td>
                                                        <td>{{author}}</td>
                                                        <td>{{title}}</td>
                                                        <td>{{description}}</td>
                                                        <td>{{url}}</td>
                                                        <td>{{urlToImage}}</td>
                                                        <td>{{publishedAt}}</td>
                                                        <td>{{content}}</td>
                                                        </tr>
                                                        {{/each}}
                                                    </table>

                                                    <p style="font-family:'Futura Medium'">Please check with p64517412@gmail.com for any queries on the email.</p>
                                                    
                                                    <p style="font-family:'Futura Medium'">Best Regards,</p>
                                                    <p style="font-family:'Futura Medium'">Team PS</p>
                                                    </body>
                                                    </html>
                                                    """,
                                        "TextPart": """
                                                    Hello {{ UserName }},
                                                    
                                                    Below is the requested news on {{ SearchString }} for Date : {{ISODate}}:  
                                                            
                                                        {{#each articles}}
                                                        {{source.id}}
                                                        {{source.name}}
                                                        {{author}}
                                                        {{title}}
                                                        {{description}}
                                                        {{url}}
                                                        {{urlToImage}}
                                                        {{publishedAt}}
                                                        {{content}}
                                                        {{/each}}

                                                    Please check with p64517412@gmail.com for any queries on the email.
                                                    
                                                    Best Regards,
                                                    Team PS
                                                    """
                                    }
                                )
            print("SES template created successfully")
            return True

    def Email_News(self , SourceEmail, ToEmail, finalresult):
        try:
            Sendresponse = self.ses_client.send_templated_email(
                                    Source=SourceEmail,
                                    Destination={
                                        'ToAddresses': [
                                            ToEmail
                                        ]
                                    },
                                    Template='NewAPIResultsMail',
                                    TemplateData= finalresult
                                )
        except Exception as e:
            print(str(e))
            self.Email_Failed_Transaction("An exception occured while sending the templated email")
        if Sendresponse['ResponseMetadata']['HTTPStatusCode'] == 200:
            print('Email sent successfully')
        else :
            print('Failed to send Email')

    def Email_Failed_Transaction(self, ReasonForFailure):
        try:
            print("Sending failed email now")
            body_text = """
                Hello,
                
                Error in automated news delivery.         
                Please check the Lambda CloudWatch logs for further insight.

                Reason for failure is : """ + ReasonForFailure + """
                
                Best Regards,
                Team PS.
                """

            # The HTML body of the email.
            body_html = """<html>
                <head>
                <style>
                    table, td {
                    border: 1px solid black;
                    border-collapse: collapse;
                    }
                    
                    
                    th {
                    border: 1px solid black;
                    border-collapse: collapse;
                    font-weight: bold
                    }
                    
                    
                    td, th {
                    padding-left: 15px;
                    text-align: left;
                    }
                </style>
                </head>
                <body>
                <p style="font-family:'Futura Medium'">Hello Labs,</p>

                <p style="font-family:'Futura Medium'">Error in automated news delivery.</p>
                <p style="font-family:'Futura Medium'">Please check the Lambda CloudWatch logs for further insight.</p>

                <p style="font-family:'Futura Medium'">Reason for failure is : """ + ReasonForFailure + """</p>
                
                <p style="font-family:'Futura Medium'">Best Regards,</p>
                <p style="font-family:'Futura Medium'">Team PS.</p>
                </body>
                </html>
                """
            # Provide the contents of the email.
            send_mail_response = self.ses_client.send_email(
                Source="p64517412@gmail.com",
                Destination={
                    'ToAddresses': ["example1@gmail.com"]
                },
                Message={
                    'Subject': {
                        'Data': "Schdeduled automated news delivery failed."

                    },
                    'Body': {
                        'Text': {
                            'Data': body_text

                        },
                        'Html': {
                            'Data': body_html

                        }
                    }
                }
            )
            print(send_mail_response)
            return send_mail_response
        except Exception as e:
            print(str(e))
            return str(e)

def lambda_handler(event, context):
    print("Started execution")
    OjectNewsMails = NewsMails() 
    CreateTemplate = OjectNewsMails.CreateUpdateEmailTemplate()
    if CreateTemplate :
        print("Email template updated successfully")
        TableResults = OjectNewsMails.GetAllDynamoDBRecord()
        if TableResults:
            print("DynamoDB contains records, processing now")
            for tableitem in TableResults:
                NewResults = OjectNewsMails.GetAllNews(tableitem['google-search'], tableitem['user'], tableitem['email'] )
                if NewResults :
                    print("News results returned, emailing now")
                    result = json.dumps(NewResults)
                    finalresultstr =  result.replace("null", "\"NA\"")
                    OjectNewsMails.Email_News( "p64517412@gmail.com", tableitem['email'], finalresultstr)
                    ReasonForFail = "Newsletter email sent for user {} with email {} on {}".format(tableitem['user'], tableitem['email'], tableitem['google-search'])
                    print(ReasonForFail)
                else:
                    print("No news results retrieved, sending fail mail now")
                    ReasonForFail = "No news results retrieved for user {} with email {} on {}".format(tableitem['user'], tableitem['email'], tableitem['google-search'])
                    OjectNewsMails.Email_Failed_Transaction(ReasonForFail)
        else:
            print("DynamoDB does not contain any email data, failed to send email")
            OjectNewsMails.Email_Failed_Transaction("DynamoDB does not contain any email data")
    else :
        print("Email template update has failed")
