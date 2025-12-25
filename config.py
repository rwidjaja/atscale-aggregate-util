# config.py
import os
import json
import requests
import urllib3
from urllib.parse import urlparse
from typing import Dict, Tuple, Optional

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "./config.json")
_JWT_CACHE = None
_CONTAINER_JWT_CACHE = None


def load_config() -> Dict:
    """Load configuration from config.json"""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_credentials() -> Tuple[str, str]:
    """Return username and password from config.json"""
    config = load_config()
    return config["username"], config["password"]


def get_instance_type() -> str:
    """Return the instance_type from config.json"""
    config = load_config()
    return config.get("instance_type", "installer")


def normalize_host(host: str) -> str:
    """Normalize host URL to include protocol"""
    if not host:
        return host
    
    # Check if host already has a protocol
    if host.startswith(('http://', 'https://')):
        return host
    
    # Default to https if no protocol specified
    return f"https://{host}"


def get_jwt(force_refresh: bool = False) -> str:
    """
    Returns authentication token based on instance_type.
    - Installer: JWT via auth endpoint
    - Container: Static token from config (for public API)
    """
    global _JWT_CACHE
    config = load_config()

    if config.get("instance_type") == "installer":
        # Installer flow - generate JWT via auth endpoint
        if _JWT_CACHE and not force_refresh:
            return _JWT_CACHE

        host = normalize_host(config["host"])
        username = config["username"]
        password = config["password"]
        org = config["organization"]
        
        # Parse the host URL to extract netloc (hostname:port)
        parsed_url = urlparse(host)
        netloc = parsed_url.netloc
        
        # For installer, we need to use port 10500 for auth
        url = f"{parsed_url.scheme}://{netloc}:10500/{org}/auth"
        resp = requests.get(
            url, auth=(username, password), verify=False, timeout=15
        )
        resp.raise_for_status()
        _JWT_CACHE = resp.text.strip()

    elif config.get("instance_type") == "container":
        # Container: Return static token for public API
        token = config.get("token")
        if not token:
            raise ValueError("Container instance requires 'token' field in config.json for public API access")
        return token

    else:
        raise ValueError(f"Unknown instance_type: {config.get('instance_type')}")

    return _JWT_CACHE


def get_container_jwt(force_refresh: bool = False) -> Optional[str]:
    """
    Returns JWT token for container private API via OIDC.
    Requires client_id and client_secret in config.json.
    Returns None if credentials not available.
    """
    global _CONTAINER_JWT_CACHE
    
    config = load_config()
    if config.get("instance_type") != "container":
        raise ValueError("get_container_jwt() only works for container instances")
    
    if _CONTAINER_JWT_CACHE and not force_refresh:
        return _CONTAINER_JWT_CACHE
    
    # Check if we have OIDC credentials
    client_id = config.get("client_id")
    client_secret = config.get("client_secret")
    username = config.get("username")
    password = config.get("password")
    host = normalize_host(config["host"])
    
    if not all([client_id, client_secret, username, password]):
        # Not all credentials available, return None
        return None
    
    # Get JWT via OIDC token endpoint
    url = f"{host}/auth/realms/atscale/protocol/openid-connect/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "username": username,
        "password": password,
        "grant_type": "password",
    }
    
    try:
        resp = requests.post(url, data=data, verify=False, timeout=15)
        resp.raise_for_status()
        _CONTAINER_JWT_CACHE = resp.json().get("access_token")
        return _CONTAINER_JWT_CACHE
    except Exception as e:
        print(f"Warning: Failed to get container JWT: {e}")
        return None


def clear_jwt_cache() -> None:
    """Clear cached JWT tokens"""
    global _JWT_CACHE, _CONTAINER_JWT_CACHE
    _JWT_CACHE = None
    _CONTAINER_JWT_CACHE = None


def validate_config() -> Dict:
    """Validate configuration and return validated config"""
    config = load_config()
    instance_type = config.get("instance_type", "installer")
    
    if instance_type == "installer":
        required = ["host", "username", "password", "organization"]
        missing = [field for field in required if field not in config]
        if missing:
            raise ValueError(f"Installer config missing fields: {missing}")
    elif instance_type == "container":
        # Container requires at least host and token for public API
        required = ["host", "token"]
        missing = [field for field in required if field not in config]
        if missing:
            raise ValueError(f"Container config missing fields: {missing}")
    else:
        raise ValueError(f"Invalid instance_type: {instance_type}")
    
    return config