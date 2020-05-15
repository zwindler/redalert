# !/usr/bin/python3
#  -*- coding: utf-8 -*-
from flask import Flask, request, make_response, Response
from datetime import datetime
import os
import json
import sys
import re

import slack

#  Slack client for Web API requests
slack_client = slack.WebClient(token=os.environ['SLACK_BOT_TOKEN'])

#  Flask web server for incoming traffic from Slack
app = Flask(__name__)
app.config.from_object("config.Config")

#  Default route handling liveness/readiness response
@app.route("/", methods=["GET"])
def root():
    return make_response("", 200)

#  Backend route handling dialog response
@app.route("/dialog", methods=["POST"])
def create():
    # print(request.form)
    callback_payload = json.loads(request.form["payload"])
    command_user_id = callback_payload["user"]["id"]
    slack_domain = callback_payload["team"]["domain"]
    origin_channel_name = callback_payload["channel"]["name"]
    origin_channel_id = callback_payload["channel"]["id"]
    incident_name = callback_payload["submission"]["incident_name"]
    incident_manager_id = callback_payload["submission"]["incident_manager"]
    severity = callback_payload["submission"]["severity"]
    incident_desc = callback_payload["submission"]["incident_desc"]

    # Get severity nice name
    severity_label = get_severity_pretty_name(severity)

    # Generate a unique incident channel name
    now = datetime.now()
    date_time = now.strftime("%Y%m%d-%H%M")
    incident_channel_name = severity+"-"+incident_name+"-"+date_time

    # Create channel
    response = slack_client.conversations_create(name=incident_channel_name)
    incident_channel_id = response["channel"]["id"]
    assert response["ok"]

    # Translate user ID as user name for user friendly message
    response = slack_client.users_profile_get(user=incident_manager_id)
    incident_manager_name = response["profile"]["real_name"]

    # List invited users
    user_ids_string = get_invited_users(command_user_id, incident_manager_id,
                                        severity)
    print(user_ids_string)

    # Add a purpose to the incident
    response = slack_client.conversations_setPurpose(
                   channel=incident_channel_id,
                   purpose=incident_desc)
    assert response["ok"]

    # Invite people in it
    # TODO: check if there are less than 1000 invites (max)
    response = slack_client.conversations_invite(channel=incident_channel_id,
                                                 users=user_ids_string)
    assert response["ok"]

    # Join command origin channel if not yet in it
    response = slack_client.conversations_join(channel=origin_channel_id)
    assert response["ok"]

    # Display a message with link to incident and incident master
    response = slack_client.chat_postMessage(
        channel="# "+origin_channel_name,
        text="Opening " + severity_label + " incident in channel <https://"
        + slack_domain + ".slack.com/archives/" + incident_channel_id
        + "|#" + incident_channel_name
        + ">, managed by <https://app.slack.com/team/" + incident_manager_id
        + "|" + incident_manager_name + ">!")
    assert response["ok"]

    return make_response("", 200)


# backend for /incident command management
@app.route("/incident", methods=["POST"])
def incident_command():
    # print(request.form)
    command_args = request.form["text"].split()
    command_type = command_args[0]
    command_user_id = request.form["user_id"]
    command_user_name = request.form["user_name"]
    command_trigger_id = request.form["trigger_id"]
    slack_domain = request.form["team_domain"]
    origin_channel_name = request.form["channel_name"]
    origin_channel_id = request.form["channel_id"]

    # Join command origin channel if not yet in it
    response = slack_client.conversations_join(channel=origin_channel_id)
    assert response["ok"]

    if (command_type == "open"):
        open_incident(slack_client, command_trigger_id, command_user_id)
        return make_response("", 200)
    elif (command_type == "list"):
        list_incident(slack_client, command_args, slack_domain,
                      origin_channel_name)
        return make_response("", 200)
    elif (command_type == "close"):
        close_incident(slack_client, origin_channel_name, origin_channel_id,
                       command_user_name, command_user_id)
        return make_response("", 200)
    else:
        # Wrong command argument
        response = slack_client.chat_postMessage(
            channel="# "+origin_channel_name,
            text="Wrong command, only type '/incident open', \
            '/incident list' or '/incident close')")
        assert response["ok"]
        return make_response("", 404)


