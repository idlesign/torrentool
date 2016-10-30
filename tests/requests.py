# This is a stab file to mock `requests` package and some of its contents for tests.


class ResponseMock(object):

    def __init__(self, text):
        self.text = text

    def raise_for_status(self):
        if self.text is None:
            raise ImportError('Mock exception')


class RequestException(Exception):
    pass


def get():
    pass


def post():
    pass
