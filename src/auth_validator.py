# --------------------------------------------------------------------------
# Copyright Commvault Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# --------------------------------------------------------------------------

"""
Authentication validator module - validates credentials at startup without circular imports.
"""

import sys
import keyring
from src.logger import logger


def validate_auth_credentials_at_startup():
    """
    Validate authentication credentials at startup to fail fast if they're missing.
    This function doesn't create any heavy objects, just checks if credentials exist.
    """
    try:
        logger.info("Validating authentication credentials...")
        
        service_name = "commvault-mcp-server"
        access_token = keyring.get_password(service_name, "access_token")
        refresh_token = keyring.get_password(service_name, "refresh_token")
        server_secret = keyring.get_password(service_name, "server_secret")
        
        # Check for missing tokens/secrets
        missing_items = []
        if not access_token:
            missing_items.append("access_token")
        if not refresh_token:
            missing_items.append("refresh_token")
        if not server_secret:
            missing_items.append("server_secret")
            
        if missing_items:
            logger.critical(f"Missing required credentials: {', '.join(missing_items)}. Please set the tokens from command line before running the server.")
            sys.exit(1)
            
        logger.info("Authentication credentials validated successfully")
        
    except Exception as e:
        logger.error(f"Failed to validate authentication credentials: {e}")
        sys.exit(1)