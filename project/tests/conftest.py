import os

import pytest
from starlette.testclient import TestClient

from app.main import create_application

from app.config import get_settings, Settings


def get_settings_override():
    return Settings(testing=1)

@pytest.fixture(scope="module")
def test_app():
    # set up
    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override
    with TestClient(app) as test_client:
        # testing
        yield test_client

    # tear down