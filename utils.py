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


def get_current_base_url(current_env: str) -> str:
    """Get the base URL for the current environment"""
    if current_env == "DAI":
        return DAI_BASE_URL
    elif current_env == "SIT":
        return SIT_BASE_URL
    else:  # UAT
        return UAT_BASE_URL


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
    """Load cookies configurations from JSON file with admin override option"""
    try:
        # Default cookies
        default_cookies = {
            "DAI": DAI_COOKIES,
            "SIT": SIT_COOKIES,
            "UAT": UAT_COOKIES
        }
        
        # Admin cookies (global)
        admin_cookies = {}
        if admin_file_path and os.path.exists(admin_file_path):
            admin_cookies = load_json_file(admin_file_path)
        
        # User cookies (personal)
        user_cookies = {}
        if os.path.exists(file_path):
            user_cookies = load_json_file(file_path)
        
        # Combine with priority: user > admin > default
        result = {}
        for env in ["DAI", "SIT", "UAT"]:
            if env in user_cookies:
                result[env] = user_cookies[env]
            elif env in admin_cookies:
                result[env] = admin_cookies[env]
            else:
                result[env] = default_cookies.get(env, "")
        
        return result
    except Exception:
        return {
            "DAI": DAI_COOKIES,
            "SIT": SIT_COOKIES,
            "UAT": UAT_COOKIES
        }


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
    
    print("URL:", url)
    
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
    for item in os.listdir(user_dir):
        if os.path.isdir(os.path.join(user_dir, item)) and item != "adminadmin":
            existing_users.append(item)

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
