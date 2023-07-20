import os
import pytest
import shutil
from app.domain.fileUpload import _save_file_to_server as sfs

import mock


mock_uploaded_file = mock.Mock()
mock_uploaded_file.file = open("./test.png", "rb")

def test_save_file_to_server():
    uploaded_file = mock_uploaded_file
    path = "./"
    save_as = "test.png"

    # Act
    actual_file = sfs(uploaded_file, path, save_as)

    # Assert
    assert os.path.exists(actual_file)
 
