"""Utils."""

import json
import os
import requests
import time
from typing import Dict, List, Any, Optional
from constants import DAI_BASE_URL, SIT_BASE_URL, UAT_BASE_URL, DAI_COOKIES, SIT_COOKIES, UAT_COOKIES


def get_base_url(env: str) -> str:
    """Get base URL."""
    env = env.upper()
    if env == 'DAI':
        return DAI_BASE_URL
    elif env == 'SIT':
        return SIT_BASE_URL
    elif env == 'UAT':
        return UAT_BASE_URL
    else:
        raise ValueError(f"Invalid environment '{env}'. Please use 'DAI', 'SIT', or 'UAT'.")


def get_current_base_url(current_env: str, module: str = "EX") -> str:
    """Get the base URL for the current environment and module"""
    environments = load_environments_config()
    if current_env in environments and environments[current_env].get('enabled', True):
        base_url = environments[current_env]['base_url']
        
        # Remove existing module suffixes if they exist
        if base_url.endswith("/api/assessment/api/v1"):
            base_url = base_url.replace("/api/assessment/api/v1", "")
        elif base_url.endswith("/api/administration/api/v1"):
            base_url = base_url.replace("/api/administration/api/v1", "")
        
        # Add module-specific suffix
        if module == "EX":
            base_url += "/api/assessment/api/v1"
        elif module == "AD":
            base_url += "/api/administration/api/v1"
        
        return base_url

    # Fallback to constants for backward compatibility with module support
    if current_env == "DAI":
        base_url = DAI_BASE_URL
    elif current_env == "SIT":
        base_url = SIT_BASE_URL
    else:  # UAT
        base_url = UAT_BASE_URL
    
    # Remove existing module suffixes and add new one
    if base_url.endswith("/api/assessment/api/v1"):
        base_url = base_url.replace("/api/assessment/api/v1", "")
    elif base_url.endswith("/api/administration/api/v1"):
        base_url = base_url.replace("/api/administration/api/v1", "")
    
    # Add module-specific suffix
    if module == "EX":
        base_url += "/api/assessment/api/v1"
    elif module == "AD":
        base_url += "/api/administration/api/v1"
    
    return base_url


def load_environments_config() -> Dict[str, Any]:
    """Load environments configuration, combining defaults with admin-added environments"""
    try:
        # Start with defaults
        result = {
            "SIT": {
                "name": "SIT",
                "base_url": SIT_BASE_URL,
                "default_cookies": SIT_COOKIES,
                "enabled": True
            },
            "DAI": {
                "name": "DAI", 
                "base_url": DAI_BASE_URL,
                "default_cookies": DAI_COOKIES,
                "enabled": True
            },
            "UAT": {
                "name": "UAT",
                "base_url": UAT_BASE_URL,
                "default_cookies": UAT_COOKIES,
                "enabled": True
            }
        }

        # Add admin environments if file exists
        env_file_path = os.path.join(os.path.dirname(__file__), "environments_config.json")
        if os.path.exists(env_file_path):
            admin_envs = load_json_file(env_file_path)
            result.update(admin_envs)
        
        return result
    except Exception:
        # Return defaults if anything fails
        return {
            "SIT": {
                "name": "SIT",
                "base_url": SIT_BASE_URL,
                "default_cookies": SIT_COOKIES,
                "enabled": True
            },
            "DAI": {
                "name": "DAI", 
                "base_url": DAI_BASE_URL,
                "default_cookies": DAI_COOKIES,
                "enabled": True
            },
            "UAT": {
                "name": "UAT",
                "base_url": UAT_BASE_URL,
                "default_cookies": UAT_COOKIES,
                "enabled": True
            }
        }


def save_environments_config(environments: Dict[str, Any]) -> bool:
    """Save environments configuration to JSON file"""
    try:
        env_file_path = os.path.join(os.path.dirname(__file__), "environments_config.json")
        return save_json_file(environments, env_file_path)
    except Exception:
        return False


