# redalert

## goal of the project

RedAlert is a basic slack bot to help incident management by using slack channels.

RedAlert is inspired by the work described by ManoMano teams in [this blog post](https://medium.com/manomano-tech/incident-management-with-a-bot-7e80deb5b5e5). Unfortunatly, ManoMano's bot (FireFighter) is closed source for now (I've asked its author).

This project aims to provide an open source equivalent.

## features

* open a channel and invite individuals (TODO or teams) in it
* (TODO) list all incident channels, optionnaly also archived ones
* (TODO) close the incident by archiving the slack channel

## possible future features

* add external persistance to store incidents in a database
* add problem management (linking incidents)
* interact with other systems like PagerDuty or Confluence (for PostMortems)

## prerequisites

* slack with admin rights (to add app)
* a server capable of running Flask python webserver with Python 3.6+

## installation

Add the App in you Slack administration

(TODO explain this)

On Ubuntu 18.04

````bash
apt install python3-pip
pip3 install flask slackclient
```

Get the sources

````bash
git clone https://github.com/zwindler/redalert && cd redalert
```

Export SLACK\_BOT\_TOKEN variable (with the value found in the Slack Apps page) and run redalert.py

```bash
export SLACK_BOT_TOKEN=xoxb-xxxx-xxxx-xxxx
```
