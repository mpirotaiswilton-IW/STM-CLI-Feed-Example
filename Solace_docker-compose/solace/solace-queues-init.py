import requests
import time
import json
import os

from requests.auth import HTTPBasicAuth


class Subscription:
    def __init__(self, topic):
        self.topic = topic


class Queue:
    # def __init__(self, name, msg_vpn_name,access_type, maxMsgSpoolUsage, permission, ingress_enabled, egress_enabled,
    #              subscribed_topics):
    #     self.name = name
    #     self.msg_vpn_name = msg_vpn_name
    #     self.access_type = access_type
    #     self.maxMsgSpoolUsage = maxMsgSpoolUsage
    #     self.permission = permission
    #     self.ingress_enabled = ingress_enabled
    #     self.egress_enabled = egress_enabled
    #     self.subscribed_topics = subscribed_topics

    def __init__(self, msg_vpn_name, attributes, subscribed_topics):
        self.msg_vpn_name = msg_vpn_name
        self.attributes = attributes
        self.subscribed_topics = subscribed_topics
    

r = requests.Response()
r.status_code = 400

max_connection_attempts = 5
connection_attempts = 0

max_retries_count = 5
retries_count = 0

dir_path = os.path.dirname(os.path.realpath(__file__))
json_file_path = dir_path + os.sep + "queues.json"

host_name = "solace"
port = "8080"

username = "admin"
password = "admin"

queues = []

try:
    with open(json_file_path, mode="r", encoding="utf-8") as read_file:
        print("file opening successful")
        json_data = json.load(read_file)
        print("json data assign successful")

    json_vars = [
        host_name,
        port,
        username,
        password
    ]

    keys = [
        "hostname",
        "port",
        "username",
        "password"
    ]

    print("assigning...")

    for i in range(len(keys)):
        # print(keys[i])
        try:
            json_vars[i] = json_data[keys[i]]
        except KeyError:
            print("the field " + keys[i] + " is not present in the json file")

    host_name = json_vars[0]
    port = json_vars[1]

    print("host acquired")
    print(host_name)
    print(port)

    username = json_vars[2]
    password = json_vars[3]

    for queue in json_data["queues"]:
        print(queue["attributes"]["queueName"])
        subscriptions = []
        for sub in queue["subscribed_topics"]:
            subscriptions.append(Subscription(sub["name"]))
        queues.append(
            Queue(
                msg_vpn_name=queue["msg_vpn_name"],
                attributes=queue["attributes"],
                subscribed_topics=subscriptions
            )
        )


except FileNotFoundError:
    print("error encountered parsing json file")

basic = HTTPBasicAuth(username, password)

while r.status_code != 200 and connection_attempts < max_connection_attempts:

    print("Attempting connection to Solace Event Broker...")
    try:
        r = requests.get(url="http://" + host_name + ":" + port + "/")
    except RuntimeError:
        if connection_attempts == max_connection_attempts:
            print("CRITICAL ERROR: Maximum number of connection attempts reached!")
            print("Exiting program...")
            exit(1)
        else:
            print("Connection Failed, retrying...")
            connection_attempts += 1
            time.sleep(1)


print("Connection successful!")

content_header = {'Content-Type': 'application/json'}

for queue in queues:

    print("Sending request to create queue: " + queue.attributes["queueName"])

    print("\n -------- \n")

    queue_req_payload = queue.attributes
    req_url = "http://" + host_name + ":" + port + "/SEMP/v2/config/msgVpns/" + queue.msg_vpn_name + "/queues"

    queue_req = requests.post(url=req_url, json=queue_req_payload, headers=content_header, auth=basic)

    print(queue_req.text)

    if queue_req.status_code == 200:

        queue_check = requests.get(
            url="http://" + host_name + ":" + port + "/SEMP/v2/config/msgVpns/" + queue.msg_vpn_name + "/queues/"
                + queue.attributes["queueName"], auth=basic)

        while queue_check.status_code != 200:
            print(queue_check.status_code)

            queue_check = requests.get(
                url="http://" + host_name + ":" + port + "/SEMP/v2/config/msgVpns/" + queue.msg_vpn_name + "/queues/"
                    + queue.attributes["queueName"], auth=basic)

        print("\n -------- \n")
        print("Queue creation successful! : " + queue.attributes["queueName"])

        for subscribed_topic in queue.subscribed_topics:
            print("Sending request to create subscribed topic: " + subscribed_topic.topic + " --- for queue: " + queue.attributes["queueName"])

            topic_req_payload = {
                'subscriptionTopic': subscribed_topic.topic
            }

            req_url = ("http://" + host_name + ":" + port + "/SEMP/v2/config/msgVpns/" + queue.msg_vpn_name + "/queues/"
                       + queue.attributes["queueName"] + "/subscriptions")

            topic_req = requests.post(url=req_url,
                                      json=topic_req_payload,
                                      headers=content_header,
                                      auth=basic)

            print(topic_req.text)

    else:

        print("Cannot Create Queue due to an Error: " + queue_req.status_code.__str__())


print("Queues and Topic creation finished")
