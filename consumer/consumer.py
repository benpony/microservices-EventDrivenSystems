import argparse
import logging
import sys
from argparse import RawTextHelpFormatter
from time import sleep

import pika


def on_message(channel, method_frame, header_frame, body):
    print(method_frame.delivery_tag)
    print(body)
    LOG.info('Message has been received %s', body)
    channel.basic_ack(delivery_tag=method_frame.delivery_tag)


if __name__ == '__main__':
    examples = sys.argv[0] + " -p 5672 -s rabbitmq "
    parser = argparse.ArgumentParser(
        formatter_class=RawTextHelpFormatter,
        description='Run consumer.py',
        epilog=examples
    )
    parser.add_argument(
        '-p',
        '--port',
        action='store',
        dest='port',
        help='The port to listen on.'
    )
    parser.add_argument(
        '-s',
        '--server',
        action='store',
        dest='server',
        help='The RabbitMQ server.'
    )

    args = parser.parse_args()
    if args.port == None:
        print("Missing required argument: -p/--port")
        sys.exit(1)
    if args.server == None:
        print("Missing required argument: -s/--server")
        sys.exit(1)

    logging.basicConfig(level=logging.INFO)
    LOG = logging.getLogger(__name__)
    credentials = pika.PlainCredentials('admin', 'admin')
    parameters = pika.ConnectionParameters(
        args.server,
        int(args.port),
        '/',
        credentials
    )
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare('pc')
    channel.basic_consume('pc',on_message)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    connection.close()
