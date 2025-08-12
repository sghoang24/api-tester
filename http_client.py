"""HTTP Client."""

import json
import requests
from typing import Dict, Any, Optional, Union


class HTTPClient:
    """HTTP Client."""
    
    def __init__(
        self,
        base_url: str = "",
        headers: Optional[Dict[str, str]] = None, 
        cookies: Optional[Union[Dict[str, str], str]] = None,
        timeout: int = 30
    ):
        """
        Initialize the HTTP client
        
        Args:
            base_url: Base URL for all requests
            headers: Default headers to include in all requests
            cookies: Cookies to include in all requests (dict or cookie string)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        # Set default headers
        default_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if headers:
            default_headers.update(headers)
        
        self.session.headers.update(default_headers)
        
        # Set cookies if provided
        if cookies:
            if isinstance(cookies, dict):
                # If cookies is a dictionary, update session cookies
                self.session.cookies.update(cookies)
            elif isinstance(cookies, str):
                # If cookies is a string, set as Cookie header directly
                # This handles both simple format and complex cookie strings
                self.session.headers['Cookie'] = cookies

    def _build_url(self, endpoint: str) -> str:
        """Build full URL from base URL and endpoint."""
        endpoint = endpoint.lstrip('/')
        if self.base_url:
            return f"{self.base_url}/{endpoint}"
        return endpoint

    def request(
        self, method: str, endpoint: str, 
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        files: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = 60
    ) -> Dict[str, Any]:
        """
        Make HTTP request with specified method
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS)
            endpoint: API endpoint
            json_data: JSON data to send in request body
            data: Form data or raw data to send
            params: Query parameters (URL parameters)
            headers: Additional headers for this request
            files: Files to upload
            timeout: Request timeout (overrides default)
        
        Returns:
            Dictionary containing response data and metadata
        """
        method = method.upper()
        url = self._build_url(endpoint)
        request_timeout = timeout or self.timeout
        
        # Prepare request arguments
        kwargs = {
            'timeout': request_timeout
        }
        
        # Handle different types of data
        if json_data is not None:
            kwargs['json'] = json_data
        elif data is not None:
            kwargs['data'] = data
        
        if params:
            kwargs['params'] = params
        
        if headers:
            kwargs['headers'] = headers
        
        if files:
            kwargs['files'] = files
            # Remove Content-Type header when uploading files
            if 'headers' not in kwargs:
                kwargs['headers'] = {}
            kwargs['headers']['Content-Type'] = None
        
        print(f"Request URL: {url}")
        try:
            response = self.session.request(method, url, **kwargs)
            
            # Try to parse JSON response
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                # If not JSON, return text content
                response_data = {"text": response.text} if response.text else None
            
            result = {
                "method": method,
                "url": url,
                "status_code": response.status_code,
                "success": response.ok,
                "data": response_data,
                "headers": dict(response.headers),
                "elapsed": response.elapsed.total_seconds()
            }
            
            # Add error info if request failed
            if not response.ok:
                result["error"] = {
                    "message": response.reason,
                    "status_code": response.status_code,
                    "details": response.text if response.text else None
                }
            
            return result
            
        except requests.exceptions.Timeout:
            return self._error_response(method, url, "Request timeout", "TimeoutError")
        except requests.exceptions.ConnectionError:
            return self._error_response(method, url, "Connection error", "ConnectionError")
        except requests.exceptions.RequestException as e:
            return self._error_response(method, url, str(e), type(e).__name__)

    def _error_response(self, method: str, url: str, message: str, error_type: str) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            "method": method,
            "url": url,
            "status_code": 0,
            "success": False,
            "error": {
                "message": message,
                "type": error_type
            },
            "data": None,
            "headers": {},
            "elapsed": 0
        }

    def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """GET request convenience method"""
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """POST request convenience method"""
        return self.request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """PUT request convenience method"""
        return self.request("PUT", endpoint, **kwargs)

    def patch(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """PATCH request convenience method."""
        return self.request("PATCH", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """DELETE request convenience method."""
        return self.request("DELETE", endpoint, **kwargs)

    def head(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """HEAD request convenience method."""
        return self.request("HEAD", endpoint, **kwargs)

    def options(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """OPTIONS request convenience method."""
        return self.request("OPTIONS", endpoint, **kwargs)

    def set_auth(self, token: str, auth_type: str = "Bearer"):
        """Set authentication header."""
        self.session.headers['Authorization'] = f"{auth_type} {token}"

    def set_header(self, key: str, value: str):
        """Set a default header for all requests."""
        self.session.headers[key] = value

    def remove_header(self, key: str):
        """Remove a default header."""
        if key in self.session.headers:
            del self.session.headers[key]

    def set_cookies(self, cookies: Union[Dict[str, str], str]):
        """Set cookies for all requests."""
        if isinstance(cookies, dict):
            self.session.cookies.update(cookies)
        elif isinstance(cookies, str):
            # Set raw cookie string directly as Cookie header
            self.session.headers['Cookie'] = cookies

    def add_cookie(self, name: str, value: str):
        """Add a single cookie."""
        self.session.cookies[name] = value

    def remove_cookie(self, name: str):
        """Remove a cookie by name."""
        if name in self.session.cookies:
            del self.session.cookies[name]

    def set_base_url(self, base_url: str):
        """Update the base URL"""
        self.base_url = base_url.rstrip('/')

    def get_cookies(self) -> Union[Dict[str, str], str]:
        """Get current cookies as dictionary or raw cookie string"""
        if 'Cookie' in self.session.headers:
            return self.session.headers['Cookie']
        return dict(self.session.cookies)

    def pretty_print(self, response: Dict[str, Any]) -> None:
        """Print response in pretty JSON format"""
        response = {
            "status_code": response['status_code'],
            "success": response['success'],
            "data": response['data'], 
        }
        print(json.dumps(response, indent=2, ensure_ascii=False))

    def is_success(self, response: Dict[str, Any]) -> bool:
        """Check if response was successful"""
        return response.get("success", False)

    def get_data(self, response: Dict[str, Any]) -> Any:
        """Extract data from response"""
        return response.get("data")

    def get_error(self, response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract error information from response"""
        return response.get("error")