def get_enabled_environments() -> List[str]:
    """Get list of enabled environment names"""
    environments = load_environments_config()
    return [env_name for env_name, config in environments.items() if config.get('enabled', True)]


def get_user_specific_paths(username: str) -> Dict[str, str]:
    """Get file paths specific to the current user"""
    # Shared by all users
    api_config_file = os.path.join(os.path.dirname(__file__), "api_configs.json")

    # User-specific files
    user_dir = os.path.join(os.path.dirname(__file__), "user_data")
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)

    user_dir = os.path.join(user_dir, username)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)

    api_history_file = os.path.join(user_dir, "api_history.json")
    user_cookies_file = os.path.join(user_dir, "cookies_config.json")
    user_apis_file = os.path.join(user_dir, "user_apis.json")

    return {
        "API_CONFIG_FILE": api_config_file,
        "API_HISTORY_FILE": api_history_file,
        "COOKIES_CONFIG_FILE": user_cookies_file,
        "USER_APIS_FILE": user_apis_file
    }


def cookies_dict_to_string(cookies_dict: Dict[str, Any]) -> str:
    """Convert cookies dictionary to string format"""
    if not cookies_dict or not isinstance(cookies_dict, dict):
        return ""

    cookie_pairs = []
    for key, value in cookies_dict.items():
        try:
            # Handle different value types
            if value is None:
                str_value = ""
            else:
                str_value = str(value)
            cookie_pairs.append(f"{key}={str_value}")
        except Exception:
            # Skip any problematic cookie entries
            pass

    return "; ".join(cookie_pairs)


def cookies_string_to_dict(cookies_string: str) -> Dict[str, str]:
    """Convert cookies string to dictionary format"""
    if not cookies_string:
        return {}

    cookies_dict = {}
    for cookie in cookies_string.split(";"):
        if "=" in cookie:
            key, value = cookie.split("=", 1)
            cookies_dict[key.strip()] = value.strip()

    return cookies_dict


def load_json_file(file_path: str) -> Any:
    """Load data from JSON file"""
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding='utf-8') as f:
                return json.load(f)
        return {} if file_path.endswith('.json') else []
    except Exception as e:
        raise Exception(f"Error loading file {file_path}: {str(e)}")


