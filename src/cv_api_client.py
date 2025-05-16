import requests
import json
from typing import Dict, Any, Optional, Union
from urllib.parse import urljoin
import time
from dotenv import load_dotenv

from src.auth_service import AuthService
from src.logger import logger
from src.utils import get_env_var

load_dotenv()

class CommvaultApiClient:
    
    def __init__(self):
        self.base_url = get_env_var("CC_SERVER_URL") + "/commandcenter/api/"
        self.auth_service = AuthService()
            
    def _get_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        auth_token, _ = self.auth_service.get_tokens()
        headers = {
            'Accept': 'application/json',
            'Authtoken': auth_token
        }
        
        if additional_headers:
            headers.update(additional_headers)
            
        return headers
    
    def _build_url(self, endpoint: str) -> str:
        return urljoin(self.base_url, endpoint)

    def _refresh_access_token(self) -> bool:
        try:
            refresh_url = self._build_url("V4/AccessToken/Renew")
            auth_token, refresh_token = self.auth_service.get_tokens()
            
            payload = {
                "accessToken": auth_token,
                "refreshToken": refresh_token
            }
            
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                url=refresh_url,
                headers=headers,
                data=json.dumps(payload),
                verify=False  # Disable SSL verification for development purposes TODO: Remove in production
            )
            
            response.raise_for_status()
            
            new_access_token = response.json().get("accessToken")
            new_refresh_token = response.json().get("refreshToken")
            if not new_access_token or not new_refresh_token:
                raise Exception("No new tokens received")
            self.auth_service.set_tokens(new_access_token, new_refresh_token)

            logger.info("Access token refreshed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to refresh access token: {str(e)}")
            return False
    
    def request(self, 
                method: str, 
                endpoint: str, 
                params: Optional[Dict[str, Any]] = None, 
                data: Optional[Union[Dict[str, Any], str]] = None, 
                headers: Optional[Dict[str, str]] = None,
                max_retries: int = 2,
                retry_delay: float = 1.0) -> requests.Response:
        
        # Check if the secret key is passed in the header for sse and streamable-http modes
        if get_env_var('MCP_TRANSPORT_MODE')!="stdio" and not self.auth_service.is_client_token_valid():
            logger.error("Invalid or missing token in client request")
            raise Exception("Invalid or missing token in request.")
        
        url = self._build_url(endpoint)
        request_headers = self._get_headers(headers)

        logger.info(f"{method} request to: {url}")
        
        request_data = data
        if isinstance(data, dict):
            request_data = json.dumps(data)
            if 'Content-Type' not in request_headers:
                request_headers['Content-Type'] = 'application/json'

        retries = 0
        while retries <= max_retries:
            try:
                response = requests.request(
                    method=method.upper(),
                    url=url,
                    headers=request_headers,
                    params=params,
                    data=request_data,
                    verify=False  # Disable SSL verification for development purposes TODO: Remove in production
                )
                logger.info(f"Response status code: {response.status_code}")
                logger.debug(f"Response content: {response.json()}")
                
                # Handle 401 Unauthorized error (expired token)
                if response.status_code == 401:
                    logger.info("Received 401 Unauthorized response. Attempting to refresh token...")
                    success = self._refresh_access_token()
                    
                    if success:
                        # Update headers with new token and retry the request
                        request_headers = self._get_headers(headers)
                        logger.info(f"Retrying {method} request with new token")
                        continue
                
                # Catch other HTTP errors
                response.raise_for_status()

                return response.json()
                
            except requests.exceptions.HTTPError as e:
                # Let the 401 handling above take care of auth errors
                if e.response.status_code != 401:
                    retries += 1
                    if retries > max_retries:
                        raise

                    backoff_time = retry_delay * (2 ** (retries - 1))
                    logger.warning(f"Request failed with {e}. Retrying in {backoff_time} seconds...")
                    time.sleep(backoff_time)
                else:
                    # If we get here, it means we got a 401 and the token refresh failed
                    raise Exception("Failed to refresh token. please create a new token update the keyring")
                    
            except requests.exceptions.RequestException as e:
                retries += 1
                if retries > max_retries:
                    raise Exception("Some issue occured. Please try again later.")
                
                backoff_time = retry_delay * (2 ** (retries - 1))
                logger.warning(f"Request failed with {e}. Retrying in {backoff_time} seconds...")
                time.sleep(backoff_time)

            except Exception as e:
                logger.error(f"An unexpected error occurred: {str(e)}")
                raise
    
    # Convenience methods for common HTTP methods
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> requests.Response:
        """Make a GET request to the API."""
        return self.request("GET", endpoint, params=params, headers=headers)
    
    def post(self, endpoint: str, data: Optional[Union[Dict[str, Any], str]] = None, 
             params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> requests.Response:
        """Make a POST request to the API."""
        return self.request("POST", endpoint, params=params, data=data, headers=headers)
    
    def put(self, endpoint: str, data: Optional[Union[Dict[str, Any], str]] = None, 
            params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> requests.Response:
        """Make a PUT request to the API."""
        return self.request("PUT", endpoint, params=params, data=data, headers=headers)
    
    def delete(self, endpoint: str, params: Optional[Dict[str, Any]] = None, 
               data: Optional[Union[Dict[str, Any], str]] = None, headers: Optional[Dict[str, str]] = None) -> requests.Response:
        """Make a DELETE request to the API."""
        return self.request("DELETE", endpoint, params=params, data=data, headers=headers)
    
    def patch(self, endpoint: str, data: Optional[Union[Dict[str, Any], str]] = None, 
              params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> requests.Response:
        """Make a PATCH request to the API."""
        return self.request("PATCH", endpoint, params=params, data=data, headers=headers)
