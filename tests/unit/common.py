from unittest.mock import MagicMock


class MockSession(MagicMock):

    async def __aenter__(self, a, b):
        return self

    def __aexit__(self):
        return self
