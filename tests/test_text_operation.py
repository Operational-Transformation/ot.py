from ot.text_operation import *
from helpers import repeat

import random


def random_char():
    """Generate a random lowercase ASCII character."""
    return chr(random.randint(97, 123))


def random_string(max_len=16):
    """Generate a random string."""

    s = ''
    s_len = random.randint(0, max_len)
    while s_len > 0:
        s += random_char()
        s_len -= 1
    return s


def random_operation(doc):
    """Generate a random operation that can be applied to the given string."""

    o = TextOperation()
    # Why can't Python 2 change variables in enclosing scope?
    i = [0]

    def gen_retain():
        r = random.randint(1, max_len)
        i[0] += r
        o.retain(r)

    def gen_insert():
        o.insert(random_char() + random_string(9))

    def gen_delete():
        d = random.randint(1, max_len)
        i[0] += d
        o.delete(d)

    while i[0] < len(doc):
        max_len = min(10, len(doc) - i[0])
        random.choice([gen_retain, gen_insert, gen_delete])()

    if random.random() < 0.5:
        gen_insert()

    return o


def test_append():
    o = TextOperation()
    o.delete(0)
    o.insert('lorem')
    o.retain(0)
    o.insert(' ipsum')
    o.retain(3)
    o.insert('')
    o.retain(5)
    o.delete(8)
    assert len(o.ops) == 3
    assert o == TextOperation(['lorem ipsum', 8, -8])


@repeat
def test_len_difference():
    doc = random_string(50)
    operation = random_operation(doc)
    assert len(operation(doc)) - len(doc) == operation.len_difference()


def test_apply():
    doc = 'Lorem ipsum'
    o = TextOperation().delete(1).insert('l').retain(4).delete(4).retain(2).insert('s')
    assert o(doc) == 'loremums'


@repeat
def test_invert():
    doc = random_string(50)
    operation = random_operation(doc)
    inverse = operation.invert(doc)
    assert doc == inverse(operation(doc))


@repeat
def test_compose():
    doc = random_string(50)
    a = random_operation(doc)
    doc_a = a(doc)
    b = random_operation(doc_a)
    ab = a.compose(b)
    assert b(doc_a) == ab(doc)


@repeat
def test_transform():
    doc = random_string(50)
    a = random_operation(doc)
    b = random_operation(doc)
    (a_prime, b_prime) = TextOperation.transform(a, b)
    assert a + b_prime == b + a_prime
    assert a_prime(b(doc)) == b_prime(a(doc))
