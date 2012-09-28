from ot.text_operation import *

import random


def random_char():
    """Generate a random lowercase ASCII character."""
    return chr(random.randint(97, 123))


def random_string(max_len=16):
    """Generate a random string."""

    s = ''
    for i in xrange(0, random.randint(0, max_len)):
        # append random lowercase ascii character
        s += random_char()
    return s


def random_operation(doc):
    """Generate a random operation that can be applied to the given string."""

    o = TextOperation()
    # Why can't Python 2 change variables in enclosing scope?
    i = [0]

    def gen_retain():
        r = random.randint(1, max_len)
        i[0] += r
        return Retain(r)

    def gen_insert():
        return Insert(random_char() + random_string(9))

    def gen_delete():
        d = random.randint(1, max_len)
        i[0] += d
        return Delete(d)

    while i[0] < len(doc):
        max_len = min(10, len(doc) - i[0])
        o.append(random.choice([gen_retain, gen_insert, gen_delete])())

    if random.random() < 0.5:
        o.append(gen_insert())

    return o


random_test_iterations = 64


def repeat(fn):
    """Decorator for running the function's body multiple times."""
    def repeated():
        i = 0
        while i < random_test_iterations:
            fn()
            i += 1
    # nosetest runs functions that start with 'test_'
    repeated.__name__ = fn.__name__
    return repeated


def test_append():
    o = TextOperation()
    o.append(Delete(0))
    o.append(Insert('lorem'))
    o.append(Retain(0))
    o.append(Insert(' ipsum'))
    o.append(Retain(3))
    o.append(Insert(''))
    o.append(Retain(5))
    o.append(Delete(8))
    assert len(o.ops) == 3
    assert o == TextOperation([
        Insert('lorem ipsum'),
        Retain(8),
        Delete(8)
    ])


@repeat
def test_len_difference():
    doc = random_string(50)
    operation = random_operation(doc)
    assert len(operation(doc)) - len(doc) == operation.len_difference()


def test_apply():
    doc = 'Lorem ipsum'
    o = TextOperation([Delete(1), Insert('l'), Retain(4), Delete(4), Retain(2), Insert('s')])
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
    assert a_prime(b(doc)) == b_prime(a(doc))
