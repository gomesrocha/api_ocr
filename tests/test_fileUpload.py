import os
import pytest
from unittest.mock import Mock
from app.domain.fileUpload import _save_file_to_server as sfs

@pytest.fixture
def mock_upload_file(tmp_path):
    # Create a dummy file
    file_path = tmp_path / "test.png"
    file_path.write_bytes(b"test data")

    mock_file = Mock()
    mock_file.filename = "test.png"
    mock_file.file = open(file_path, "rb")

    yield mock_file

    mock_file.file.close()

def test_save_file_to_server(mock_upload_file):
    # Act
    actual_file = sfs(mock_upload_file)

    # Assert
    assert os.path.exists(actual_file)
    assert actual_file.endswith("test.png")

    # Check content matches
    with open(actual_file, "rb") as f:
        content = f.read()
    assert content == b"test data"

    # Cleanup
    try:
        os.remove(actual_file)
    except OSError:
        pass
