import boto3
import tempfile
import os
import logging
from botocore.exceptions import ClientError
from app.core.tenants import get_tenant_config

log = logging.getLogger("uvicorn")

def download_file_from_storage(client_id: str, object_key: str) -> str:
    """
    Downloads a file from object storage to a temporary file.

    Args:
        client_id (str): The tenant identifier.
        object_key (str): The path to the file in the bucket.

    Returns:
        str: The path to the downloaded temporary file.

    Raises:
        ValueError: If tenant configuration is missing.
        ClientError: If S3 interaction fails (e.g. file not found).
    """
    config = get_tenant_config(client_id)
    if not config:
        raise ValueError(f"Configuration for client {client_id} not found.")

    try:
        # Determine file extension if possible
        suffix = os.path.splitext(object_key)[1]

        # Create a temporary file (not automatically deleted on close, we delete it later)
        # Using delete=False so we can return the path and use it.
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            log.info(f"Downloading {object_key} for client {client_id} from {config.endpoint_url or 'AWS S3'}...")

            s3_client = boto3.client(
                "s3",
                endpoint_url=config.endpoint_url,
                aws_access_key_id=config.aws_access_key_id,
                aws_secret_access_key=config.aws_secret_access_key,
                region_name=config.region_name
            )

            s3_client.download_fileobj(config.bucket_name, object_key, tmp_file)
            log.info(f"Downloaded to {tmp_file.name}")
            return tmp_file.name

    except ClientError as e:
        log.error(f"S3 ClientError downloading {object_key}: {e}")
        raise e
    except Exception as e:
        log.error(f"Unexpected error downloading {object_key}: {e}")
        raise e