def get_severity_pretty_name(severity):
    for level in app.config["SEVERITY_LEVELS"]:
        if level["value"] == severity:
            severity_label = level["label"]
            return severity_label


def get_invited_users(command_user_id, incident_manager_id, severity):
    include_in_incident = app.config["INCLUDE_IN_INCIDENT"]
    user_ids = []
    user_ids_string = ""

    # Start adding people in the list
    user_ids.append(command_user_id)

    if incident_manager_id != command_user_id:
        user_ids.append(incident_manager_id)

    if include_in_incident["always"] != []:
        user_ids.append(include_in_incident["always"])

    if include_in_incident[severity]:
        user_ids.append(include_in_incident[severity])

    # Dedupe invited users list
    user_ids = list(dict.fromkeys(user_ids))
    for user_id in user_ids:
        user_ids_string += user_id+","

    return user_ids_string


def channel_match_pattern(channel):
    for level in app.config["SEVERITY_LEVELS"]:
        if re.match("^" + level["value"], channel['name']):
            return True
    return False


def open_incident(slack_client, command_trigger_id, command_user_id):
    # Push a dialog, callback will be done on /dialog
    response = slack_client.api_call(
        "dialog.open",
        json={
            'trigger_id': command_trigger_id,
            'dialog': {
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
                        "options": app.config["SEVERITY_LEVELS"]
                    },
                    {
                        "label": "Incident manager",
                        "name": "incident_manager",
                        "type": "select",
                        "data_source": "users"
                    },
                    {
                        "label": "Brief description of the incident",
                        "name": "incident_desc",
                        "type": "textarea",
                        "hint": "A brief description of the incident."
                    }
                ]
            }
        }
    )
    assert response["ok"]


def list_incident(slack_client, command_args, slack_domain,
                  origin_channel_name):
    incident_dict = {}

    # Check if we also want to list closed incidents
    exclude_archived = "true"
    if len(command_args) > 1 and command_args[1] == 'all':
        exclude_archived = "false"

    # TODO cleanup this part of the code
    # Get the channel list
    response = slack_client.conversations_list(
        exclude_archived=exclude_archived,
        limit=100
    )
    for channel in response['channels']:
        if channel_match_pattern(channel):
            if channel['is_archived']:
                incident_dict[channel['id']] = "~"+channel['name']+"~"
            else:
                incident_dict[channel['id']] = channel['name']

    # Deal with pagination
    while response['response_metadata']['next_cursor'] != '':
        # Get the channel list
        response = slack_client.conversations_list(
            exclude_archived=exclude_archived,
            cursor=response['response_metadata']['next_cursor'],
            limit=100
        )
        for channel in response['channels']:
            if channel_match_pattern(channel):
                if channel['is_archived']:
                    incident_dict[channel['id']] = "~"+channel['name']+"~"
                else:
                    incident_dict[channel['id']] = channel['name']

    if exclude_archived == "false":
        incident_list_string = 'Listing ALL incidents (including closed):\n'
    else:
        incident_list_string = 'Listing incidents:\n'
    # Generate a user friendly list
    for current_channel_id, current_channel_name in incident_dict.items():
        incident_list_string += "- <https://" + slack_domain \
            + ".slack.com/archives/" + current_channel_id + "|# " \
            + current_channel_name + ">\n"

    # Display a message listing incidents
    response = slack_client.chat_postMessage(
        channel="#" + origin_channel_name,
        text=incident_list_string
    )
    assert response["ok"]


def close_incident(slack_client, origin_channel_name, origin_channel_id,
                   command_user_name, command_user_id):
    current_channel = {}
    current_channel['name'] = origin_channel_name
    if not channel_match_pattern(current_channel):
        response = slack_client.chat_postMessage(
            channel="#" + origin_channel_name,
            text="Unable to archive this channel, it's not an incident."
        )
        assert response["ok"]
    else:
        # Display a message explicitly saying incident is closed
        # and by whom
        response = slack_client.chat_postMessage(
            channel="#" + origin_channel_name,
            text="<https://app.slack.com/team/" + command_user_id
            + "|" + command_user_name + "> closed this incident."
        )
        assert response["ok"]

        response = slack_client.conversations_archive(
            channel=origin_channel_id
        )
        assert response["ok"]


def main():
    app.run(host='0.0.0.0', port=3000)
    sys.exit()


if __name__ == '__main__':
    main()
