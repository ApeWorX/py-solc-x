import pytest


class WrapperMock:
    """
    Simple mock for solcx.wrapper.solc_wrapper
    """

    def __call__(self, **kwargs):
        for key, value in self.kwargs.items():
            assert kwargs[key] == value
        return '{"contracts":{}}', "", [], 0

    def expect(self, **kwargs):
        self.kwargs = kwargs


@pytest.fixture
def wrapper_mock(monkeypatch):
    mock = WrapperMock()
    monkeypatch.setattr("solcx.wrapper.solc_wrapper", mock)
    yield mock
