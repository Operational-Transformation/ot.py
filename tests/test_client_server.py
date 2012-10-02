from test_text_operation import random_string, random_operation
from helpers import repeat
import random

from ot.client import Client
from ot.server import MemoryBackend, Server


class MyClient(Client):
    def __init__(self, revision, id, document, channel):
        Client.__init__(self, revision)
        self.id = id
        self.document = document
        self.channel = channel

    def send_operation(self, revision, operation):
        self.channel.write((self.id, revision, operation))

    def apply_operation(self, operation):
        self.document = operation(self.document)

    def perform_operation(self):
        operation = random_operation(self.document)
        self.document = operation(self.document)
        self.apply_client(operation)


class NetworkChannel():
    """Mock a FIFO network connection."""

    def __init__(self, on_receive):
        self.buffer = []
        self.on_receive = on_receive

    def is_empty(self):
        return len(self.buffer) == 0

    def write(self, msg):
        self.buffer.append(msg)

    def read(self):
        return self.buffer.pop(0)

    def receive(self):
        return self.on_receive(self.read())


@repeat
def test_client_server_interaction():
    document = random_string()
    server = Server(document, MemoryBackend())

    def server_receive(msg):
        (client_id, revision, operation) = msg
        operation_p = server.receive_operation(client_id, revision, operation)
        msg = (client_id, operation_p)
        client1_receive_channel.write(msg)
        client2_receive_channel.write(msg)

    def client_receive(client):
        def rcv(msg):
            (client_id, operation) = msg
            if client.id == client_id:
                client.server_ack()
            else:
                client.apply_server(operation)
        return rcv

    client1_send_channel = NetworkChannel(server_receive)
    client1 = MyClient(0, 'client1', document, client1_send_channel)
    client1_receive_channel = NetworkChannel(client_receive(client1))

    client2_send_channel = NetworkChannel(server_receive)
    client2 = MyClient(0, 'client2', document, client2_send_channel)
    client2_receive_channel = NetworkChannel(client_receive(client2))

    channels = [
        client1_send_channel, client1_receive_channel,
        client2_send_channel, client2_receive_channel
    ]

    def can_receive():
        for channel in channels:
            if not channel.is_empty():
                return True
        return False

    def receive_random():
        filtered = []
        for channel in channels:
            if not channel.is_empty():
                filtered.append(channel)
        random.choice(filtered).receive()

    n = 64
    while n > 0:
        if not can_receive() or random.random() < 0.75:
            client = random.choice([client1, client2])
            client.perform_operation()
        else:
            receive_random()
        n -= 1

    while can_receive():
        receive_random()

    assert server.document == client1.document == client2.document
