from ot.server import MemoryBackend, Server
from ot.text_operation import TextOperation
from test_text_operation import random_string, random_operation


def test_MemoryBackend():
    backend = MemoryBackend()
    assert backend.operations == []
    backend = MemoryBackend([1, 2, 3])
    assert backend.operations == [1, 2, 3]
    assert backend.get_last_revision_from_user('user1') == None
    backend.save_operation('user1', 4)
    assert backend.operations == [1, 2, 3, 4]
    assert backend.get_last_revision_from_user('user1') == 3
    assert backend.get_operations(0) == [1, 2, 3, 4]
    assert backend.get_operations(2) == [3, 4]
    assert backend.get_operations(2, 3) == [3]


def test_Server():
    backend = MemoryBackend()
    doc = random_string()
    server = Server(doc, backend)
    assert server.document == doc
    assert server.backend == backend

    op1 = random_operation(doc)
    doc1 = op1(doc)
    assert server.receive_operation('user1', 0, op1) == op1
    assert server.document == doc1
    assert backend.operations == [op1]

    op2 = random_operation(doc1)
    doc2 = op2(doc1)
    assert server.receive_operation('user1', 1, op2) == op2
    assert backend.operations == [op1, op2]
    assert server.document == doc2

    server.receive_operation('user1', 1, op2) == None
    assert backend.operations == [op1, op2]
    assert server.document == doc2

    op2_b = random_operation(doc1)
    (op2_b_p, op2_p) = TextOperation.transform(op2_b, op2)
    assert server.receive_operation('user2', 1, op2_b) == op2_b_p
    assert backend.operations == [op1, op2, op2_b_p]
    assert server.document == op2_p(op2_b(doc1))
