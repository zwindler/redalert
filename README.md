# redalert

## Goal of the project

RedAlert is a basic Slack bot to helps in **incident management** by using Slack channels. It's nowhere as complete as [Netflix' "Dispatch"](https://github.com/Netflix/dispatch) incident manager, nor does it aims to be.

RedAlert is inspired by the work described by ManoMano SRE team in [this blog post](https://medium.com/manomano-tech/incident-management-with-a-bot-7e80deb5b5e5). Unfortunatly, ManoMano's bot (FireFighter) is closed source for now (I've asked its author who confirmed it).

This project aims to provide an open source alternative.

## Features

* open a channel, add a small description and invite individuals in it
* configurable incident severity levels
* automatically add individuals or teams (configurable)
* list all incident channels, optionnaly also archived ones (aka closed incidents)
* close the incident by archiving the Slack channel

## Future features

* better documentation
* add tests to check if configuration is valid
* add external persistance to store incidents in an external database to allow better analysis
* add **problem management** (linking incidents, adding tasks)
* interact with other systems like:
  * PagerDuty (create an incident to alert "on call" operator)
  * Trello (tasks)
  * Confluence (postmortems)
  * ...
* add multiple individuals at incident creation ([not possible yet?](https://stackoverflow.com/questions/48523512/slack-interactive-message-menu-select-multiple))
* custom config file that overrides the default values from config.py

## Prerequisites

* a Slack workspace with enough rights to add app and custom commands (???)
* a server capable of running Flask python webserver with Python 3.6+

## Manual installation

Add the App in you Slack administration

(TODO explain this)

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

## Configure it

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

The following labels (sev1, sev2, ...) have to correspond to actual severity levels, as configured in the `SEVERITY_LEVELS` variable.

The values are user comma separated user lists like in this example:

```python
class Config(object):
    INCLUDE_IN_INCIDENT = {
        "always" : "U010PPYMH33",
        "sev1" : "U0105K7EFNX,U0xxxxxxxx",
        "sev2" : "U0105K7EFNX",
        "sev3" : [],
        "sev4" : [],
        "sev5" : []
    }
```
