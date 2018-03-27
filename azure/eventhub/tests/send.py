#!/usr/bin/env python

"""
send test
"""

import logging
import argparse
import time
import threading
import utils
from azure.eventhub import EventHubClient, Sender, EventData

logger = utils.get_logger("send_test.log", logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument("--duration", help="Duration in seconds of the test", type=int, default=3600)
parser.add_argument("--payload", help="payload size", type=int, default=512)
parser.add_argument("--batch", help="Number of events to send and wait", type=int, default=1)
parser.add_argument("--conn-str", help="EventHub connection string")
parser.add_argument("--eventhub", help="Name of EventHub")
parser.add_argument("--address", help="Address URI to the EventHub entity")
parser.add_argument("--sas-policy", help="Name of the shared access policy to authenticate with")
parser.add_argument("--sas-key", help="Shared access key")


def check_send_successful(outcome, condition):
    if outcome.value != 0:
        print("Send failed {}".format(condition))


def main(address, policy, key):
    client = EventHubClient(address, username=policy, password=key)
    sender = client.add_sender()
    client.run()
    deadline = time.time() + args.duration
    total = 0

    def data_generator():
        for i in range(args.batch):
            yield b"D" * args.payload

    if args.batch > 1:
        print("Sending batched messages")
    else:
        print("Sending single messages")

    try:
        while time.time() < deadline:
            if args.batch > 1:
                data = EventData(batch=data_generator())
            else:
                data = EventData(body=b"D" * args.payload)
            sender.transfer(data, callback=check_send_successful)
            total += args.batch
            if total % 5000 == 0:
               sender.wait()
               print("Send total {}".format(total))
    except Exception as err:
        print("Send failed {}".format(err))
    finally:
        client.stop()
    print("Sent total {}".format(total))


if __name__ == '__main__':
    args = parser.parse_args()
    entity = None
    if args.conn_str:
        address, policy, key, entity = utils.parse_conn_str(args.conn_str)
    elif args.address:
        address = args.address
        policy = args.sas_policy
        key = args.sas_key
    else:
        raise ValueError("Must specify either '--conn-str' or '--address'")
    entity = entity or args.eventhub
    address = utils.build_uri(address, entity)

    try:
        main(address, policy, key)
    except KeyboardInterrupt:
        pass
