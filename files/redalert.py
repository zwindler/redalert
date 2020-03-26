#!/usr/bin/python3
# -*- coding: utf-8 -*-
from flask import Flask, request, make_response, Response
import os
import json
import psycopg2
import sys

import slack

# Slack client for Web API requests
slack_client = slack.WebClient(token=os.environ['SLACK_BOT_TOKEN'])
#SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]

# Flask web server for incoming traffic from Slack
app = Flask(__name__)

# Backend route handling incident creation response
@app.route("/create", methods=["POST"])
def create():
  print(request.form)
  callback_payload = json.loads(request.form["payload"])
  command_user_id = callback_payload["user"]["id"]
  severity = callback_payload["submission"]["severity"]
  #print(severity)
  channel_origin = callback_payload["channel"]["name"]
  #print(channel_origin)
  incident_name = callback_payload["submission"]["incident_name"]
  #print(incident_name)
  incident_manager_id = callback_payload["submission"]["incident_manager"]
  #print(incident_manager)

  #Translate user ID as user name
  response = slack_client.users_profile_get(user = incident_manager_id)
  incident_manager_name = response["profile"]["real_name"]

  response = slack_client.chat_postMessage(
    channel="#"+channel_origin,
    text="Opening "+ severity +" in channel #"+ incident_name +", managed by "+ incident_manager_name +"!")
  assert response["ok"]

  return make_response("", 200)

@app.route("/incident", methods=["POST"])
def incident():
  #print(request.form)
  command_type = request.form["text"]
  #print(command_type)
  command_user_id = request.form["user_id"]
  #print(command_user_id)
  command_trigger_id = request.form["trigger_id"]
  #print(command_trigger_id)

  if (command_type == "open"):
    print("Got open as 1st argument")

    #print("Get users list")
    #users = {}
    #users_list_output = slack_client.users_list()
    #for user in users_list_output["members"]:
    #   users[user["id"]]=user["name"]

    response = slack_client.api_call(
      "dialog.open", 
      json={
        'trigger_id' : command_trigger_id,
        'dialog' : {
          "title": "Create an incident",
          "submit_label": "Submit",
          "callback_id": command_user_id + "_incident_creation_form",
          "elements": [
            {
              "type": "text",
              "label": "Incident name",
              "name": "incident_name"
            },
            {
              "label": "Incident severity",
              "type": "select",
              "name": "severity",
              "placeholder": "Select incident severity",
              "options": [
                {
                  "label": "Red Alert",
                  "value": "redalert"
                },
                {
                  "label": "Yellow Alert",
                  "value": "yellowalert"
                },
                {
                  "label": "Announcement",
                  "value": "announcement"
                }
              ]
            },
            {
              "label": "Incident manager",
              "name": "incident_manager",
              "type": "select",
              "data_source": "users"
            }
          ]
        }
      }
    )
    assert response["ok"]

  elif (command_type == "close"):
    print("Got close as 1st argument")
    response = slack_client.chat_postMessage(
      channel="#alerts",
      text="Closing incident!")
    assert response["ok"]
  else:
    response = slack_client.chat_postMessage(
      channel="#alerts",
      text="Wrong command, only type '/incident open' or '/incident close')")
    assert response["ok"]

  return make_response("", 200)    

def main():
  app.run(host='0.0.0.0', port=3000)
  sys.exit()

if __name__ == '__main__':
  main()