def save_json_file(data: Any, file_path: str) -> bool:
    """Save data to JSON file"""
    try:
        with open(file_path, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        raise Exception(f"Error saving file {file_path}: {str(e)}")


def load_user_apis(file_path: str) -> Dict[str, Any]:
    """Load user's saved API configurations"""
    try:
        return load_json_file(file_path)
    except Exception:
        return {}


def save_user_apis(apis: Dict[str, Any], file_path: str) -> bool:
    """Save user's API configurations"""
    try:
        return save_json_file(apis, file_path)
    except Exception:
        return False


def load_api_configs(file_path: str) -> Dict[str, Any]:
    """Load API configurations from JSON file"""
    try:
        return load_json_file(file_path)
    except Exception:
        return {}


def save_api_config(configs: Dict[str, Any], file_path: str) -> bool:
    """Save API configurations to JSON file"""
    try:
        return save_json_file(configs, file_path)
    except Exception:
        return False


def load_api_history(file_path: str) -> List[Dict[str, Any]]:
    """Load API call history from JSON file"""
    try:
        data = load_json_file(file_path)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_api_history(history: List[Dict[str, Any]], file_path: str) -> bool:
    """Save API call history to JSON file"""
    try:
        return save_json_file(history, file_path)
    except Exception:
        return False


def load_cookies_config(file_path: str, admin_file_path: Optional[str] = None) -> Dict[str, str]:
    """Load cookies configurations with simple priority: user cookies (if not empty) > admin cookies > defaults"""
    try:
        # Get all available environments
        environments = load_environments_config()
        
        # Load admin cookies
        admin_cookies = {}
        if admin_file_path and os.path.exists(admin_file_path):
            admin_cookies = load_json_file(admin_file_path)
        
        # Load user cookies (default to empty for all environments)
        user_cookies = {}
        if os.path.exists(file_path):
            user_cookies = load_json_file(file_path)
        
        # Initialize result with empty cookies for all environments
        result = {}
        for env_name, env_config in environments.items():
            if not env_config.get('enabled', True):
                continue  # Skip disabled environments
            
            # Default to empty string for user cookies
            result[env_name] = ""
        
        # Only set user cookies if they exist and are not empty
        for env_name in result.keys():
            if env_name in user_cookies and user_cookies[env_name].strip():
                result[env_name] = user_cookies[env_name]
        
        return result
    except Exception:
        # Simple fallback - all environments get empty cookies
        environments = load_environments_config()
        return {env_name: "" for env_name, config in environments.items() if config.get('enabled', True)}


def save_cookies_config(configs: Dict[str, str], file_path: str) -> bool:
    """Save cookies configurations to JSON file"""
    try:
        return save_json_file(configs, file_path)
    except Exception:
        return False


def make_http_request(api: Dict[str, Any]) -> requests.Response:
    """Make HTTP request based on API configuration"""
    method = api['method']
    url = api['url']
    headers = api.get('headers', {})
    params = api.get('params', {})
    cookies = api.get('cookies', {})
    
    if method == "GET":
        return requests.get(url, headers=headers, params=params, cookies=cookies)
    elif method == "POST":
        return requests.post(url, headers=headers, json=api.get('body', {}), params=params, cookies=cookies)
    elif method == "PUT":
        return requests.put(url, headers=headers, json=api.get('body', {}), params=params, cookies=cookies)
    elif method == "DELETE":
        return requests.delete(url, headers=headers, json=api.get('body', {}), params=params, cookies=cookies)
    elif method == "PATCH":
        return requests.patch(url, headers=headers, json=api.get('body', {}), params=params, cookies=cookies)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")


def get_response_content(response: requests.Response) -> Any:
    """Extract content from HTTP response"""
    try:
        return response.json()
    except:
        return response.text


def create_history_entry(api_name: str, api_config: Dict[str, Any], response: Dict[str, Any], current_env: str) -> Dict[str, Any]:
    """Create a history entry for an API call"""
    path = api_config.get('path', '')
    api_url_path = api_config.get('url_path', '')
    return {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "name": api_name,
        "environment": current_env,
        "path": path if len(path) > 0 else api_url_path,
        "method": api_config['method'],
        "status_code": response['status_code'],
        "time_ms": response['time'],
        "config": api_config,
    }


def get_existing_users() -> List[str]:
    """Get list of existing users (excluding adminadmin)"""
    user_dir = os.path.join(os.path.dirname(__file__), "user_data")
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)

    existing_users = []
    qa_users = []
    ba_users = []
    regular_users = []
    
    # Separate QA, BA users from regular users
    for item in os.listdir(user_dir):
        if os.path.isdir(os.path.join(user_dir, item)) and item != "adminadmin":
            if item.upper().startswith("QA"):
                qa_users.append(item)
            elif item.upper().startswith("BA"):
                ba_users.append(item)
            else:
                regular_users.append(item)
    
    # Sort each group alphabetically
    qa_users.sort()
    ba_users.sort()
    regular_users.sort()
    
    # Combine with QA users first, then BA users, then regular users
    existing_users = qa_users + ba_users + regular_users

    return existing_users


def validate_username(username: str, existing_users: List[str]) -> Optional[str]:
    """Validate username and return error message if invalid, None if valid"""
    if username == "adminadmin":
        return "Cannot create user with admin username. Use Admin Login instead."
    elif username in existing_users:
        return "Username already exists. Please choose another."
    elif not username.isalnum():
        return "Username must contain only letters and numbers."
    return None


def ensure_path_format(path: str) -> str:
    """Ensure API path starts with a slash"""
    if not path.startswith('/'):
        return '/' + path
    return path
