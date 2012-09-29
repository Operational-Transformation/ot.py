class Server(object):
    """Receives operations from clients, transforms them against all
    concurrent operations and sends them back to all clients.
    """

    def __init__(self, document, operations=[]):
        self.document = document
        self.operations = operations[:]

    def receive_operation(self, revision, operation):
        """Transforms an operation coming from a client against all concurrent
        operation, applies it to the current document and returns the operation
        to send to the clients.
        """

        Operation = operation.__class__

        concurrent_operations = self.operations[revision:]
        for concurrent_operation in concurrent_operations:
            (operation, _) = Operation.transform(operation, concurrent_operation)

        self.document = operation(self.document)
        self.operations.append(operation)
        return operation
