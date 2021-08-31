from flask import Flask, render_template, request
import json
import requests
import time
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
app = Flask(__name__)

@app.route('/')
def home():
   return render_template('home.html')

@app.route('/mail',methods = ['POST', 'GET'])
def mail():
   if request.method == 'POST':
      result = request.form
      url = "https://api.symbl.ai/oauth2/token:generate"
      appId = request.form.get("appId")  # App Id found in your platform
      appSecret = request.form.get("appSecret")  # App Id found in your platform
      videopath= request.form.get("videofile")  # Location of Video file
      print(appId)
      print(appSecret)
      payload = {"type": "application","appId": appId,"appSecret": appSecret}
      headers = {'Content-Type': 'application/json'}
      responses = {400: 'Bad Request! Please refer docs for correct input fields.',401: 'Unauthorized. Please generate a new access token.',404: 'The conversation and/or it\'s metadata you asked could not be found, please check the input provided',429: 'Maximum number of concurrent jobs reached. Please wait for some requests to complete.',500: 'Something went wrong! Please contact support@symbl.ai'}
      response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
      if response.status_code == 200:
          # Successful API execution
          print("accessToken => " + response.json()['accessToken'])  # accessToken of the user
          print("expiresIn => " + str(response.json()['expiresIn']))  # Expiry time in accessToken
      elif response.status_code in responses.keys():
          print(responses[response.status_code], response.text)  # Expected error occurred
      else:
          print("Unexpected error occurred. Please contact support@symbl.ai" + ", Debug Message => " + str(response.text))
      time.sleep(60)
      video_url = "https://api.symbl.ai/v1/process/video/url"
      # save FPDF() class into a
      # # variable pdf
      pdf = FPDF()
      # Add a page
      pdf.add_page()
      # set style and size of font
      # # that you want in the pdf
      pdf.set_font("Arial", size = 10)
      # create a cell
      # set your access token here. See https://docs.symbl.ai/docs/developer-tools/authentication
      access_token = response.json()['accessToken']
      video_headers = {'Authorization': 'Bearer ' + access_token,'Content-Type': 'application/json' }
      video_payload = {'url': videopath,'name': "BusinessMeeting",'confidenceThreshold': 0.6,}
      video_responses = {400: 'Bad Request! Please refer docs for correct input fields.',401: 'Unauthorized. Please generate a new access token.',404: 'The conversation and/or it\'s metadata you asked could not be found, please check the input provided',429: 'Maximum number of concurrent jobs reached. Please wait for some requests to complete.',500: 'Something went wrong! Please contact support@symbl.ai'}
      video_response = requests.request("POST", video_url, headers=video_headers, data=json.dumps(video_payload))
      print(video_response.json()['conversationId'])
      if video_response.status_code == 201:
          # Successful API execution
          print("conversationId => " + video_response.json()['conversationId'])
          print("jobId => " + video_response.json()['jobId'])  # ID to be used with Job API.
      elif video_response.status_code in video_responses.keys():
          print(video_responses[video_response.status_code])  # Expected error occurred
      else:
          print("Unexpected error occurred. Please contact support@symbl.ai" + ", Debug Message => " + str(response.text))
      sptxt_baseUrl = "https://api.symbl.ai/v1/conversations/{conversationId}/messages"
      # Generated using Submit text end point
      conversationId=video_response.json()['conversationId']
      print(conversationId)
      sptxt_url = sptxt_baseUrl.format(conversationId=conversationId)
      print(sptxt_url)
      # Speech to Text/ Storing Meeting Transcription
      sptxt_header = {'Authorization': 'Bearer ' + access_token,'Content-Type': 'application/json'}
      sptxt_params = {'verbose': True, 'sentiment': True }
      sptxt_responses = {401: 'Unauthorized. Please generate a new access token.',404: 'The conversation and/or it\'s metadata you asked could not be found, please check the input provided',500: 'Something went wrong! Please contact support@symbl.ai'}
      time.sleep(120)
      sptxt_response = requests.request("GET", sptxt_url, headers=sptxt_header)
      if sptxt_response.status_code == 200:
          # Successful API execution
          print("messages => " + str(sptxt_response.json()['messages']))
          transcription=[]
          for value in sptxt_response.json()['messages']:
              transcription.append(value['text'].replace('u', ' ',1)) 
          print(transcription) # messages is a list of id, text, from, startTime, endTime, conversationId, words, phrases, sentiment
      elif sptxt_response.status_code in sptxt_responses.keys():
          print(sptxt_responses[sptxt_response.status_code])  # Expected error occurred
      else:
          print("Unexpected error occurred. Please contact support@symbl.ai" + ", Debug Message => " + str(response1.text))
      for i in transcription:
          pdf.cell(200, 10, txt = i,ln = transcription.index(i)+1, align = 'L')
      pdf.output("MeetingTranscription.pdf")   
      # Meeting Topics
      topics_baseUrl = "https://api.symbl.ai/v1/conversations/{conversationId}/topics"
      topics_url = topics_baseUrl.format(conversationId=conversationId)
      topics_headers = {'Authorization': 'Bearer ' + access_token,'Content-Type': 'application/json'}
      topics_params = {'sentiment': True, 'parentRefs': True, }
      topics_responses = {401: 'Unauthorized. Please generate a new access token.',404: 'The conversation and/or it\'s metadata you asked could not be found, please check the input provided',500: 'Something went wrong! Please contact support@symbl.ai'}
      topics_response = requests.request("GET", topics_url, headers=topics_headers, params=json.dumps(topics_params))
      if topics_response.status_code == 200:
          # Successful API execution
          print("topics => " + str(topics_response.json()['topics']))
          topics=[]
          for value in topics_response.json()['topics']:
              topics.append(value['text'].replace('u', ' ',1)) 
          print(topics)  # topics object containing topics id, text, type, score, messageIds, sentiment object, parentRefs
      elif topics_response.status_code in topics_responses.keys():
          print(topics_responses[topics_response.status_code])  # Expected error occurred
      else:
          print("Unexpected error occurred. Please contact support@symbl.ai" + ", Debug Message => " + str(response.text))
      #Action Items
      action_baseUrl = "https://api.symbl.ai/v1/conversations/{conversationId}/action-items"
      action_url = action_baseUrl.format(conversationId=conversationId)
      action_headers = {'Authorization': 'Bearer ' + access_token,'Content-Type': 'application/json'}
      action_responses = {401: 'Unauthorized. Please generate a new access token.',404: 'The conversation and/or it\'s metadata you asked could not be found, please check the input provided',500: 'Something went wrong! Please contact support@symbl.ai'}
      action_response = requests.request("GET", action_url, headers=action_headers)
      if action_response.status_code == 200:
          # Successful API execution
          print("actionItems => " + str(action_response.json()['actionItems']))
          actionItems=[]
          for value in action_response.json()['actionItems']:
              temptxt=value['text'].replace('u', ' ',1)
              print(temptxt)
              actionItems.append(temptxt) 
          print(actionItems)  # actionsItems object containing actionItem id, text, type, score, messageIds, phrases, definitive, entities, assignee
      elif action_response.status_code in action_responses.keys():
          print(action_responses[action_response.status_code])  # Expected error occurred
      else:
          print("Unexpected error occurred. Please contact support@symbl.ai" + ", Debug Message => " + str(response.text))
      followups_baseUrl = "https://api.symbl.ai/v1/conversations/{conversationId}/follow-ups"
      followups_url = followups_baseUrl.format(conversationId=conversationId)
      followups_headers = { 'Authorization': 'Bearer ' + access_token,'Content-Type': 'application/json'}
      followups_responses = {401: 'Unauthorized. Please generate a new access token.',404: 'The conversation and/or it\'s metadata you asked could not be found, please check the input provided', 500: 'Something went wrong! Please contact support@symbl.ai'}
      followups_response = requests.request("GET", followups_url, headers=followups_headers)
      if followups_response.status_code == 200:
          # Successful API execution
          print("followUps => " + str(followups_response.json()['followUps']))
          followUps=[]
          for value in followups_response.json()['followUps']:
              temptxt=value['text'].replace('u', ' ',1)
              print(temptxt)
              followUps.append(temptxt) 
          print(followUps)  # followUps object containing followUp id, text, type, score, messageIds, entities, from, assignee, phrases
      elif followups_response.status_code in followups_responses.keys():
          print(followups_responses[followups_response.status_code])  # Expected error occurred
      else:
          print("Unexpected error occurred. Please contact support@symbl.ai" + ", Debug Message => " + str(response.text))
      listToStr = '\n'.join(map(str, topics))
      print(listToStr) 
      actionToStr='\n'.join(map(str, actionItems))
      followUpsToStr='\n'.join(map(str,followUps))
      body = '''
Hi,
Here is the attached pdf file containing the transcription of your meeting.

Below topics are covered in the meeting:
'''+listToStr+"\n"+"\n"+"Following action items are generated from the meeting:"+"\n"+actionToStr+"\n"+"\n"+"Following follow-ups are generated from the meeting:"+"\n"+followUpsToStr
      # put your email here
      sender = request.form.get("semail")
      # get the password in the gmail (manage your google account, click on the avatar on the right)
      # then go to security (right) and app password (center)
      # insert the password and then choose mail and this computer and then generate
      # copy the password generated here
      password = request.form.get("spassword")
      # put the email of the receiver here
      receiver = request.form.get("remail")
      #Setup the MIME
      message = MIMEMultipart()
      message['From'] = sender
      message['To'] = receiver
      message['Subject'] = request.form.get("subject")
      message.attach(MIMEText(body, 'plain'))
      pdfname = 'MeetingTranscription.pdf'
      # open the file in bynary
      binary_pdf = open(pdfname, 'rb')
      payload = MIMEBase('application', 'octate-stream', Name=pdfname)
      # payload = MIMEBase('application', 'pdf', Name=pdfname)
      payload.set_payload((binary_pdf).read())
      # enconding the binary into base64
      encoders.encode_base64(payload)
      # add header with pdf name
      payload.add_header('Content-Decomposition', 'attachment', filename=pdfname)
      message.attach(payload)
      #use gmail with port
      session = smtplib.SMTP('smtp.gmail.com', 587)
      #enable security
      session.starttls()
      #login with mail_id and password
      session.login(sender, password)
      text = message.as_string()
      session.sendmail(sender, receiver, text)
      session.quit()
      print('Mail Sent')
      return render_template("mail.html",result = result)

if __name__ == '__main__':
   app.run(debug = True)