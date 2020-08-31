from requests.cookies import MockRequest


class MockResponse(object):

    def __init__(self, headers):
        self._headers = headers

    def info(self):
        return self

    def getheaders(self, name):
        return self._headers.get_list(name)

    def get_all(self, name, default=None):
        if default is None:
            default = []
        return self._headers.get_list(name) or default


def extract_cookies_to_jar(jar, request, response):
    req = MockRequest(request)
    res = MockResponse(response)
    reveal_type(jar)