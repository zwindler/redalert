# redalert

## goal of the project

RedAlert is a basic Slack bot to helps in **incident management** by using Slack channels.

RedAlert is inspired by the work described by ManoMano SRE team in [this blog post](https://medium.com/manomano-tech/incident-management-with-a-bot-7e80deb5b5e5). Unfortunatly, ManoMano's bot (FireFighter) is closed source for now (I've asked its author who confirmed it).

This project aims to provide an open source alternative.

## features

* open a channel, (TODO add a small description) and invite individuals (TODO or teams) in it
* configurable incident severity levels
* list all incident channels, (TODO) optionnaly also archived ones (closed incidents)
* close the incident by archiving the Slack channel

## possible future features

* add external persistance to store incidents in an external database to allow better analysis
* add **problem management** (linking incidents, adding tasks)
* interact with other systems like PagerDuty (create an incident to alert "on call" operator, Trello (tasks), Confluence (postmortems)

## prerequisites

* a Slack workspace with enough rights to add app and custom commands (???)
* a server capable of running Flask python webserver with Python 3.6+

## installation

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
