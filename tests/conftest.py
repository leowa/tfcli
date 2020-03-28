
import pytest


@pytest.fixture(scope='function')
def hello(request):
    return "hello"
