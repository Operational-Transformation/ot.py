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
