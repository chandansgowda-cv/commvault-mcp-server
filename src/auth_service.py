import keyring
import sys
from fastmcp.server.dependencies import get_http_request

from src.logger import logger


class AuthService:
    def __init__(self):
        self.__service_name = "commvault-mcp-server"
        self.__access_token = None
        self.__refresh_token = None

        self.fetch_and_set_tokens()

    def get_tokens(self):
        return self.__access_token, self.__refresh_token
    
    def fetch_and_set_tokens(self):
        access_token = keyring.get_password(self.__service_name, "access_token")
        refresh_token = keyring.get_password(self.__service_name, "refresh_token")
        if access_token is None or refresh_token is None:
            logger.critical("Please set the tokens from command line before running the server. Refer to the documentation for more details.")
            sys.exit(1)
        self.__access_token = access_token
        self.__refresh_token = refresh_token
        return access_token, refresh_token
    
    def set_access_token(self, access_token: str):
        keyring.set_password(self.__service_name, "access_token", access_token)
        self.__access_token = access_token
    
    def set_refresh_token(self, refresh_token: str):
        keyring.set_password(self.__service_name, "refresh_token", refresh_token)
        self.__refresh_token = refresh_token

    def set_tokens(self, access_token: str, refresh_token: str):
        self.set_access_token(access_token)
        self.set_refresh_token(refresh_token)
        
    def is_client_token_valid(self) -> bool:
        request = get_http_request()
        auth_header = request.headers.get("Authorization")
        if auth_header is None:
            logger.error("Authorization header is missing in request")
            return False
        mcp_client_token = auth_header.split(" ")[1] if auth_header.startswith("Bearer ") else auth_header
        secret = keyring.get_password(self.__service_name, "server_secret")
        if secret is None:
            logger.error("Server secret not found in keyring")
            return False

        return mcp_client_token == secret
        