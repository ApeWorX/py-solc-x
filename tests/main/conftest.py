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


class CompileCombinedJsonMock:
    """
    Simple mock for solcx.main._compile_combined_json
    """

    def __call__(self, **kwargs):
        for key, value in self.kwargs.items():
            assert kwargs[key] == value
        return {}

    def expect(self, **kwargs):
        self.kwargs = kwargs


@pytest.fixture
def compile_combined_json_mock(monkeypatch):
    mock = CompileCombinedJsonMock()
    monkeypatch.setattr("solcx.main._compile_combined_json", mock)
    yield mock
