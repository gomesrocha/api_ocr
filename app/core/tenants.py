import json
import os
from typing import Dict, Optional
from pydantic import BaseModel

class TenantConfig(BaseModel):
    bucket_name: str
    endpoint_url: Optional[str] = None
    aws_access_key_id: str
    aws_secret_access_key: str
    region_name: str

# Cache for tenant configuration
_TENANTS_CACHE: Dict[str, TenantConfig] = {}

def load_tenants(config_path: str = "tenants.json"):
    """
    Load tenant configurations from a JSON file.
    """
    global _TENANTS_CACHE
    if not os.path.exists(config_path):
        return

    try:
        with open(config_path, "r") as f:
            data = json.load(f)
            for client_id, config in data.items():
                _TENANTS_CACHE[client_id] = TenantConfig(**config)
    except Exception as e:
        # In a real app, logging here would be good
        print(f"Error loading tenants configuration: {e}")

def get_tenant_config(client_id: str) -> Optional[TenantConfig]:
    """
    Retrieve configuration for a specific tenant.
    Initializes cache if empty.
    """
    if not _TENANTS_CACHE:
        load_tenants()
    return _TENANTS_CACHE.get(client_id)
