

from flask import Flask, request, make_response, Response
import os
import json

from slackclient import SlackClient
from pyzabbix.api import ZabbixAPI


# Your app's Slack bot user token
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]

ZABBIX_URL = os.environ["ZABBIX_URL"]
ZABBIX_USER = os.environ["ZABBIX_USER"]
ZABBIX_PASSWORD = os.environ["ZABBIX_PASSWORD"]

# Slack client for Web API requests
slack_client = SlackClient(SLACK_BOT_TOKEN)

# Flask webserver for incoming traffic from Slack
app = Flask(__name__)


# Helper for verifying that requests came from Slack
def verify_slack_token(request_token):
    if SLACK_VERIFICATION_TOKEN != request_token:
        print("Error: invalid verification token!")
        print("Received {} but was expecting {}".format(request_token, SLACK_VERIFICATION_TOKEN))
        return make_response("Request contains invalid Slack verification token", 403)


# The endpoint Slack will send message actions
@app.route("/slack/message_actions", methods=["POST"])
def message_actions():

    # Parse the request payload
    form_json = json.loads(request.form["payload"])

    # Verify that the request came from Slack
    verify_slack_token(form_json["token"])

    zabbix_event_id = form_json["original_message"]["attachments"][0]["actions"][0]["value"]

    # Create ZabbixAPI class instance
    zapi = ZabbixAPI(url=ZABBIX_URL, user=ZABBIX_USER, password=ZABBIX_PASSWORD)

    # Try to acknowledge Event
    ack_result = zapi.do_request('event.acknowledge',
                              {
                                  'eventids': [zabbix_event_id],
                                  "action": 2,
                                  "message": "Problem acknowledged by username"
                              })
    if "error" in ack_result:
        return make_response("Fail to acknowledge event by zabbix api: {}".format(ack_result.has_key["error"]), 500)
    # Logout from Zabbix
    zapi.user.logout()

    # Check to see what the user's selection was and update the message accordingly
    attachments = form_json["original_message"]["attachments"][0]
    attachments["actions"] = []
    attachments["text"] += "\n *Already acknowledged by* <@{}>".format(form_json["user"]["id"])

    response = slack_client.api_call(
      "chat.update",
      channel=form_json["channel"]["id"],
      ts=form_json["message_ts"],
      text=form_json["original_message"]["text"],
      attachments=[attachments]  # rewrite `attachments` for replace acknowledge button to person who ack message
    )
    # Send an HTTP 200 response with empty body so Slack knows we're done here
    return make_response("", 200)


# Start the Flask server
if __name__ == "__main__":
    app.run(host='0.0.0.0')
