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
  return make_response("", 200)

@app.route("/incident", methods=["POST"])
def incident():
  command_type = json.dumps(request.form["text"]).strip('"')
  command_origin = json.dumps(request.form["channel_name"]).strip('"')
  command_user_id = json.dumps(request.form["user_id"]).strip('"')
  command_trigger_id = json.dumps(request.form["trigger_id"]).strip('"')

  print(command_type)
  print(command_origin)
  print(command_user_id)
  print(command_trigger_id)

  if (command_type == "open"):
    print("Got open as 1st argument")

    open_dialog = slack_client.api_call(
      "dialog.open", 
      json={
        'trigger_id' : command_trigger_id,
        'dialog' : {
          "title": "Create an incident",
          "submit_label": "Submit",
          "callback_id": command_user_id + "incident_creation_form",
          "elements": [
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
                  "label": "Minor Alert",
                  "value": "minoralert"
                }
              ]
            }
          ]
        }
      }
    )

    print(open_dialog)
    response = slack_client.chat_postMessage(
      channel="#"+command_origin,
      text="Opening incident!")
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
