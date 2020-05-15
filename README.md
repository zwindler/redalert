# redalert

## Goal of the project

RedAlert is a basic Slack bot to helps in **incident management** by using Slack channels. It's nowhere as complete as [Netflix' "Dispatch"](https://github.com/Netflix/dispatch) incident manager, nor does it aims to be.

RedAlert is inspired by the work described by ManoMano SRE team in [this blog post](https://medium.com/manomano-tech/incident-management-with-a-bot-7e80deb5b5e5). Unfortunatly, ManoMano's bot (FireFighter) is closed source for now (I've asked its author who confirmed it).

This project aims to provide an open source alternative.

## Features

* open a channel, add a small description (optionnal) and (optionnaly) invite individuals in it
* configurable incident severity levels
* automatically add individuals in some or every incidents (configurable)
* list all incident channels, optionnaly also archived ones (aka closed incidents)
* close the incident by archiving the Slack channel

## Future features

* A Slack App (one click install instead of the whole "Slack administration" chapter)
* add external persistance to store incidents in an external database to allow better analysis
* add **problem management** (linking incidents, adding tasks)
* interact with other systems like:
  * PagerDuty (create an incident to alert "on call" operator)
  * Trello (tasks)
  * Confluence (postmortems)
  * ...
* pick multiple individuals in incident creation dialog ([not technically possible yet](https://stackoverflow.com/questions/48523512/slack-interactive-message-menu-select-multiple))
* custom config file that overrides the default values from config.py

## Prerequisites

* a Slack workspace with enough rights to add an app and custom commands
* a server capable of running Flask python webserver with Python 3.6+ *or* a Docker image

## Slack administration

The Slack App is not yet packaged for Slack easy installation. For now, you will have to create the App yourself.

Add a new App in you Slack administration page ([api.slack.com/apps](https://api.slack.com/apps)).

![Create the App](binaries/1_slack_your_apps_redalert.png)

Once the App is created, you will see something like this.

![In Basic Information](binaries/2_slack_your_apps_redalert_basic_info.png)

Click on the "Slash Commands" menu to add a new *Slash Command*. It will allow us to communicate with the future Python App that we will deploy in the next chapter and send commands to it.

`/incident` is a suggestion but you can put anything (/redalert, etc). What really matters is that the *Request URL* parameters *has to* point to `https://[your-redalert-webserver]/incident` URL.

![Create Slash Command](binaries/3_slack_api_create_slash_command.png)

Once this is done, enable "Interactivity" in the main App page. This will allow us to open up dialogs, when you type `/incident open` for example.

Once again, the URL pattern is important there. The URL has to point to your python webserver and **has to** finish by "/dialog".

![Add interactivity](binaries/4_slack_api_interactivity.png)

This step is optionnal but having a nice looking App is always better in my opinion. You can customize the App by adding a Icon and some description.

![Add Icon](binaries/6_slack_api_basic_info_Add_Icon.png)

![Add Icon result](binaries/6_slack_api_basic_info_Add_Icon2.png)

The last thing we have to do is to configure authorizations for your app/slack bot. This is done in the **OAuth & Permissions** menu.

The following permissions are the **very least permissions** that you have to give to the bot to make it work.

* **channels:join** to allow redalert bot to join the public channel from which you will call the `/incident` commands
* **channels:manage** to allow redalert to open channels
* **channels:read** to list channels and thus respond to the `/incident list` command
* **chat:write** to write small messages in response to commands
* **commands** automatically added when you added the slash command
* **users.profile:read** to translate IDs in user names

Note: if you want to use redalert in private channels or group conversations, you will have to add more permissions.

![OAuth app scope](binaries/5_slack_api_oauth_bot_scode.png)

Now the App is finished from the Slack Administration App page point of view. You can now deploy it in your Slack workspace.

Note: should you change the permissions, you will have to redeploy it.

![Install App in your Workspace](binaries/7_slack_api_install_app.png)

![Install App in your Workspace](binaries/8_slack_api_install2.png)

The very last step it to get the **Slack Bot Token** which will be required by our Python webapp to authenticate in your Slack workspace.

![Get Bot Token for next steps](binaries/9_slack_api_redalert_bot_token.png)

## Backend App deployment

On Ubuntu 18.04

```bash
apt install python3-pip
pip3 install flask slackclient
```

Get the sources

```bash
git clone https://github.com/zwindler/redalert && cd redalert
```

Export SLACK\_BOT\_TOKEN variable (with the value found in the Slack Apps page) and run redalert.py

```bash
export SLACK_BOT_TOKEN=xoxb-xxxx-xxxx-xxxx
./redalert.py
```

## Docker image

As an alternative, you can also run or build yourself the Docker image of the redalert flask app

### Build it yourself and run it

Inside redalert repository, simply run `docker build`

```bash
docker build -t redalert .
docker run -it -e SLACK_BOT_TOKEN=xoxb-your-own-slack-bot-token redalert
```

### Run it from official image

```bash
docker run -it -e SLACK_BOT_TOKEN=xoxb-your-own-slack-bot-token zwindler/redalert
```

## Configure redalert

redalert comes with some small level of customisation, including for now only the various incident severity levels (more features coming soon, see **features** chapter).

To customize it, you can either :

* override the whole `config.py` configuration file coming with the repo by modifying it
* or with a docker mount over the file (if you chose Docker to run it)

```bash
docker run -it -e SLACK_BOT_TOKEN=xoxb-your-own-slack-bot-token -v custom_config.py:/home/redalert/custom_config.py zwindler/redalert
```

The `config.py` file is a standard Flask configuration file. It allows multiple configurations, including a default one for all your environments and a system of overrides [described here](https://flask.palletsprojects.com/en/1.1.x/config/).

For now, the only configurable part are :

### Severity levels

The severity levels can be configured through the **SEVERITY_LEVELS** variable. You can modify the `config.py` file like this for example:

```python
class Config(object):
    # Alternative Star Trek(tm) inspired alert levels
    SEVERITY_LEVELS = [
        {
            "label": "Red Alert",
            "value": "redalert"
        },
        {
            "label": "Yellow Alert",
            "value": "yellowalert"
        },
        {
            "label": "Captain Announcement",
            "value": "announcement"
        }
    ]
```

Note: you cannot use "always" as a value for the severity levels

### Always include some individuals in the incident

Depending on the severity of the incident, you can decide to always add some individual (through their slack user ID).

The "always" code means that no matter the severity, this contact will always be included in the incident, in addition to the IDs added afterward in the various severities.

The following labels (sev1, sev2, ...) have to correspond to actual severity levels, as configured in the `INCLUDE_IN_INCIDENT` variable.

The values are user comma separated user lists like in this example:

```python
class Config(object):
    INCLUDE_IN_INCIDENT = {
        "always" : ["U010PPYMH33"],
        "sev1" : ["U0105K7EFNX", "U0xxxxxxxx"],
        "sev2" : ["U0105K7EFNX"],
        "sev3" : [],
        "sev4" : [],
        "sev5" : []
    }
```

Note: the UserIDs HAVE TO exist in your Slack workspace or the webapp will crash.
